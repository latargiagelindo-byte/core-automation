#!/usr/bin/env python3
"""Night-gentle Actual proposal heartbeat + optional batch note.
Proposal-only. Default: zero OmniRoute LLM calls. Hard stop 07:30 Europe/Rome.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path("/opt/core-automation")
CLUSTERS = ROOT / "data" / "actual-imports" / "payee_clusters.json"
OUT = ROOT / "memory-bank" / "proposta_categorie_actual.md"
LOG = ROOT / "data" / "actual-night-batch.log"
ROME = ZoneInfo("Europe/Rome")
DEADLINE_H, DEADLINE_M = 7, 30


def log(msg: str) -> None:
    line = f"{datetime.now(ROME).isoformat()} {msg}"
    print(line)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def in_night_window() -> bool:
    # Allow only 00:00-07:29 Europe/Rome
    now = datetime.now(ROME)
    return (now.hour, now.minute) < (DEADLINE_H, DEADLINE_M)


def omniroute_gate() -> tuple[bool, str]:
    try:
        out = subprocess.check_output(
            [
                "bash",
                "-lc",
                "export NVM_DIR=$HOME/.nvm; [ -s $NVM_DIR/nvm.sh ] && . $NVM_DIR/nvm.sh; pm2 jlist",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        data = json.loads(out)
        for p in data:
            if p.get("name") != "omniroute":
                continue
            st = p.get("pm2_env", {}).get("status")
            mem = int((p.get("monit") or {}).get("memory") or 0)
            mem_mb = mem // 1024 // 1024
            if st != "online":
                return False, f"status={st} memMB={mem_mb}"
            if mem_mb > 1200:
                return False, f"mem high memMB={mem_mb}"
            err = Path("/root/.pm2/logs/omniroute-error.log")
            if err.exists():
                tail = err.read_text(encoding="utf-8", errors="ignore")[-8000:]
                if "429" in tail or "rate limit" in tail.lower():
                    return False, f"429/rate-limit in error log memMB={mem_mb}"
            return True, f"online memMB={mem_mb}"
        return False, "not in pm2 list"
    except Exception as e:
        return False, f"check-error {e}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, required=True)
    ap.add_argument("--llm", action="store_true", help="reserved; night-gentle never calls LLM")
    args = ap.parse_args()

    if not in_night_window():
        log(f"SKIP batch={args.batch}: outside night window 00:00-07:30 (OmniRoute reserved for morning)")
        return 0

    ok, reason = omniroute_gate()
    log(f"omniroute_gate ok={ok} ({reason}) batch={args.batch} llm_flag={args.llm}")

    day = datetime.now(ROME).strftime("%Y-%m-%d")
    marker = f"### Heartbeat {day} lotto {args.batch}"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if not OUT.exists():
        OUT.write_text(
            "# Proposta categorie Actual — Spese di casa\n\n_File creato dal job notturno; rieseguire cluster se vuoto._\n\n",
            encoding="utf-8",
        )
    text = OUT.read_text(encoding="utf-8")
    if marker in text:
        log(f"SKIP heartbeat already present: {marker}")
        return 0

    # Optional slice note from clusters (local only)
    note = ""
    if CLUSTERS.exists():
        data = json.loads(CLUSTERS.read_text(encoding="utf-8"))
        bs = int(data.get("batch_size_unique") or 20)
        chunk = data["groups"][args.batch * bs : args.batch * bs + bs]
        note = f" gruppi_unici_in_lotto={len(chunk)}"

    block = (
        f"\n{marker}\n"
        f"- ora: {datetime.now(ROME).isoformat()}\n"
        f"- OmniRoute gate: {'OK' if ok else 'ALERT'} ({reason})\n"
        f"- mode: sola-proposta / zero-LLM-notturno{note}\n"
        f"- Actual DB: non modificato\n"
    )
    with OUT.open("a", encoding="utf-8") as f:
        f.write(block)
    log(f"OK wrote heartbeat batch={args.batch}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
