# OmniRoute 3.8.52 — guida operativa

Data: 24 novembre 2026  
Istanza: CX23, pacchetto `omniroute` 3.8.52, dati in `/opt/omniroute/data`, ascolto su `127.0.0.1:20128`.

Le sezioni **Fatti** citano la documentazione del progetto. Le sezioni **Scelte per questa macchina** sono deduzioni sullo stato verificato quel giorno. Nessuna chiave è riportata in questo file.

## Fonti

- Repository: https://github.com/cheaper-inference/OmniRoute
- Release pubblicata più recente al 24 novembre 2026: **v3.8.54**, 17 novembre 2026. Il pacchetto installato è **3.8.52**.
- User Guide sul branch `release/v3.8.55` (gli identificatori di modello di quel branch non vanno copiati alla cieca: sul server fa fede `GET /v1/models`).
- `docs/reference/ENVIRONMENT.md` sullo stesso branch.
- Resilience Guide, intestazione 3.8.52, aggiornata il 18 ottobre 2026.
- `docs/security/INFERENCE_AUTH_POSTURE.md` sul tag v3.8.52.
- `.env.selfhost.example` sul branch principale.

## Fatti della documentazione

OmniRoute è un gateway locale. Dashboard e API stanno sulla porta 20128. I client OpenAI-compatibili chiamano `http://127.0.0.1:20128/v1`. I dati stanno in `DATA_DIR` (default `~/.omniroute`): database, usage e log.

Avvio continuo documentato:

```bash
omniroute autostart enable
```

Su Linux senza interfaccia questo aggancia il servizio systemd dell’utente. In alternativa PM2:

```javascript
module.exports = {
  apps: [{
    name: "omniroute",
    script: "npm",
    args: "start",
    env: {
      NODE_ENV: "production",
      OMNIROUTE_MEMORY_MB: "512",
      DATA_DIR: "/opt/omniroute/data"
    },
    node_args: "--max-old-space-size=512",
    max_memory_restart: "300M"
  }]
};
```

`OMNIROUTE_MEMORY_MB` di default vale 512. `OMNIROUTE_PRESSURE_SELF_RESTART=true` fa uscire il processo se la pressione di memoria resta critica, così il supervisore lo rialza.

Log applicativi:

```bash
APP_LOG_TO_FILE=true
APP_LOG_FILE_PATH=logs/application/app.log
APP_LOG_MAX_FILE_SIZE=50M
APP_LOG_RETENTION_DAYS=7
APP_LOG_MAX_FILES=20
CALL_LOG_RETENTION_DAYS=7
PROXY_LOGS_TABLE_MAX_ROWS=100000
```

Il percorso del file di log è relativo a `DATA_DIR`. La tabella `proxy_logs` viene potata a 100.000 righe. I backup SQLite automatici sono attivi e al massimo uno ogni 60 minuti, salvo `DISABLE_SQLITE_AUTO_BACKUP=true`.

Routing, due livelli.

Tra account dello stesso provider: Fill First, Round Robin (3 richieste, poi si sposta), P2C, Random, Least Used, Cost Optimized.

Dentro una combo: `priority` segue l’ordine e non ruota; `round-robin` e `least-used` spalmano le quote; `fill-first` svuota il primo modello. Esempio gratuito della guida upstream:

```bash
omniroute combo create free-stack \
  --models "groq/llama-3.3-70b-versatile,gemini/gemini-2.5-flash,cerebras/gpt-oss-120b" \
  --strategy round-robin
```

Un 429 di una chiave non apre il circuit breaker del provider. Mette in cooldown solo quella connessione. Il breaker scatta sui 408, 500, 502, 503 e 504. `comboCooldownWait` può attendere un 429 breve e riprovare. Non attende `quota_exhausted` né errori di autenticazione. Quota esaurita e cooldown stanno in memoria: dopo un restart la prima richiesta può prendere un altro 429.

NVIDIA NIM, nella User Guide, è a pagamento (`nvidia/…`). OpenRouter è un catalogo in passthrough (`openrouter/…`).

Rete, da `.env.selfhost.example`:

```bash
APP_BIND_HOST=127.0.0.1
REQUIRE_API_KEY=true
```

`REQUIRE_API_KEY` nasce a `false`. Con quel valore un bearer sbagliato viene trattato come anonimo. `GET /v1/models` che risponde 401 non dimostra che l’inferenza sia protetta: la prova è `POST /v1/chat/completions`. Se il processo ascolta fuori da localhost con la chiave non obbligatoria, all’avvio scrive un avviso e parte lo stesso. La sezione VPS della User Guide mostra `HOSTNAME=0.0.0.0`. La guida di sicurezza dice di allargare il bind solo con `REQUIRE_API_KEY=true` o con un reverse proxy che autentica.

Cifratura del database:

```bash
STORAGE_ENCRYPTION_KEY=$(openssl rand -hex 32)
```

Senza una copia di quella chiave il database cifrato non si rilegge. `ALLOW_API_KEY_REVEAL` resta a `false`.

## Stato verificato il 24 novembre 2026

- `omniroute status` con `DATA_DIR=/opt/omniroute/data` riporta versione 3.8.52 e data dir `/opt/omniroute/data`. Il database c’è.
- Il processo ascolta solo `127.0.0.1:20128`.
- PM2, file `/opt/omniroute/ecosystem.config.cjs`: `max_memory_restart` è `1600M`, `OMNIROUTE_MEMORY_MB` è `1024`. Il tetto di riavvio è già sopra il heap. `HOST`, `API_HOST` e `OMNIROUTE_SERVER_HOST` sono `127.0.0.1`. `DATA_DIR` è già `/opt/omniroute/data`.
- In `/opt/omniroute/data/.env` la variabile `STORAGE_ENCRYPTION_KEY` è presente. `REQUIRE_API_KEY`, `APP_BIND_HOST`, `HOSTNAME` e `PORT` non sono in quel file. Il bind reale è quello dell’ecosistema PM2, non `APP_BIND_HOST`.
- Senza `DATA_DIR` il CLI carica prima `/root/.omniroute/.env` e ignora la chiave del pacchetto. Quel file esiste ancora ed è un residuo: non va cancellato senza una conferma a parte.
- La copia di sicurezza già prevista è `/opt/core-automation/bin/backup_omniroute.sh`. Tiene al massimo due copie di database e di `.env` in `/var/backups/omniroute`, permessi 600. Si lancia a mano.
- Non ci sono timer di manutenzione OmniRoute.

## Scelte per questa macchina

Il bind resta su localhost. Il Lenovo ci arriva dal tunnel SSH. Non impostare `HOSTNAME=0.0.0.0`.

`REQUIRE_API_KEY=true` è la chiusura delle chiamate anonime. Va aggiunto nell’ambiente del processo e il processo va riavviato, altrimenti il flag non entra in vigore. I client già collegati (ZeroClaw, Archivista) devono continuare a mandare il bearer. `APP_BIND_HOST` nel `.env` di questa installazione PM2 non è la variabile che tiene il processo su localhost: quella è già `HOST` / `API_HOST` / `OMNIROUTE_SERVER_HOST`.

La combo `gratis` resta in strategia `priority`. Un provider a `quota_exhausted` non va atteso dal cooldown della combo: il round-robin continuerebbe a mandarci una parte delle richieste. Due chiavi OpenRouter attive sono il caso del cooldown di connessione: un 429 ne esclude una, l’altra resta utilizzabile.

Ogni invocazione del CLI deve avere `DATA_DIR=/opt/omniroute/data`. L’alias proposto, nel bash di root:

```bash
alias omniroute='DATA_DIR=/opt/omniroute/data command omniroute'
```

`command` evita che il nome dentro l’alias richiami di nuovo l’alias. La verifica è `omniroute status`: la riga Data Dir deve essere `/opt/omniroute/data` e non deve comparire «Authentication required».

Non abbassare `max_memory_restart` a 600M. Oggi è 1600M, sopra i 1024 MB di heap. Abbassarlo farebbe ripartire il processo prima del limite di memoria di Node.

I controlli automatici scrivono solo in `/opt/omniroute/data/logs/manutenzione.log`. Non modificano configurazioni e non riavviano servizi. Il log non contiene chiavi: per la cifratura registra solo «presente» o «assente». Il backup mensile è lo script già esistente. La prova `POST` senza bearer si fa solo se `REQUIRE_API_KEY=true` è davvero nell’ambiente del processo; altrimenti la chiamata può uscire verso un provider e consumare quota. In quel caso il controllo scrive che la prova è stata saltata.

## Checklist

Ogni lunedì alle 08:00, in automatico quando il timer sarà attivo:

- Servizio PM2 `omniroute` su o giù.
- Dimensione di `/opt/omniroute/data`.
- Connessioni in `quota_exhausted` o `credits_exhausted`, e breaker aperti, senza stampare chiavi.
- Una riga di riepilogo nel log.

Il primo giorno del mese alle 08:30:

- `bin/backup_omniroute.sh`, massimo due copie.
- Presenza di `STORAGE_ENCRYPTION_KEY`, senza valore.
- Codice HTTP del `POST /v1/chat/completions` senza chiave, solo se il flag è attivo. L’esito atteso è 401.

A mano, quando serve:

- Dashboard, pagina Health, dopo un’interruzione.
- Una richiesta corta su una chat nuova verso `gratis`. Una chat già sopra i 32.000 token non misura il routing: DeepSeek ha rifiutato 34.167 token contro un massimo di 32.768.
- Confronto della versione installata con il tag GitHub prima di un aggiornamento. Il salto utile al 24 novembre 2026 è 3.8.53 e 3.8.54.
