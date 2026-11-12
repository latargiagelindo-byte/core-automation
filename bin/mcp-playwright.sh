#!/bin/bash
set -euo pipefail
export PATH="/opt/node-v22/bin:$PATH"
export NODE_PATH="/opt/node-v22/lib/node_modules"
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-/root/.cache/ms-playwright}"
# Headless Chromium for Wingman form filling. Submit policy: Cline rules (OK esplicito).
exec /opt/node-v22/bin/node /opt/node-v22/lib/node_modules/@playwright/mcp/cli.js --browser chromium --headless "$@"
