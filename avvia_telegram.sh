#!/bin/bash
set -u
TOKEN_FILE=/opt/core-automation/.secrets/telegram_bot_token
TOKEN=$(tr -d '\r\n' < "$TOKEN_FILE")
if [ -z "$TOKEN" ] || [ "$TOKEN" = "INSERISCI_QUI_IL_TOKEN" ]; then
  echo "Token assente. Il bridge non parte. Scrivi il token del bot nuovo in $TOKEN_FILE"
  exit 1
fi
export CLINE_HUB_DISCOVERY_PATH=/opt/core-automation/.cline-data/hub-discovery.json
exec /opt/node-v22/bin/cline \
  --config /opt/core-automation/.cline \
  --data-dir /opt/core-automation/.cline-data \
  connect telegram \
  -k "$TOKEN" \
  --cwd /opt/core-automation \
  --mode plan \
  --no-tools \
  --allowed-user-id 8318140432 \
  --rpc-address 127.0.0.1:25464
