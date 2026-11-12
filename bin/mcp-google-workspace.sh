#!/bin/bash
set -euo pipefail
export PATH=/opt/node-v22/bin:/usr/local/bin:/usr/bin:/bin
CRED_DIR=/opt/core-automation/.secrets/google
CRED_FILE="$CRED_DIR/credentials.json"
TOKEN_FILE="$CRED_DIR/tokens.json"

if [[ ! -f "$CRED_FILE" ]]; then
  echo "Manca $CRED_FILE — metti credentials.json OAuth Desktop e riprova." >&2
  exit 1
fi

eval "$(/usr/bin/python3 - "$CRED_FILE" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p, encoding="utf-8"))
block = d.get("installed") or d.get("web") or d
cid = block.get("client_id") or ""
sec = block.get("client_secret") or ""
if not cid or not sec:
    raise SystemExit("credentials.json senza client_id/client_secret")
print(f"export GOOGLE_CLIENT_ID={cid!r}")
print(f"export GOOGLE_CLIENT_SECRET={sec!r}")
PY
)"

export GOOGLE_WORKSPACE_MCP_TOKEN_PATH="$TOKEN_FILE"
export GOOGLE_WORKSPACE_SERVICES="${GOOGLE_WORKSPACE_SERVICES:-drive,gmail,calendar}"
exec /opt/node-v22/bin/google-workspace-mcp "${@:-start}"
