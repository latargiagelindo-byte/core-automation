#!/bin/bash
# hub start si stacca: questo script resta in attesa finché l'hub vive.
set -uo pipefail
export HOME=/opt/core-automation
export PATH=/opt/node-v22/bin:/usr/local/bin:/usr/bin:/bin
export CLINE_HUB_DISCOVERY_PATH=/opt/core-automation/.cline-data/hub-discovery.json
cd /opt/core-automation

CLINE=/opt/node-v22/bin/cline
DISCOVERY=/opt/core-automation/.cline-data/hub-discovery.json

hub_pid() {
  /usr/bin/python3 - "$DISCOVERY" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
try:
    data = json.loads(p.read_text(encoding="utf-8"))
except Exception:
    raise SystemExit(0)
pid = data.get("pid")
url = str(data.get("url") or "")
if isinstance(pid, int) and ":25464" in url:
    print(pid)
PY
}

alive() {
  local pid="$1"
  [ -n "$pid" ] || return 1
  kill -0 "$pid" 2>/dev/null
}

pid=$(hub_pid)
if ! alive "${pid:-}"; then
  "$CLINE" hub start \
    --cwd /opt/core-automation \
    --host 127.0.0.1 \
    --port 25464 \
    --pathname /hub \
    --discovery-path "$DISCOVERY" \
    --no-connectors \
    || { echo "hub start fallito" >&2; exit 1; }
  for _ in $(seq 1 30); do
    pid=$(hub_pid)
    alive "${pid:-}" && break
    sleep 1
  done
fi
alive "${pid:-}" || { echo "hub non attivo dopo l'avvio" >&2; exit 1; }
echo "hub attivo, pid ${pid}"

fail=0
while true; do
  sleep 10
  cur=$(hub_pid)
  if [ "${cur}" = "${pid}" ] && alive "$cur"; then
    fail=0
  else
    fail=$((fail + 1))
    echo "controllo ${fail}/3: atteso pid ${pid}, letto '${cur}'" >&2
    [ "${fail}" -ge 3 ] && exit 1
  fi
done
