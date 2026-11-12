#!/bin/bash
set -euo pipefail
if [[ -f /opt/core-automation/.secrets/actual.env ]]; then
  set -a
  # shellcheck disable=SC1091
  source /opt/core-automation/.secrets/actual.env
  set +a
fi
export ACTUAL_SERVER_URL="${ACTUAL_SERVER_URL:-http://127.0.0.1:5006}"
export ACTUAL_BUDGET_SYNC_ID="${ACTUAL_BUDGET_SYNC_ID:-ffa8459e-0ffc-48cb-a63c-7d8ab5136fc7}"
export ACTUAL_SYNC_TTL_MS="${ACTUAL_SYNC_TTL_MS:-60000}"
if [[ -z "${ACTUAL_PASSWORD:-}" && -z "${ACTUAL_SESSION_TOKEN:-}" ]]; then
  echo "actual-mcp: missing ACTUAL_PASSWORD (or ACTUAL_SESSION_TOKEN) in /opt/core-automation/.secrets/actual.env" >&2
  exit 2
fi
BIN=""
for c in /root/.nvm/versions/node/v24.22.2/bin/actual-mcp /opt/node-v22/bin/actual-mcp "$(command -v actual-mcp 2>/dev/null || true)"; do
  if [[ -n "$c" && -x "$c" ]]; then BIN="$c"; break; fi
done
if [[ -z "$BIN" ]]; then
  echo "actual-mcp binary not found" >&2
  exit 127
fi
# NO --enable-write => read-only
exec "$BIN"
