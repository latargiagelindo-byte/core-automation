"""Monitor aggiornamenti in sola lettura per /opt/core-automation.

Non scarica codice e non installa pacchetti. Segna solo se, in una lista fissa,
esiste una versione più nuova. L'installazione resta una decisione manuale.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path("/opt/core-automation")
DATA = ROOT / "data"
REPORT = DATA / "update_report.json"
SEEN = DATA / "seen_versions.json"
STAMP = DATA / "last_check.txt"
INTERVAL = timedelta(days=7)
TIMEOUT_S = 15

# Lista chiusa. Un nome nuovo entra solo se lo aggiungiamo qui, a mano.
WATCH = (
    {
        "id": "pypdf",
        "kind": "pypi",
        "name": "pypdf",
        "why": "lettura e scrittura di PDF",
    },
    {
        "id": "server-filesystem",
        "kind": "npm",
        "name": "@modelcontextprotocol/server-filesystem",
        "why": "strumento MCP per il filesystem",
    },
    {
        "id": "mcp-servers",
        "kind": "github",
        "name": "modelcontextprotocol/servers",
        "why": "repository degli strumenti MCP ufficiali",
    },
)


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def due(force: bool) -> bool:
    if force or not STAMP.exists():
        return True
    try:
        last = datetime.fromisoformat(STAMP.read_text(encoding="utf-8").strip())
    except ValueError:
        return True
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - last >= INTERVAL


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json, application/json",
            "User-Agent": "core-automation-update-monitor",
        },
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("risposta non oggetto")
    return payload


def remote_version(item: dict) -> tuple[str, str]:
    kind = item["kind"]
    name = item["name"]
    if kind == "pypi":
        data = fetch_json(f"https://pypi.org/pypi/{name}/json")
        return str(data["info"]["version"]), f"https://pypi.org/project/{name}/"
    if kind == "npm":
        data = fetch_json(f"https://registry.npmjs.org/{name}/latest")
        return str(data["version"]), f"https://www.npmjs.com/package/{name}"
    if kind == "github":
        url = f"https://api.github.com/repos/{name}/releases/latest"
        try:
            data = fetch_json(url)
            tag = str(data.get("tag_name") or "")
            if tag:
                return tag, str(data.get("html_url") or f"https://github.com/{name}")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
        data = fetch_json(f"https://api.github.com/repos/{name}/commits/HEAD")
        sha = str(data.get("sha") or "")
        return sha[:12], f"https://github.com/{name}/commit/{sha}"
    raise ValueError(f"tipo sconosciuto: {kind}")


def classify(seen: str | None, available: str | None, error: str | None) -> str:
    if error:
        return "errore"
    if not available:
        return "errore"
    if not seen:
        return "novita"
    if seen != available:
        return "aggiornamento"
    return "invariato"


def check(force: bool) -> dict:
    DATA.mkdir(parents=True, exist_ok=True)
    if not due(force):
        report = {
            "generated_at": now_iso(),
            "mode": "sola_lettura",
            "installs": False,
            "status": "saltato",
            "reason": "ultimo controllo più recente di 7 giorni; usa --force per ripetere",
            "items": [],
        }
        save_json(REPORT, report)
        return report

    seen_map = load_json(SEEN)
    approvals = load_json(DATA / "approvals.json")
    items = []
    for entry in WATCH:
        error = None
        available = None
        page = ""
        try:
            available, page = remote_version(entry)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        seen = seen_map.get(entry["id"])
        if isinstance(seen, dict):
            seen = seen.get("version")
        seen_text = str(seen) if seen else None
        status = classify(seen_text, available, error)
        items.append(
            {
                "id": entry["id"],
                "name": entry["name"],
                "kind": entry["kind"],
                "why": entry["why"],
                "seen": seen_text,
                "available": available,
                "page": page,
                "status": status,
                "approval": approvals.get(entry["id"], "in_attesa"),
                "error": error,
                "action": "nessuna installazione: serve una conferma manuale fuori da questo script",
            }
        )
        if available and not error:
            seen_map[entry["id"]] = {"version": available, "checked_at": now_iso()}

    report = {
        "generated_at": now_iso(),
        "mode": "sola_lettura",
        "installs": False,
        "status": "completo",
        "items": items,
    }
    save_json(REPORT, report)
    save_json(SEEN, seen_map)
    STAMP.write_text(now_iso() + "\n", encoding="utf-8")
    return report


def approve(item_id: str) -> dict:
    known = {entry["id"] for entry in WATCH}
    if item_id not in known:
        raise SystemExit(f"Voce sconosciuta: {item_id}")
    approvals = load_json(DATA / "approvals.json")
    approvals[item_id] = "approvato"
    save_json(DATA / "approvals.json", approvals)
    report = load_json(REPORT)
    for item in report.get("items") or []:
        if item.get("id") == item_id:
            item["approval"] = "approvato"
    if report:
        save_json(REPORT, report)
    print("Segnato come approvato. Nessun pacchetto è stato installato.")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Controllo aggiornamenti in sola lettura")
    parser.add_argument("--force", action="store_true", help="ignora l'attesa di 7 giorni")
    parser.add_argument("--approve", metavar="ID", help="segna una voce come approvata, senza installare")
    args = parser.parse_args()
    if args.approve:
        approve(args.approve)
        return 0
    report = check(force=args.force)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("Nessun pacchetto è stato installato.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
