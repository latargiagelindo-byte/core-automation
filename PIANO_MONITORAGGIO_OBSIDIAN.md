# Piano: Monitoraggio Silenzioso della Fortezza CX23 con Obsidian e AWS

## 1. Obiettivi e Principi (da IDENTITA_E_VISIONE.md)
- **Sobrietà e Privacy-First**: Monitoraggio locale ed eco-compatibile sul server CX23, senza dipendenze commerciali pesanti.
- **Integrazione AWS (eu-north-1)**: Sfruttamento delle risorse nel rispetto del Free Tier e dei crediti di progetto.
- **Obsidian come "Cervello della Fortezza"**: Centralizzazione dei report in formato Markdown pulito e strutturato.

## 2. Percorsi dei File su CX23 (`/opt/core-automation`)
- **Script di Monitoraggio Fortezza**: `/opt/core-automation/bin/fortress_monitor.py` (raccoglie metriche di sistema, stato servizi systemd/PM2, esito backup S3).
- **Cartella Markdown locale**: `/opt/core-automation/data/obsidian/fortress/`
- **Nota principale**: `/opt/core-automation/data/obsidian/fortress/Stato-Fortezza.md`
- **Storico report JSON**: `/opt/core-automation/data/fortress_history/`

## 3. Strategia di Sincronizzazione con Obsidian
- **Canale primario (Google Drive MCP / API)**: Lo script di monitoraggio genera il file Markdown e, tramite integrazione Google Drive, lo aggiorna direttamente nella cartella dedicata su Google Drive di Gelindo (es. `Obsidian/Fortezza-CX23/`), sincronizzandosi automaticamente su tutti i client locali di Gelindo.
- **Alternativa locale**: Sincronizzazione via Git privato o cartella condivisa Syncthing se configurata.

## 4. Schema della Nota Markdown ("Cervello della Fortezza")

```markdown
---
data_aggiornamento: "YYYY-MM-DD HH:MM:SS"
regione_aws: "eu-north-1"
profilo: "greenfield-adventures"
stato_generale: "OPERATIVO / ATTENZIONE"
---

# 🛡️ Monitoraggio Fortezza CX23

## 1. Stato dei Servizi e Risorse
- **CPU / RAM / Disco**: [Metriche attuali]
- **Servizi attivi**: [systemd / PM2 / Chat Server]
- **Aggiornamenti software (sola lettura)**: [Ultimo controllo da updater_monitor.py]

## 2. Backup e Sicurezza AWS (eu-north-1)
- **Ultimo Backup S3**: [Data / Esito]
- **Policy Lifecycle**: [Attiva / Costo zero]

## 3. Sintesi e Azioni Consigliate (Wingman)
- [Note operative e spunti di riflessione]
```
