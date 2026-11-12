#!/bin/bash
# Copia consistente del database OmniRoute. Si lancia a mano. Massimo 2 copie.
set -euo pipefail

SRC_DB="/opt/omniroute/data/storage.sqlite"
SRC_ENV="/opt/omniroute/data/.env"
DEST_DIR="/var/backups/omniroute"
STAMP="$(date +%Y%m%d_%H%M%S)"

if [[ ! -f "$SRC_DB" ]]; then
  echo "Database assente: $SRC_DB" >&2
  exit 1
fi
if [[ ! -f "$SRC_ENV" ]]; then
  echo "Chiave assente: il database senza .env non si riapre." >&2
  exit 1
fi

mkdir -p "$DEST_DIR"
chmod 700 "$DEST_DIR"

DEST_DB="$DEST_DIR/storage_${STAMP}.sqlite"
sqlite3 "$SRC_DB" ".backup ${DEST_DB}"
result="$(sqlite3 "$DEST_DB" "PRAGMA integrity_check;")"
if [[ "$result" != "ok" ]]; then
  echo "Copia non integra: $result" >&2
  rm -f "$DEST_DB"
  exit 1
fi
chmod 600 "$DEST_DB"
install -m 600 "$SRC_ENV" "$DEST_DIR/env_${STAMP}"

ls -1t "$DEST_DIR"/storage_*.sqlite 2>/dev/null | tail -n +3 | xargs -r rm -f
ls -1t "$DEST_DIR"/env_* 2>/dev/null | tail -n +3 | xargs -r rm -f

echo "Backup OmniRoute ok: $DEST_DB"
