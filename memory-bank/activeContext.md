# Active context

Aggiornato: 2026-11-15 16:50 UTC

- Heartbeat `main`: `heartbeat_respond` era offerto ma rifiutato se il trigger non passava anche da `messages.visibleReplies=message_tool`. Ogni ciclo da 30 minuti chiudeva con `agent-runner-failure`.
- Patch in `/root/.nvm/versions/node/v24.22.2/lib/node_modules/openclaw/dist/openclaw-tools-Do7h0W5U.mjs`: un trigger heartbeat accetta il tool. Backup `openclaw-tools-Do7h0W5U.mjs.bak_20261115_164324`.
- Gateway riavviato 16:43 UTC. Prova `heartbeat-main`: ok, nessun invio Telegram (`deliveryStatus=not-requested`).
- Dopo il primo ciclo i worker tornano circa a 1,45 GiB. `wingman-ascolto` resta fermo.
- OpenClaw 2026.11.3: la patch va riapplicata dopo un upgrade del pacchetto.
