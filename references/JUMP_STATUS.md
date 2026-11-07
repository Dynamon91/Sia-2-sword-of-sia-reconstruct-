# Salto e caduta — tre pose integrate nella ROM

Aggiornamento del 7 novembre 2026. La build esistente ora usa tre sagome osservate nel video del Mondo 1, livello 1, al posto della precedente posa unica di salto. Le pose provengono da due salti della stessa sequenza; non sono nuovi disegni né sprite originali recuperati.

| Fase | Riferimento video | Selezione nella ricostruzione |
| --- | --- | --- |
| Salita | 120,08 s | Velocità verticale inferiore a −0,5 pixel per aggiornamento |
| Apice | 120,32 s | Velocità verticale fra −0,5 e 0 |
| Caduta | 119,50 s | Velocità verticale positiva, anche lasciando un bordo |

Le soglie sono stimate. Gli attacchi mantengono la propria animazione; presa e risalita usano le quattro pose già integrate. A terra e dopo il respawn la posa aerea viene disattivata. La pausa blocca fisica e fase del salto.

## Pulizia degli asset

- Sagome tracciate nel riferimento normalizzato a 240×160, senza deformare il personaggio.
- Tela trasparente di 56×56 pixel, ancoraggio dei piedi a (28,56); margine laterale per tutta la spada e correzione dell'ancora quando si guarda a sinistra.
- Esclusi esplicitamente i frammenti di roccia fra gli stivali; rimossi cielo ai bordi e componenti isolate di uno/due pixel.
- Alpha solo 0/255, nessun colore nascosto nei pixel trasparenti, nessun uso dei colori riservati all'interfaccia.
- Nessun watermark o overlay della registrazione dentro i nuovi asset. Sagome e colori restano approssimati perché derivati da video compresso.

`assets/jump_manifest.json` conserva hash del video, tempi, contorni, esclusioni e ancore. `tools/convert_jump.py --video PERCORSO` ripete l'estrazione; senza video ricrea il buffer GBA dalle PNG versionate. I primi ritagli respinti restano esclusi dalla ROM.

## Verifica

- Test con sanitizzatori: salita → apice → caduta in salti reali, entrambe le direzioni, atterraggio, uscita dalla piattaforma, rilascio del bordo, reset e game over.
- mGBA: tutte le pose aeree confrontate pixel per pixel nel framebuffer, compresi i pixel trasparenti contro lo scenario; controllo anche della spada durante il salto e del ritorno alla posa aerea.
- Ripetute le prove di collisioni, presa/risalita, danni, cadute, tre vite, game over, gemme, menu e impostazioni.
- `previews/jump_gameplay.gif` registra due salti consecutivi comandati con gli input del gioco. Tutti i fotogrammi acquisiti sono conservati, con gli stessi colori; solo ingrandimento intero nearest-neighbor e arrotondamento temporale imposto dal formato GIF. Nessuna interpolazione.

Questo aggiornamento completa un piccolo ciclo di animazione. Restano cinque inquadrature parziali del primo livello: i quattro mondi, i boss, l'interfaccia completa, le altre animazioni e l'audio separato non sono completati. **Avanzamento complessivo invariato al 9%**, stima ponderata e non misura del tempo rimanente.
