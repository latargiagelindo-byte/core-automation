#!/bin/bash
# Controllo di sola lettura. Non cambia configurazioni e non riavvia servizi.
set -u
LOG="/opt/omniroute/data/logs/manutenzione.log"
DB="/opt/omniroute/data/storage.sqlite"
mkdir -p "$(dirname "$LOG")"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
{
  echo "=== settimanale ${STAMP} ==="
  if ss -ltn | awk '$4=="127.0.0.1:20128"{found=1} END{exit found?0:1}'; then
    echo "servizio: in ascolto su 127.0.0.1:20128"
  else
    echo "servizio: porta 20128 non in ascolto"
  fi
  du -sh /opt/omniroute/data | awk '{print "data_dir:", $1}'
  echo "connessioni esaurite:"
  esaurite="$(sqlite3 -separator ' | ' "$DB" \
    "SELECT COALESCE(name,'(senza nome)'), provider, COALESCE(test_status,''), COALESCE(last_error_type,'')
     FROM provider_connections
     WHERE is_active=1
       AND (
         test_status IN ('quota_exhausted','credits_exhausted')
         OR last_error_type IN ('quota_exhausted','credits_exhausted')
       )
     ORDER BY provider, name;")"
  if [[ -n "$esaurite" ]]; then
    printf '%s\n' "$esaurite"
  else
    echo "(nessuna)"
  fi
  echo "breaker aperti:"
  aperti="$(sqlite3 -separator ' | ' "$DB" \
    "SELECT name, state, failure_count FROM domain_circuit_breakers WHERE state != 'CLOSED' ORDER BY name;")"
  if [[ -n "$aperti" ]]; then
    printf '%s\n' "$aperti"
  else
    echo "(nessuno)"
  fi
  echo "=== fine settimanale ==="
} >> "$LOG" 2>&1
