# Active context

Updated: 2026-11-14 10:17 UTC

## Focus
OpenClaw gateway stabilizzato su CX23 (heap 1536, MemoryHigh 1.6G / MemoryMax 1.85G).

## Now
- Gateway active, Telegram connected (polling), bind loopback :18789.
- Workspace: PENDING.md symlink → state; TOOLS.md + HEARTBEAT.md ripristinati; plugins.allow=[brave, telegram].
- Cron morning-0800-posta: messaggio aggiornato (no prompts_get vuoto).
- Paperless healthcheck allineato a :8010 → healthy.
- control-ui-tailscale.url chmod 600. Token non ruotato.

## Avoid
- Non rieseguire `openclaw doctor --fix` senza supervisione: può rimuovere TOOLS.md/HEARTBEAT.md.
- Non alzare heap a 2048 su host 3.7 GiB.
- Sandbox off e no fail2ban (scelta Gelindo).
