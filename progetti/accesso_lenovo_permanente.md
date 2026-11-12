# Accesso Sicuro e Permanente Lenovo ↔ CX23

## Architettura
- **Protocollo**: SSH crittografato con chiavi asimmetriche (`ed25519`).
- **Persistenza**: Utilizzo di parametri di KeepAlive (`ServerAliveInterval 60`, `ServerAliveCountMax 3`) e `autossh` (o task schedulato Windows) sul PC Lenovo per garantire la riconnessione automatica in background.
- **Sicurezza**: Autenticazione basata esclusivamente su chiave privata/pubblica; nessuna porta esposta al pubblico oltre la 22 protetta da fail2ban e restrizioni firewall (UFW su CX23).

## Configurazione sul PC Lenovo (`C:\Users\web\.ssh\config`)
```ssh
Host gelindo-cx23
    HostName cx23.gelindo.org (o IP pubblico CX23)
    User root
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3
    Compression yes
```

## Script di avvio persistente (PowerShell su Lenovo)
Per mantenere il tunnel attivo in modo permanente e trasparente:
```powershell
while ($true) {
    autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -N -R 20128:127.0.0.1:20128 root@cx23.gelindo.org
    Start-Sleep -Seconds 10
}
```

## Integrazione con Wingman (CX23)
Una volta attivo il tunnel e autorizzato l'accesso, Wingman potrà interagire direttamente con le cartelle locali del Lenovo (es. `Raccolta_MyPassport` / pCloud) in modo sicuro e senza duplicazioni.
