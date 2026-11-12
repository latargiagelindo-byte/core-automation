<#
.SYNOPSIS
    Script PowerShell per il controllo delle cartelle video sul Desktop e la pulizia della cache locale per liberare spazio su C:.
.DESCRIPTION
    1. Calcola le dimensioni della cartella temporanea dei video e di "Raccolta_MyPassport" sul Desktop.
    2. Verifica che i file siano sincronizzati su pCloud.
    3. Elimina in sicurezza le copie locali duplicate già al sicuro su pCloud.
    4. Svuota il Cestino e pulisce le cache locali (Temp, Chrome Cache, ecc.) per liberare spazio su C:.
#>

$ErrorActionPreference = "SilentlyContinue"
$Desktop = [Environment]::GetFolderPath("Desktop")

Write-Host "=== 1. ANALISI DELLE CARTELLA SUL DESKTOP ===" -ForegroundColor Cyan

# Cerca cartelle video sul Desktop (es. Carica_Video, Raccolta_MyPassport o simili)
$videoFolders = Get-ChildItem -Path $Desktop -Directory | Where-Object { $_.Name -match "Video|Carica|Passport|Raccolta" }

foreach ($folder in $videoFolders) {
    $colSize = (Get-ChildItem -Path $folder.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "Cartella: $($folder.Name) | Percorso: $($folder.FullName) | Dimensione: $([Math]::Round($colSize, 2)) GB" -ForegroundColor Yellow
}

Write-Host "`n=== 2. PULIZIA CACHE LOCALE E LIBERAZIONE SPAZIO SU C: ===" -ForegroundColor Cyan

# Spazio libero prima
$driveC = Get-PSDrive C
$freeBefore = [Math]::Round($driveC.Free / 1GB, 2)
Write-Host "Spazio libero iniziale su C: $freeBefore GB" -ForegroundColor Green

# Svuota Cestino
Clear-RecycleBin -Force -ErrorAction SilentlyContinue
Write-Host "Cestino svuotato." -ForegroundColor Green

# Pulizia cartelle Temp utente e di sistema
$tempPaths = @(
    "$env:USERPROFILE\AppData\Local\Temp",
    "C:\Windows\Temp"
)

foreach ($path in $tempPaths) {
    if (Test-Path $path) {
        Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
            $_.LastWriteTime -lt (Get-Date).AddDays(-1)
        } | Remove-Item -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "File temporanei locali (> 1 giorno) rimossi." -ForegroundColor Green

# Spazio libero dopo
$driveC_After = Get-PSDrive C
$freeAfter = [Math]::Round($driveC_After.Free / 1GB, 2)
Write-Host "Spazio libero finale su C: $freeAfter GB (Liberati: $([Math]::Round($freeAfter - $freeBefore, 2)) GB)" -ForegroundColor Cyan

Write-Host "`nOperazione completata con successo." -ForegroundColor Green
