# Nuvole animate — prime due inquadrature

Aggiornamento del 7 novembre 2026, integrato nella build esistente.

## Cosa è misurato nel video

Analizzati 33 campioni del Mondo 1, livello 1, da 114,00 a 120,40 secondi. Il confronto della fascia di cielo libera da overlay misura uno spostamento verso sinistra di 6 pixel ogni 0,2 secondi durante il gioco: circa 30 pixel al secondo. Fra 115,20 e 116,80 secondi i campioni mostrano la stessa posizione delle nuvole durante il dialogo. L'errore medio di registrazione fra campioni rimane inferiore a 2 livelli RGB su 255.

Tempi, spostamenti ed errori sono conservati in `assets/cloud_manifest.json`, con l'hash del video. La ROM avanza di mezzo pixel per aggiornamento del gioco: a frequenza GBA nativa sono circa 29,86 pixel al secondo.

## Cosa è integrato

- Fascia di cielo superiore animata nelle prime due inquadrature, separata da rocce, alberi, gemme e personaggio.
- Fase condivisa fra le due inquadrature: lo scorrimento non riparte entrando nel ponte.
- Pausa, dialoghi e game over fermano il tempo attivo; il ripristino della partita azzera la fase.
- Due copie allineate della stessa texture consentono trasferimenti DMA anche agli spostamenti dispari, senza righe saltate o disallineamenti di un pixel.
- Conversione ripetibile dalle PNG versionate e, facoltativamente, dal video con `tools/convert_clouds.py --video PERCORSO`.

La prova nativa misura ancora 180 aggiornamenti del gioco in 180 fotogrammi emulati nella prima area. Tutte le 320 posizioni della texture sono confrontate con una composizione indipendente, compresi il ritorno all'inizio e la sovrapposizione dello scenario. Sono controllati anche la telecamera rialzata e l'ingresso nel ponte. I test precedenti di salto, attacco, presa al bordo, collisioni, cadute e game over continuano a passare.

`previews/scenery_gameplay.gif` contiene tre secondi continuativi registrati dalla ROM con il personaggio fermo. Il controllo del file verifica i colori originali di ogni fotogramma e la durata, senza interpolare immagini.

## Limiti precisi

Il tratto osservato dimostra il movimento e le soste, ma **non rivela il periodo completo originale**. La ripetizione di 320 pixel è una ricostruzione: le estremità, entrambe di cielo azzurro, vengono raccordate. Le prime 13 righe coperte dal banner e 3 righe con residui della compressione usano una continuazione sfumata stimata; altri piccoli punti occultati usano il cielo osservato più vicino. La parte inferiore viene raccordata al colore del fondale esistente con dithering, evitando un cambio netto di colore.

Non vengono copiati banner, loghi, gemme, personaggi o rocce nella texture delle nuvole. Il parallax completo, le nuvole inferiori e le animazioni degli scenari successivi restano da ricostruire. I quattro mondi non sono completati. **Avanzamento complessivo: 9% stimato**, invariato per questo miglioramento circoscritto.
