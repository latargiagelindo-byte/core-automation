# Active context

Aggiornato: 2026-11-17 13:54 UTC

- Gateway: heap V8 768 MiB, MemoryHigh=1200M, MemoryMax=1450M. NODE_OPTIONS unifica IPv4 e il tetto heap, anche per i figli.
- Riavvio 13:53 UTC, health 200, NRestarts=0. Subito dopo il cgroup e circa 1,07 GiB: sotto la soglia alta, con poco margine.
- state/ pesa 65 MiB. memoryFlush acceso. I 1,2 GiB precedenti erano heap del processo, non sessioni su disco.
- Patch heartbeat nel pacchetto npm 2026.11.3 ancora presente: va riapplicata dopo un upgrade.
