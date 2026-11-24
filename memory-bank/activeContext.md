# Active context

Aggiornato: 2026-11-24 19:43 UTC

- Telegram `home` è di Archivista. Il mittente è in allowlist. OpenClaw spento e disabled. Cline è dismesso: niente Hub e niente chat su 8081.
- Archivista ha `lenovo_fs`, `lenovo_ctl` (`stato_bridge`, `avvia_bridge`) e `google-drive`. Gmail e Calendar restano su main e giramondo.
- Il ponte Lenovo parte all'accesso dell'utente (`ArchivistaLenovoFs`), si rialza da solo, e `avvia_bridge` lo accende solo se è spento.
- Contesto di main e giramondo: profilo `contesto`, 64000. OAuth Google in produzione. Storico prezzi Segugio acceso, senza file di stato.
- L'utente di sistema `cline` resta, perché ci girano Postgres e Valkey. La home `/opt/cline-work` resta.
