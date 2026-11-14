# Stato foto rclone

Aggiornato: 2026-11-14 17:44 Europe/Rome

Scheda completa per Wing: `/opt/openclaw/workspace/memory-bank/stato_foto_rclone.md`

## Regole
- Drive e cartelle foto deputate sul Lenovo: coda verso Google Foto (rclone).
- Downloads: solo classificazione. Niente upload automatico.
- Zero cancellazioni senza elenco + OK di Gelindo.

## Verifica mancanti Carica_Google_Foto (107)
- **99 OK** → album Photos `Carica_mancanti_verificati` (~250 MiB)
- **8 SKIP**: 7 `._*` + 1 JPG vuoto
- Report: `verifica_mancanti_107.csv`, `mancanti_107_SKIP.csv`

## Censimento Drive (2026-11-12)
- `Carica_Google_Foto`: 12395 file / 25.819 GiB
- `_TUTTE_LE_FOTO`: 1789 / 1.057 GiB
- `Foto_Salvate_PC`: 749 / 2.034 GiB
- `Raccolta_Temporanea_Foto`: 0
- Sparpagliate: ~17100 immagini fuori cartelle note

## Coda
1. ~~Mancanti Carica (107)~~ FATTO
2. `_TUTTE_LE_FOTO` ← **prossimo**
3. `Foto_Salvate_PC`
4. `Raccolta_Temporanea_Foto`
5. Sparpagliate → cartella unica (dopo OK)

## Prossimo passo
Riprendere rclone copy di `_TUTTE_LE_FOTO` sul Lenovo; poi resto coda. Staging globale solo dopo prioritarie + OK Gelindo.
