#!/bin/bash
set -u
export PATH=/opt/node-v22/bin:/usr/local/bin:/usr/bin:/bin
export HOME=/opt/core-automation
export CLINE_HUB_DISCOVERY_PATH=/opt/core-automation/.cline-data/hub-discovery.json
ROOM=$(tr -d '\r\n' < /opt/core-automation/.secrets/room-secret)
if [ -z "$ROOM" ]; then
  echo "room-secret assente" >&2
  exit 1
fi
LOG=/opt/core-automation/data/dashboard.log
# Keep the real process as PID 1 of the service; send banner to a redacted log.
exec > >(
  while IFS= read -r line || [ -n "$line" ]; do
    printf '%s\n' "${line//$ROOM/***}" >> "$LOG"
  done
) 2>&1
exec /opt/node-v22/bin/cline hub dashboard \
  --no-open \
  --cwd /opt/core-automation \
  --config /opt/core-automation/.cline \
  --data-dir /opt/core-automation/.cline-data \
  --host 127.0.0.1 \
  --port 8080 \
  --room-secret "$ROOM" \
  --public-url https://preview.gelindo.org
