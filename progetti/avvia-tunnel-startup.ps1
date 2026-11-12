<#
.SYNOPSIS
    Script di avvio automatico del tunnel SSH inverso per OmniRoute (Porta 20128) da Lenovo a CX23.
.DESCRIPTION
    Esegue il tunnel SSH in background con riconnessione automatica in caso di caduta della linea.
    Da inserire nella cartella Esecuzione Automatica (Shell:startup) del PC Lenovo.
#>

$ErrorActionPreference = "SilentlyContinue"

# Configurazione host e porte
$SSHHost = "gelindo-cx23" # Configurato in C:\Users\web\.ssh\config
$RemotePort = "20128"
$LocalPort = "20128"

while ($true) {
    # Avvia ssh in modalità non-interattiva con keepalive attivo e port forwarding inverso (-R)
    ssh -N -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -R "$RemotePort`:127.0.0.1:$LocalPort" $SSHHost
    
    # Se il tunnel cade, attende 10 secondi prima di riprovare
    Start-Sleep -Seconds 10
}
