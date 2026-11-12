#!/usr/bin/env python3
"""Chat web Core Automation → Cline Hub. Solo 127.0.0.1, dietro Nginx."""
from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs
import urllib.error
import urllib.request

ROOT = Path("/opt/core-automation")
STATIC = ROOT / "chat" / "static"
SECRETS = ROOT / ".secrets"
DATA = ROOT / "data" / "chat"
UPLOADS = ROOT / "data" / "uploads"
HOST = os.environ.get("COREAUTO_CHAT_HOST", "127.0.0.1")
PORT = int(os.environ.get("COREAUTO_CHAT_PORT", "8081"))

CLINE_BIN = os.environ.get("CLINE_BIN", "/opt/node-v22/bin/cline")
HUB_PROVIDER = os.environ.get("COREAUTO_HUB_PROVIDER", "openai-compatible")
HUB_MODEL = os.environ.get("COREAUTO_HUB_MODEL", "gratis")
HUB_TIMEOUT = int(os.environ.get("COREAUTO_HUB_TIMEOUT", "180"))
CLINE_SOFT_TIMEOUT = max(30, HUB_TIMEOUT - 15)
MAX_UPLOAD_BYTES = int(os.environ.get("COREAUTO_MAX_UPLOAD_BYTES", str(12 * 1024 * 1024)))
ALLOWED_EXT = {
    ".pdf", ".png", ".jpg", ".jpeg", ".webp", ".gif",
    ".txt", ".md", ".csv", ".json", ".jsonl",
    ".doc", ".docx", ".xls", ".xlsx", ".odt", ".rtf",
}


OMNI_URL = os.environ.get("COREAUTO_OMNI_URL", "http://127.0.0.1:20128/v1/chat/completions")
OMNI_MODEL = os.environ.get("COREAUTO_OMNI_MODEL", "gratis")
FAST_CHAT = os.environ.get("COREAUTO_CHAT_FAST", "1") != "0"

# Richieste che meritano Hub+MCP. Il resto (saluti, chiacchiere) va su OmniRoute diretto.
TASK_RE = re.compile(
    r"\b("
    r"cerca|ricerca|tavily|web|notizie|"
    r"leggi|scrivi|modifica|crea|elimina|apri|mostra il file|riassumi|"
    r"deploy|restart|nginx|systemd|ssh|server|"
    r"budget|actual|spese|movimento|"
    r"email|gmail|calendario|drive|foto|rclone|gphotos|"
    r"aws|lambda|s3|backup|"
    r"memory-bank|memoria|mcp|script|comando|cron|hub"
    r")\b",
    re.I,
)


def use_hub_tools(message: str, attachments: list[str]) -> bool:
    if attachments:
        return True
    if not FAST_CHAT:
        return True
    msg = (message or "").strip()
    if not msg:
        return False
    # Domande sugli allegati senza file allegati: risposta diretta, niente caccia MCP.
    if re.search(r"allegat", msg, re.I) and not attachments:
        return False
    return bool(TASK_RE.search(msg))


def run_fast_omniroute(message: str, history: list) -> dict:
    """Risposta Wingman diretta via OmniRoute (senza sessione Hub/MCP)."""
    key = read_secret("omniroute_api_key")
    messages = [
        {
            "role": "system",
            "content": (
                "Sei Wingman, assistente personale di Gelindo. "
                "Rispondi in italiano, in prima persona, breve e amichevole. "
                "In questo turno NON ci sono allegati da leggere: non inventarli e non dire "
                "'nessun allegato trovato' a meno che Gelindo non chieda esplicitamente degli allegati. "
                "Se chiede degli allegati e non ne ha caricati, dì chiaramente che in questo messaggio "
                "non ha allegato file. Niente meta-commenti, niente dump di segreti."
            ),
        }
    ]
    if isinstance(history, list):
        for item in history[-6:]:
            if not isinstance(item, dict):
                continue
            role = item.get("role")
            content = item.get("content")
            if role in ("user", "assistant") and isinstance(content, str) and content.strip():
                messages.append({"role": role, "content": content.strip()[:1500]})
    messages.append({"role": "user", "content": (message or "").strip()[:4000]})
    payload = {
        "model": OMNI_MODEL,
        "messages": messages,
        "max_tokens": 400,
        "temperature": 0.4,
    }
    req = urllib.request.Request(
        OMNI_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            data = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        return {
            "content": f"Non riesco a risponderti al volo via OmniRoute ({exc}). Riprova.",
            "session_id": None,
            "status": "failed",
            "bridge_id": None,
            "rc": 1,
            "via": "omniroute-fast",
        }
    content = ""
    choices = data.get("choices") or []
    if choices:
        msg = (choices[0] or {}).get("message") or {}
        content = (msg.get("content") or "").strip()
        if not content:
            # gpt-oss a volte mette testo in reasoning
            content = (msg.get("reasoning") or msg.get("reasoning_content") or "").strip()
            if content and len(content) > 280:
                content = content[:280].rstrip() + "…"
    if not content:
        content = "Sono qui. Ripeti pure il messaggio in una riga."
    low = content.lower()
    if "[system]" in low or "this run is not complete" in low or "submit_and_exit" in low:
        content = "Sono qui con te. Dimmi pure."
    return {
        "content": content,
        "session_id": None,
        "status": "completed",
        "bridge_id": None,
        "rc": 0,
        "via": "omniroute-fast",
    }




def read_secret(name: str) -> str:
    return (SECRETS / name).read_text(encoding="utf-8").strip()


def room_ok(secret: str) -> bool:
    return bool(secret) and secret == read_secret("room-secret")


def safe_filename(name: str) -> str:
    base = Path(name or "file").name
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", base).strip("._") or "file"
    return base[:120]


def save_upload(filename: str, raw: bytes) -> Path:
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ValueError(f"Allegato troppo grande (max {MAX_UPLOAD_BYTES} byte)")
    ext = Path(filename).suffix.lower()
    if ext and ext not in ALLOWED_EXT:
        raise ValueError(f"Tipo file non consentito: {ext}")
    UPLOADS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = UPLOADS / f"{stamp}_{uuid.uuid4().hex[:8]}_{safe_filename(filename)}"
    dest.write_bytes(raw)
    dest.chmod(0o644)
    return dest


def build_prompt(message: str, history: list, attachments: list[str]) -> tuple[str, str]:
    bridge_id = uuid.uuid4().hex
    hist_lines = []
    if isinstance(history, list):
        for item in history[-8:]:
            if not isinstance(item, dict):
                continue
            role = item.get("role")
            content = item.get("content")
            if role in ("user", "assistant") and isinstance(content, str) and content.strip():
                hist_lines.append(f"{role}: {content.strip()[:1500]}")
    hist_block = "\n".join(hist_lines) if hist_lines else "(nessuna)"
    if attachments:
        att_section = (
            "Allegati di QUESTO messaggio (leggili subito con filesystem MCP):\n"
            + "\n".join(f"- {p}" for p in attachments)
        )
    else:
        att_section = (
            "Allegati di QUESTO messaggio: nessuno.\n"
            "VIETATO cercare cartelle/file 'allegati' sul server. "
            "Se Gelindo chiede degli allegati, rispondi che in questo messaggio non ne ha caricati."
        )
    prompt = f"""Sei Wingman, assistente personale di Gelindo. Cline Hub è solo il motore: presentati e agisci come Wingman.
Segui .clinerules e memory-bank/. Lavora in /opt/core-automation.
[bridge_id={bridge_id}]

Contesto cronologia recente:
{hist_block}

{att_section}

Messaggio di Gelindo:
{message.strip()[:4000]}

Istruzioni:
1) Usa tool MCP (memory, filesystem, tavily-search) SOLO se servono davvero al compito.
2) Per saluti o domande semplici: ZERO tool. Rispondi e chiudi subito.
3) OBBLIGATORIO: chiama submit_and_exit (verified=true) con summary = risposta finale a Gelindo.
   - summary in prima persona ("Io"), naturale, amichevole, sintetica;
   - zero meta-commenti; niente "[SYSTEM]"; niente spiegazioni sul tool;
   - niente dump di segreti.
4) Non rispondere solo "OK" nel testo assistente: metti la risposta in summary e chiudi.
"""
    return bridge_id, prompt


def _assistant_texts(messages: list) -> list[str]:
    out: list[str] = []
    for msg in messages or []:
        if msg.get("role") != "assistant":
            continue
        for part in msg.get("content") or []:
            if isinstance(part, dict) and part.get("type") == "text" and isinstance(part.get("text"), str):
                t = part["text"].strip()
                if t:
                    out.append(t)
    return out


def _is_noise_assistant_text(text: str) -> bool:
    low = text.lower()
    if "[system]" in low:
        return True
    if "submit_and_exit" in low and "terminal completion" in low:
        return True
    if "this run is not complete" in low:
        return True
    return False


def session_has_submit(session_id: str) -> bool:
    msg_path = ROOT / ".cline-data" / "sessions" / session_id / f"{session_id}.messages.json"
    if not msg_path.exists():
        return False
    try:
        data = json.loads(msg_path.read_text(encoding="utf-8"))
    except Exception:
        return False
    for msg in data.get("messages") or []:
        for part in msg.get("content") or []:
            if isinstance(part, dict) and part.get("type") == "tool_use" and part.get("name") == "submit_and_exit":
                return True
    return False


def extract_reply_from_session(session_id: str) -> str:
    msg_path = ROOT / ".cline-data" / "sessions" / session_id / f"{session_id}.messages.json"
    if not msg_path.exists():
        return ""
    data = json.loads(msg_path.read_text(encoding="utf-8"))
    # Prefer submit_and_exit summary
    for msg in reversed(data.get("messages") or []):
        for part in msg.get("content") or []:
            if isinstance(part, dict) and part.get("type") == "tool_use" and part.get("name") == "submit_and_exit":
                inp = part.get("input") or {}
                summary = inp.get("summary")
                if isinstance(summary, str) and summary.strip():
                    return summary.strip()
    # Fallback: first useful assistant text (before Cline nag loop)
    for t in _assistant_texts(data.get("messages") or []):
        if _is_noise_assistant_text(t):
            continue
        return t
    return ""


def find_session_by_bridge(bridge_id: str, started_after: float) -> tuple[str, str] | None:
    db = ROOT / ".cline-data" / "db" / "sessions.db"
    if not db.exists():
        return None
    con = sqlite3.connect(str(db))
    try:
        rows = con.execute(
            "select session_id, status, prompt, started_at from sessions order by started_at desc limit 12"
        ).fetchall()
    finally:
        con.close()
    needle = f"bridge_id={bridge_id}"
    for sid, status, prompt, started_at in rows:
        if prompt and needle in prompt:
            return sid, status or ""
    return None


def run_hub_session(prompt: str, bridge_id: str) -> dict:
    env = os.environ.copy()
    env["HOME"] = str(ROOT)
    env["PATH"] = "/opt/node-v22/bin:/usr/local/bin:/usr/bin:/bin"
    env["CLINE_HUB_DISCOVERY_PATH"] = str(ROOT / ".cline-data" / "hub-discovery.json")
    started = time.time()
    cmd = [
        CLINE_BIN,
        "-y",
        "--json",
        "--cwd",
        str(ROOT),
        "--config",
        str(ROOT / ".cline"),
        "--data-dir",
        str(ROOT / ".cline-data"),
        "-P",
        HUB_PROVIDER,
        "-m",
        HUB_MODEL,
        "--timeout",
        str(CLINE_SOFT_TIMEOUT),
        "--retries",
        "0",
        prompt,
    ]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        cwd=str(ROOT),
    )
    session_id = None
    status = ""
    reply = ""
    first_text_at = None
    hard_deadline = started + HUB_TIMEOUT + 40
    early_grace = 3  # seconds after first usable text without submit_and_exit
    stdout = ""
    stderr = ""
    rc = None
    try:
        while time.time() < hard_deadline:
            found = find_session_by_bridge(bridge_id, started)
            if found:
                session_id, status = found
            if session_id:
                if session_has_submit(session_id):
                    reply = extract_reply_from_session(session_id)
                    break
                cand = extract_reply_from_session(session_id)
                if cand:
                    reply = cand
                    if first_text_at is None:
                        first_text_at = time.time()
                    elif time.time() - first_text_at >= early_grace:
                        # Model answered but ignored submit_and_exit: stop nag loop.
                        break
                if status in ("completed", "failed"):
                    reply = extract_reply_from_session(session_id) or reply
                    break
            if proc.poll() is not None:
                break
            time.sleep(0.5)
        else:
            rc = 124
    finally:
        if proc.poll() is None:
            try:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=3)
            except Exception:
                pass
        try:
            out, err = proc.communicate(timeout=2)
        except Exception:
            out, err = "", ""
        stdout = out or ""
        stderr = err or ""
        if rc is None:
            rc = proc.returncode if proc.returncode is not None else 0

    # Final flush
    for _ in range(10):
        found = find_session_by_bridge(bridge_id, started)
        if found:
            session_id, status = found
            break
        time.sleep(0.2)
    if session_id and not reply:
        reply = extract_reply_from_session(session_id)
    if not reply:
        for line in (stdout or "").splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            ev = obj.get("event") if isinstance(obj, dict) else None
            if isinstance(ev, dict) and ev.get("toolName") == "submit_and_exit":
                inp = ev.get("input") or {}
                if isinstance(inp, dict) and inp.get("summary"):
                    reply = str(inp["summary"]).strip()
    if not reply:
        reply = (
            "La sessione Hub non ha restituito una risposta leggibile. "
            f"stato={status or 'sconosciuto'} rc={rc}."
        )
        if stderr.strip():
            reply += f" Dettaglio: {stderr.strip()[:240]}"
    # Never leak Cline SYSTEM nag text to the web UI.
    if _is_noise_assistant_text(reply):
        reply = "Ho completato il pensiero interno, ma non sono riuscito a chiudere pulito la sessione. Riprova pure con lo stesso messaggio."
    return {
        "content": reply,
        "session_id": session_id,
        "status": status or ("completed" if rc == 0 else "failed"),
        "bridge_id": bridge_id,
        "rc": rc,
        "via": "cline-hub",
    }


def parse_json_body(raw: bytes) -> dict:
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def parse_multipart(content_type: str, raw: bytes) -> tuple[dict[str, str], list[tuple[str, bytes]]]:
    """Return (fields, files) where files are (filename, content)."""
    if "boundary=" not in content_type:
        raise ValueError("multipart senza boundary")
    boundary = content_type.split("boundary=", 1)[1].strip()
    if boundary.startswith('"') and boundary.endswith('"'):
        boundary = boundary[1:-1]
    delim = b"--" + boundary.encode("utf-8")
    fields: dict[str, str] = {}
    files: list[tuple[str, bytes]] = []
    parts = raw.split(delim)
    for part in parts:
        if not part or part in (b"--\r\n", b"--", b"--\n"):
            continue
        if part.startswith(b"--"):
            continue
        if part.startswith(b"\r\n"):
            part = part[2:]
        if part.endswith(b"\r\n"):
            part = part[:-2]
        if b"\r\n\r\n" not in part:
            continue
        header_blob, body = part.split(b"\r\n\r\n", 1)
        if body.endswith(b"\r\n"):
            body = body[:-2]
        headers = header_blob.decode("utf-8", errors="ignore").split("\r\n")
        disposition = ""
        for h in headers:
            if h.lower().startswith("content-disposition:"):
                disposition = h
        if "name=" not in disposition:
            continue
        name_m = re.search(r'name="([^"]+)"', disposition)
        file_m = re.search(r'filename="([^"]*)"', disposition)
        if not name_m:
            continue
        name = name_m.group(1)
        if file_m is not None:
            filename = file_m.group(1) or "file"
            files.append((filename, body))
        else:
            fields[name] = body.decode("utf-8", errors="replace")
    return fields, files


class Handler(BaseHTTPRequestHandler):
    server_version = "CoreAutoChat/2.0"

    def log_message(self, fmt: str, *args) -> None:
        import sys

        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _query(self) -> str:
        return self.path.split("?", 1)[1] if "?" in self.path else ""

    def _path_only(self) -> str:
        return self.path.split("?", 1)[0]

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, code: int, obj: dict) -> None:
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self._send(code, raw, "application/json; charset=utf-8")

    def do_GET(self) -> None:
        path = self._path_only()
        if path in ("/cline-chat-verde.png", "/icon.png"):
            img = (STATIC / "cline-chat-verde.png").read_bytes()
            self._send(200, img, "image/png")
            return
        if path in ("/", "/index.html", "/chat", "/chat/"):
            html = (STATIC / "index.html").read_bytes()
            self._send(200, html, "text/html; charset=utf-8")
            return
        if path == "/health":
            self._send_json(200, {"ok": True, "via": "cline-hub", "uploads": str(UPLOADS)})
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:
        path = self._path_only()
        if path not in ("/api/chat", "/api/upload"):
            self._send(404, b"not found", "text/plain; charset=utf-8")
            return
        length = int(self.headers.get("Content-Length") or "0")
        if length > MAX_UPLOAD_BYTES + 2_000_000:
            self._send_json(413, {"error": "payload troppo grande"})
            return
        raw = self.rfile.read(length) if length else b""
        content_type = self.headers.get("Content-Type") or ""

        try:
            if content_type.startswith("multipart/form-data"):
                fields, files = parse_multipart(content_type, raw)
                secret = fields.get("roomSecret") or self.headers.get("X-Room-Secret") or ""
                message = (fields.get("message") or "").strip()
                history_raw = fields.get("history") or "[]"
                try:
                    history = json.loads(history_raw)
                except json.JSONDecodeError:
                    history = []
                attachments: list[str] = []
                for filename, blob in files:
                    if not blob:
                        continue
                    saved = save_upload(filename, blob)
                    attachments.append(str(saved))
            else:
                data = parse_json_body(raw)
                secret = str(data.get("roomSecret") or self.headers.get("X-Room-Secret") or "")
                message = str(data.get("message") or "").strip()
                history = data.get("history") or []
                attachments = []
                for item in data.get("attachments") or []:
                    if isinstance(item, str) and item.startswith(str(UPLOADS)):
                        attachments.append(item)
                # optional inline base64 attachments: [{name, content_base64}]
                import base64

                for item in data.get("files") or []:
                    if not isinstance(item, dict):
                        continue
                    name = str(item.get("name") or "file")
                    b64 = item.get("content_base64")
                    if not isinstance(b64, str) or not b64:
                        continue
                    saved = save_upload(name, base64.b64decode(b64))
                    attachments.append(str(saved))
        except Exception as exc:  # noqa: BLE001
            self._send_json(400, {"error": str(exc)[:300]})
            return

        if not room_ok(secret):
            self._send_json(403, {"error": "stanza"})
            return

        if path == "/api/upload":
            if not attachments:
                self._send_json(400, {"error": "nessun file"})
                return
            self._send_json(200, {"ok": True, "paths": attachments})
            return

        if not message and not attachments:
            self._send_json(400, {"error": "vuoto"})
            return
        if not message and attachments:
            message = "Ho allegato uno o più file. Leggili e dimmi cosa contengono in sintesi."

        hist = history if isinstance(history, list) else []
        try:
            if use_hub_tools(message, attachments):
                bridge_id, prompt = build_prompt(message, hist, attachments)
                result = run_hub_session(prompt, bridge_id)
                via = result.get("via") or "cline-hub"
            else:
                bridge_id = uuid.uuid4().hex
                result = run_fast_omniroute(message, hist)
                result["bridge_id"] = bridge_id
                via = result.get("via") or "omniroute-fast"
        except Exception as exc:  # noqa: BLE001
            self._send_json(502, {"error": str(exc)[:300]})
            return

        DATA.mkdir(parents=True, exist_ok=True)
        out = {
            "role": "assistant",
            "content": result["content"],
            "session_id": result.get("session_id"),
            "status": result.get("status"),
            "bridge_id": bridge_id,
            "attachments": attachments,
            "via": via,
        }
        (DATA / "last.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        self._send_json(200, out)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    UPLOADS.mkdir(parents=True, exist_ok=True)
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"chat on http://{HOST}:{PORT} via cline-hub timeout={HUB_TIMEOUT}s", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
