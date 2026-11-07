# Sfondo della sesta area — integrazione provvisoria

Aggiornamento del 7 novembre 2026. Lo sfondo è ora **integrato nella sesta area giocabile** con collisioni provvisorie. La stima complessiva è **10%** dopo il traguardo descritto in `CONTINUATION_PLAYABLE_STATUS.md`.

## Contenuto

Il fotogramma a 159 s del video W1L1 è ripulito da Sia, effetto della spada, nemico sconfitto, indicatore delle gemme, banner e logo della registrazione. La roccia che era coperta viene recuperata dal riferimento a 160 s, usando la registrazione già controllata (−54,+34). Vengono copiati solo i pixel della componente di terreno: il cielo di sfondo si muove diversamente e non viene traslato insieme alla roccia.

Sono conservati esattamente **26271 pixel RGB** del riferimento al di fuori delle zone sostituite. **1899 pixel** appartengono al terreno recuperato. Il cielo occultato è una stima per interpolazione armonica dai bordi visibili; le prime 14 righe sono inizializzate dalla riga 14. Non è recupero dei pixel originali nascosti. Il manifest conserva le regioni interessate, gli hash delle fonti e il metodo.

## File preparati

- `assets/continuation_background.png`: RGB ripulito, 240×160.
- `assets/continuation_palette.bin`: copia tracciata della palette usata per il candidato; viene confrontata con la palette della stanza se disponibile.
- `assets/continuation_background.bin`: palette di 512 byte e 38.400 indici, formato previsto dal renderer; collegato da `src/assets.s` come `continuation_background`.
- `assets/continuation_background_gba.png`: decodifica degli indici con la palette del progetto, non una cattura dell'emulatore.
- `assets/continuation_background_preview.png`: la stessa decodifica ingrandita 3× senza interpolazione.
- `assets/continuation_visual_terrain.json`: contorni visivi della componente calda connessa dell'isola e del ponte/pilastro. Include esplicitamente `not_collision_geometry: true`.

La quantizzazione usa gli indici 1–239, senza occupare i colori dell'interfaccia. Solo il cielo stimato usa dithering ordinato fra due colori vicini, per ridurre le bande; terreno e pixel osservati mantengono il criterio di colore più vicino già usato nel progetto.

## Riproduzione e verifica

Dopo `python3 tools/unpack_assets.py`, eseguire:

```bash
python3 tools/convert_continuation_background.py
python3 tools/convert_continuation_background.py --check
```

Richiede Python, Pillow, NumPy e SciPy. Il controllo verifica identità del ritaglio con il riferimento versionato, traslazione dichiarata, dimensioni, palette, pixel non modificati e riproduzione dei PNG, del buffer e dei manifest. GitHub esegue `--check` dopo aver preparato gli asset esistenti.

## Lavoro restante

Le punte d'erba e i dettagli del ponte non definiscono automaticamente il piano su cui poggiano i piedi. I contorni sono una guida visiva, non una mappa di collisione recuperata. Piani percorribili, volumi solidi, vuoti, ancore dei piedi e passaggi avanti/indietro sono implementati in forma provvisoria e devono essere ulteriormente calibrati. Anche entità e animazioni del tratto restano da ricostruire. La build giocabile contiene ora sei inquadrature parziali.
