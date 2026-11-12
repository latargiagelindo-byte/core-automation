# Stato foto rclone

Aggiornato: 2026-11-12 20:47 Europe/Rome

## Regole
- Drive e cartelle foto deputate sul Lenovo: coda verso Google Foto.
- Downloads: solo classificazione (privata / lavoro / ignora). Niente upload automatico.
- Zero cancellazioni senza elenco + OK di Gelindo.

## Coda Drive (ordine)
1. Mancanti Carica_Google_Foto (107)
2. _TUTTE_LE_FOTO
3. Foto_Salvate_PC
4. Raccolta_Temporanea_Foto
5. Sparpagliate su Drive: 17100 file immagine fuori dalle cartelle note

## Cartelle Drive note
cartella,oggetti,byte,errore
gdrive:Carica_Google_Foto,12.395k (12395),25.819 GiB (27722640078 Byte),
gdrive:_TUTTE_LE_FOTO,1.789k (1789),1.057 GiB (1135295499 Byte),
gdrive:Foto_Salvate_PC,749,2.034 GiB (2184301558 Byte),
gdrive:Raccolta_Temporanea_Foto,0,0 B (0 Byte),

## Lenovo cartelle deputate
percorso,file,byte
"C:\Users\web\Pictures",238,166746883
"C:\Users\web\Documents\Immagini",0,0
"C:\Users\web\Documents\00_MEDIA_DA_VALUTARE",15,7015702
"C:\Users\web\Documents\Archivio_Raccolta_MyPassport",12395,27722640078

## Downloads (da revisionare, non caricati)
- Private candidate: 20
- Lavoro candidate: 0
- Ignota / da vedere: 35

## Prossimo passo
Riprendere rclone copy dei mancanti quando la quota Photos e libera.
