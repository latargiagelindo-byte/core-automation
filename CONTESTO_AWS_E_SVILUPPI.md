# Contesto AWS e sviluppi — Core Automation / Wingman

Aggiornato: 2026-11-10 (verificato live su CX23)

Documento unico di memoria operativa AWS per **Cline (Hub)** e operatori umani.
Complementare a `STATO_PROGETTO.md` / `memory-bank/activeContext.md`.
Regola Cursor correlata: `.cursor/rules/aws-infrastructure.mdc` (`alwaysApply: true`).

---

## 1. Identità progetto (new AWS experience)

| Campo | Valore |
| --- | --- |
| Progetto | **Greenfield Adventures** |
| Account ID | `113016737452` |
| Experience | **New AWS Experience** (Builder ID + progetto, non root classico) |
| Regione obbligatoria | **`eu-north-1`** (Stoccolma) |
| Piano | Free plan (crediti / scadenza indicativa maggio 2027) |
| Profilo AWS CLI (CX23) | **`greenfield-adventures`** |
| Auth tipica | `aws login` (credenziali sessione ~12h; rinnovo fino ~90g) |
| Ruolo sessione verificato | `arn:aws:sts::113016737452:assumed-role/AccountFullAccessRole/...` |

Terminologia da usare con gli agenti:

- dire **progetto** (non “account” generico)
- dire **team member** (non “IAM user” per accessi umani)
- gestione billing/team: **AWS Settings** → https://settings.aws.com/
- risorse: **AWS Management Console** del progetto

---

## 2. Host operativo CX23

| Voce | Dettaglio |
| --- | --- |
| Server | Debian CX23 (`gelindo-cx23`), runtime `/opt/core-automation` |
| AWS CLI | v2.39.x in `/usr/local/bin/aws` |
| `uv` / `uvx` | 0.13.x in `/usr/local/bin` (symlink → `/root/.local/bin`) |
| Credenziali | `/root/.aws` (login cache); Hub `HOME=/opt/core-automation` con symlink `.aws/login` e `.aws/cli` → `/root/.aws/...` |
| MCP Hub file | `/opt/core-automation/.cline-data/settings/cline_mcp_settings.json` |

Comandi utili:

```bash
export AWS_PROFILE=greenfield-adventures
export AWS_REGION=eu-north-1
aws sts get-caller-identity
```

Login headless tipico (PC Windows + tunnel callback oppure `--remote`):

```bash
# sul CX23, con tunnel SSH -L 8400:127.0.0.1:8400 dal PC:
aws login --redirect-port 8400 --region eu-north-1 --profile greenfield-adventures
# oppure:
aws login --remote --region eu-north-1 --profile greenfield-adventures
```

---

## 3. Server MCP attivi (Hub Cline)

File: `/opt/core-automation/.cline-data/settings/cline_mcp_settings.json`

### AWS

| Server | Ruolo | Note |
| --- | --- | --- |
| `aws-mcp` | Proxy ufficiale Agent Toolkit → `https://aws-mcp.us-east-1.api.aws/mcp` | `command=/usr/local/bin/uvx`, env `AWS_MCP_PROXY_PROFILES=greenfield-adventures`, `HOME=/root` |
| `awslabs.aws-documentation-mcp-server` | Documentazione AWS aggiornata | `uvx`, `autoApprove: []`, `AWS_REGION=eu-north-1` |
| `awslabs.core-mcp-server` | Tool awslabs core | `uvx`, `autoApprove: []`, approvazione esplicita |

### Già presenti (non AWS)

`filesystem`, `memory`, `tavily-search`, `google-workspace` (+ eventuale `actual-mcp` nella copia `.cline/data`).

Agent Toolkit: ~25 skill in `/root/.cline/skills` (es. `aws-serverless`, `aws-iam`, `amazon-bedrock`, …).

---

## 4. Risorse AWS attive (verificate 2026-11-10)

### S3 — backup

- Bucket: **`core-automation-backup-113016737452-eu-north-1`**
- Region constraint: `eu-north-1`
- Oggetti noti al momento della verifica:
  - `test.txt`
  - `core-automation-backup_20261110_191010.tar.gz` (~923 MB)
- Uso: deposito backup Core Automation / CX23; target per job di backup (anche notturni).

### Lambda

- Nome: **`HelloCline`**
- Runtime: `python3.12` (`x86_64`)
- Handler: `lambda_function.lambda_handler`
- Role: `arn:aws:iam::113016737452:role/HelloClineRole`
- Timeout / memory: 3s / 128 MB
- Ruolo: smoke / hello-world per validare deploy serverless da Cline/Cursor

### Altro

- EventBridge / Scheduler: nessun rule/schedule dedicato rilevato al momento della verifica (il backup notturno va formalizzato su CX23 cron e/o EventBridge se/quando definito).

---

## 5. Vincoli Free Tier / budget / regione

- **Creare risorse Regionali solo in `eu-north-1`.**
- Eccezioni limitate (WAF / CloudWatch Logs / CloudFront globali) solo dove la documentazione new-experience lo consente; non spostare Lambda/API Gateway fuori da `eu-north-1`.
- Free plan: rispettare servizi ammessi e crediti; evitare risorse costose non richieste.
- In caso di `Access Denied` improvvisi: verificare spend limit / stato piano in AWS Settings → Billing.
- Non chiedere né salvare Access Key lunghe se basta `aws login` a sessione.
- `autoApprove` AWS MCP: conservativo (operazioni cloud = conferma esplicita Gelindo).

---

## 6. Prospettive di sviluppo (serverless / AI)

Ordine di lavoro suggerito (un pezzo alla volta, con OK esplicito su costi):

1. **Backup notturno affidabile** → sync selettivo `/opt/core-automation` (esclusi segreti/cache) verso `s3://core-automation-backup-113016737452-eu-north-1/` + retention.
2. **Serverless operativo** → estendere oltre `HelloCline` (API HTTP, EventBridge, DLQ, IAM least-privilege).
3. **Osservabilità** → CloudWatch Logs/metriche nella selected Region; allarmi NTFY se utile.
4. **AI su AWS (opzionale)** → Bedrock / skill Agent Toolkit solo dopo verifica disponibilità Free plan in `eu-north-1` e stima costi.
5. **Integrazione Wingman** → tool MCP/Cline per inventario risorse, restore da S3, deploy guidato.

Non attivare “funzionalità avanzate” AWS senza richiesta esplicita.

---

## 7. Checklist rapida per agenti

1. `aws sts get-caller-identity --profile greenfield-adventures`
2. Lavorare solo in `eu-north-1`
3. Prima di creare risorse: leggere questo file + skill Agent Toolkit rilevante
4. Documentare qui ogni nuova risorsa stabile (nome, ARN/ID, scopo, data)
5. Aggiornare anche `memory-bank/activeContext.md` e, in locale, `STATO_PROGETTO.md`

---

## 8. Cronologia sintetica

| Data | Evento |
| --- | --- |
| 2026-11-10 | Install `uv`/`aws` CLI; MCP awslabs; template `~/.aws` |
| 2026-11-10 | Login progetto Greenfield Adventures (tunnel callback :8400) |
| 2026-11-10 | Agent Toolkit + `aws-mcp`; skill Cline |
| 2026-11-10 | Bucket S3 backup + Lambda `HelloCline` |
| 2026-11-10 | Creati questo documento e regola Cursor `aws-infrastructure.mdc` |
