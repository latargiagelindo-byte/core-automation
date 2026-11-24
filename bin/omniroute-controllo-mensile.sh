#!/bin/bash
# Copia di sicurezza e prove. Non cambia configurazioni e non riavvia servizi.
set -u
LOG="/opt/omniroute/data/logs/manutenzione.log"
ENV_FILE="/opt/omniroute/data/.env"
mkdir -p "$(dirname "$LOG")"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
{
  echo "=== mensile ${STAMP} ==="
  if /opt/core-automation/bin/backup_omniroute.sh; then
    echo "backup: ok, al massimo due copie"
  else
    echo "backup: fallito"
  fi
  if grep -qE '^STORAGE_ENCRYPTION_KEY=.+' "$ENV_FILE"; then
    echo "STORAGE_ENCRYPTION_KEY: presente"
  else
    echo "STORAGE_ENCRYPTION_KEY: assente"
  fi
  flag="$(grep -E '^REQUIRE_API_KEY=' "$ENV_FILE" | tail -n 1 | cut -d= -f2- | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]')"
  if [[ "$flag" == "true" || "$flag" == "1" || "$flag" == "yes" ]]; then
    code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 \
      -X POST http://127.0.0.1:20128/v1/chat/completions \
      -H 'content-type: application/json' \
      -d '{"model":"gratis","messages":[{"role":"user","content":"ping"}]}')"
    echo "post_senza_chiave: ${code}"
  else
    echo "post_senza_chiave: saltata, REQUIRE_API_KEY non attivo"
  fi
  echo "=== fine mensile ==="
} >> "$LOG" 2>&1
