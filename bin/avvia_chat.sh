#!/bin/bash
set -u
export PATH=/usr/bin:/bin
export COREAUTO_CHAT_HOST=127.0.0.1
export COREAUTO_CHAT_PORT=8081
export OMNIROUTE_API_URL=http://127.0.0.1:20128/v1
export OMNIROUTE_MODEL=gratis
export OMNIROUTE_STRATEGY=priority
exec /usr/bin/python3 /opt/core-automation/chat_server.py
