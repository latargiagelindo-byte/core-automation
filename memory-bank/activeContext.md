# Active context

Aggiornato: 2026-11-12 sera (chiusura giornata)

## Focus
OpenClaw POC su CX23 operativo: stesso bot Telegram, OmniRoute 127.0.0.1:20128, memory-bank travasata, Control UI via Tailscale Serve.
Telegram testato OK (risposte + attivita autonoma). wingman-ascolto stopped.

## Accesso Control UI
- URL: https://gelindo-cx23.tail00a81c.ts.net/
- Token: /opt/openclaw/state/control-ui.url (o control-ui-tailscale.url)
- Tailnet ora: solo gelindo-cx23 + lenovogel (PC). Android ancora fuori -> sul tel non apre finche Tailscale Active stesso account.
- Serve: foreground proxy :443 -> 127.0.0.1:36055 (gestito da OpenClaw tailscale.mode=serve)

## Stato noto a fine giornata
- Gateway active; OmniRoute :20128; SocialPulse :3920; Hub :8081
- RAM stretta (~3.0/3.7G, gateway ~1.5G RSS)
- MCP openpulse: timeout 22:06, processo assente — ripartire
- Cron mattina OpenClaw 07:30-09:00: script install presente, NON in crontab (solo vecchio morning_briefing.py 09:00)

## Domani (coda)
1. Ripristino MCP openpulse + install cron stagger mattina
2. Tailscale su Android -> verifica Control UI tel
3. Coda posticipata: foto Drive->Foto Lenovo; Metricool; AWS
