# Intro ripristinata e pulizia grafica

PLAY avvia il filmato registrato: 588 fotogrammi, 240×160, 6 fps per 98 secondi. A mette in pausa o riprende, START salta direttamente alla schermata Please wait; al termine del filmato si vede la stessa schermata di caricamento.

La fascia della registrazione occupa 13 righe superiori; l’avatar copre il rettangolo `(208,13,32,18)`. La maschera precedente si fermava una riga troppo presto e usava come sorgente una riga ancora contaminata: restavano una barra grigia e righe verticali. La pulizia ora ricostruisce solo le zone coperte mediante continuazione dei colori RGB dai bordi visibili, poi sceglie i colori della stessa palette GBA. I pixel osservati mantengono coordinate e indici originali; il testo non viene spostato o stirato. I dettagli nascosti restano stime, non grafica originale recuperata.

Il flusso video usa blocchi GBA LZ77 indicizzati: il primo fotogramma è completo, i successivi sono differenze XOR dal precedente. Il buffer di lavoro rimane in EWRAM; l’emulatore confronta tutti i 588 fotogrammi presentati, inclusa la palette, con i frame puliti. Controlla inoltre che lo sfondo nero iniziale non contenga residui grigi indipendentemente dal riferimento generato. Sono acquisite dalla ROM anche la scena lunare, la sala e il ritratto. Il pacchetto include la ROM solo dopo i controlli mGBA di intro, comandi, passaggio al caricamento e dimensione massima GBA.

La versione SRAM v2 migra i vecchi record v1 con INTRO attivo e conserva la preferenza SOUND. Dopo la migrazione, INTRO può essere disattivata da OPTIONS.

La stima complessiva resta al 16%; mappe successive, animazioni mancanti, movimento/danno delle spine e hardware reale restano da completare o verificare.

## Verifica del 15 novembre 2026

GitHub Actions 43722516549, commit `d339dced348fd2cc74456d557755e76e4e0a3ac8`:
pipeline completa superata. I quattro test di pulizia coprono conservazione dei
pixel osservati, rimozione dei residui grigi, assenza di strisce verticali e
codec LZ77. La rigenerazione dai dati originali produce gli hash versionati.

Il collaudo mGBA osserva PLAY prima dell'avvio e verifica tutti i 588 fotogrammi
presentati, con audio, pausa e caricamento finale. Sono conservate le verifiche
del percorso, della parete superiore e della riapertura SRAM. Il pacchetto ha
113 catture reali della ROM; nessun test su hardware reale è dichiarato.

ROM: 21.298.836 byte. SHA-256:
`43a1fef41d9f15deb882dfd046d49e0a46dd6ff96f9a569475c2c7ad741d3e20`.
Le catture `intro_text_clean.png`, `intro_moon_clean.png`,
`intro_chamber_clean.png` e `intro_portrait_clean.png` provengono dalla ROM
verificata. La preview accosta le catture senza modificare i pixel del filmato.
