# Active context

Aggiornato: 2026-11-17 20:00 UTC

- Gateway in ascolto su 127.0.0.1:18789. Riavvio dopo il plugin elefante, circa 17:47 UTC. Heap 768 MiB e limiti cgroup restano quelli del pomeriggio.
- `google-workspace__send_email` non è nell'array tools del modello. La chiamata nativa è `dispatch_action` con id `google-workspace__send_email` e args `to` (array), `subject`, `body`. Il campo `message` non esiste.
- Il plugin `no-false-confirm` rifiuta il JSON scritto in chat se manca una tool_call nativa (`content` di tipo `toolCall`). I test del modello restano per il 18/11. Ultimo invio reale: `1a1eaa42e554bdd1`.
