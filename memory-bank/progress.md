# Progress

Updated: 2026-11-14 10:17 UTC

## Done
- Symlink workspace/PENDING.md → state/PENDING.md.
- TOOLS.md da bak; HEARTBEAT.md da memory-backup/latest (ripristinati anche post doctor).
- Cron morning-0800-posta: guard prompts_get + Gmail-only in message; install-morning-crons.sh allineato.
- gateway install --force --runtime-path node v24.22.2; unit MemoryHigh=1.6G MemoryMax=1.85G max-old-space-size=1536.
- Paperless compose healthcheck → curl 127.0.0.1:8010; container healthy.
- chmod 600 control-ui-tailscale.url; plugins.allow brave (+ telegram da doctor).
- Smoke: health 200, Telegram connected, audit critical=0.

## Open
- Doctor: memory.search provider openai senza API key.
- Swap ~1.4 GiB: monitorare dopo 24h.
- doctor --fix può hangare su agent-db: usare timeout/supervisione.
