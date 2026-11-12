#!/bin/bash
set -euo pipefail
if [[ -f /opt/core-automation/.secrets/notify.env ]]; then
  set -a
  source /opt/core-automation/.secrets/notify.env
  set +a
fi
TOPIC="${NTFY_TOPIC:-$(tr -d '\r\n' < /opt/core-automation/.secrets/ntfy_topic)}"
BASE_URL="${NTFY_URL:-$(tr -d '\r\n' < /opt/core-automation/.secrets/ntfy_url)}"
CLICK="${NTFY_CLICK:-https://gelindo.org}"
if [[ "$BASE_URL" == *"$TOPIC"* ]]; then
  URL="$BASE_URL"
elif [[ "$BASE_URL" == */ ]]; then
  URL="${BASE_URL}${TOPIC}"
else
  URL="${BASE_URL}/${TOPIC}"
fi
TITLE="Wingman"
if [[ "${1:-}" == "--title" ]]; then
  TITLE="${2:-Wingman}"
  shift 2
fi
if [[ $# -gt 0 ]]; then
  BODY="$*"
else
  BODY=$(cat)
fi
curl -fsS -d "$BODY" \
  -H "Title: ${TITLE}" \
  -H "Priority: default" \
  -H "Click: ${CLICK}" \
  -H "Tags: wingman" \
  "$URL"
echo
