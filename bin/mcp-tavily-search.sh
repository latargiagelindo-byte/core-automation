#!/bin/bash
set -u
KEY_FILE=/opt/core-automation/.secrets/tavily_api_key
KEY=$(tr -d '\r\n' < "$KEY_FILE" 2>/dev/null || true)
if [ -z "$KEY" ] || [ "$KEY" = "INSERISCI_QUI_LA_CHIAVE" ]; then
  echo "Chiave Tavily assente in $KEY_FILE" >&2
  exit 1
fi
export TAVILY_API_KEY="$KEY"
export PATH=/opt/node-v22/bin:/usr/local/bin:/usr/bin:/bin
if [ -x /opt/node-v22/bin/tavily-mcp ]; then
  exec /opt/node-v22/bin/tavily-mcp "$@"
fi
if [ -f /opt/node-v22/lib/node_modules/tavily-mcp/build/index.js ]; then
  exec /opt/node-v22/bin/node /opt/node-v22/lib/node_modules/tavily-mcp/build/index.js "$@"
fi
exec /opt/node-v22/bin/npx -y tavily-mcp@"0.2.22" "$@"
