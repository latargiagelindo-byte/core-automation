#!/usr/bin/env python3
"""MCP stdio: il bot puo solo leggere lo stato del ponte Lenovo e avviarlo."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8766"


def send(msg: dict) -> None:
    payload = json.dumps(msg, ensure_ascii=False, separators=(",", ":"))
    print(payload, flush=True)


def read_message() -> dict | None:
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(b"{"):
            return json.loads(stripped.decode("utf-8"))
        if stripped.lower().startswith(b"content-length:"):
            headers = {"content-length": stripped.split(b":", 1)[1].strip().decode("ascii")}
            while True:
                extra = sys.stdin.buffer.readline()
                if not extra or extra in (b"\r\n", b"\n"):
                    break
                if b":" in extra:
                    key, value = extra.decode("utf-8").split(":", 1)
                    headers[key.strip().lower()] = value.strip()
            length = int(headers.get("content-length", "0"))
            raw = sys.stdin.buffer.read(length)
            return json.loads(raw.decode("utf-8"))


def call(method: str, path: str, timeout: float) -> dict:
    data = None if method == "GET" else b""
    req = urllib.request.Request(BASE + path, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"bridge": "down", "errore": raw[:300] or str(exc)}
    except Exception as exc:
        return {"bridge": "down", "errore": str(exc)}


def ok_text(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}]}


def err_text(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}], "isError": True}


def tool_stato(_: dict) -> dict:
    payload = call("GET", "/stato", 5)
    if payload.get("errore") and payload.get("bridge") != "up":
        return err_text(
            "Il controllo del ponte non risponde. "
            "Il PC Lenovo e' spento oppure la sessione non e' aperta."
        )
    state = payload.get("bridge") or "down"
    if state == "up":
        return ok_text("Ponte Lenovo attivo.")
    return ok_text("Ponte Lenovo spento.")


def tool_avvia(_: dict) -> dict:
    payload = call("POST", "/avvia", 25)
    action = payload.get("azione")
    if action == "gia_attivo":
        return ok_text("Ponte Lenovo gia' attivo. Non l'ho riavviato.")
    if action == "avviato" or payload.get("bridge") == "up":
        return ok_text("Ponte Lenovo avviato.")
    if payload.get("errore"):
        return err_text(
            "Non riesco a raggiungere il controllo sul Lenovo. "
            "Il PC e' spento oppure la sessione non e' aperta."
        )
    return err_text("Avvio del ponte non riuscito.")


TOOLS = {
    "stato_bridge": {
        "description": "Dice se il ponte filesystem del Lenovo e' attivo. Non modifica nulla.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "handler": tool_stato,
    },
    "avvia_bridge": {
        "description": "Avvia il ponte filesystem del Lenovo se e' spento. Se e' gia' attivo non lo riavvia.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "handler": tool_avvia,
    },
}


def handle(msg: dict) -> None:
    mid = msg.get("id")
    method = msg.get("method")
    params = msg.get("params") or {}

    if method == "initialize":
        send(
            {
                "jsonrpc": "2.0",
                "id": mid,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "lenovo_ctl", "version": "1.0.0"},
                },
            }
        )
        return

    if method == "notifications/initialized":
        return

    if method == "tools/list":
        send(
            {
                "jsonrpc": "2.0",
                "id": mid,
                "result": {
                    "tools": [
                        {
                            "name": name,
                            "description": meta["description"],
                            "inputSchema": meta["inputSchema"],
                        }
                        for name, meta in TOOLS.items()
                    ]
                },
            }
        )
        return

    if method == "tools/call":
        name = params.get("name")
        meta = TOOLS.get(name)
        if not meta:
            send({"jsonrpc": "2.0", "id": mid, "result": err_text(f"Tool sconosciuto: {name}")})
            return
        send({"jsonrpc": "2.0", "id": mid, "result": meta["handler"](params.get("arguments") or {})})
        return

    if method == "ping":
        send({"jsonrpc": "2.0", "id": mid, "result": {}})
        return

    if mid is not None:
        send(
            {
                "jsonrpc": "2.0",
                "id": mid,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
        )


def main() -> None:
    while True:
        msg = read_message()
        if msg is None:
            break
        handle(msg)


if __name__ == "__main__":
    main()
