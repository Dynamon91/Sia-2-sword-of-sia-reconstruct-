# Sesta inquadratura giocabile — W1L1

Checkpoint precedente: il percorso è stato poi esteso a otto aree. Stato attuale in `BRIDGE_RUN_PLAYABLE_STATUS.md`.

Aggiornamento del 7 novembre 2026. Il percorso giocabile passa da cinque a **sei inquadrature parziali** del primo livello. La nuova zona usa lo sfondo preparato dal riferimento a 159 s e contiene una salita, il bordo dell'isola, un vuoto e il primo tratto del ponte. Non completa il livello né aggiunge il successivo tratto di combattimento.

## Comportamento implementato

- Proseguendo a destra dopo il secondo nemico si entra nella nuova area. La trasformazione della camera (−188,+25) è quella verificata dai riferimenti; movimento e coordinate si conservano attraversando il collegamento.
- Il ritorno a sinistra conserva la trasformazione inversa, le quattro gemme, gli avversari sconfitti, HP e vite. La seconda guardia è la stessa entità fra le due inquadrature, non un duplicato che riappare.
- La pendenza ha un piano di cammino provvisorio seguito in entrambe le direzioni. Il salto dal bordo raggiunge il ponte; per tornare occorre avvicinarsi al bordo del ponte prima di saltare a sinistra.
- I volumi dell'isola e del pilastro fermano gli urti laterali. Un salto mancato può causare una caduta: viene consumata una vita, con respawn nell'area e conservazione dei progressi. Tre vite esaurite portano al game over esistente.
- Pausa, ripresa, reset, salto e attacco mantengono i controlli già presenti.

## Collisioni provvisorie dichiarate

Il piano dell'isola passa per (0,123), (48,123), (64,113), (80,105), (104,101), (133,101). Il ponte usa il piano y=95 e il pilastro x=202..214. Sono valori di gameplay ricavati e regolati sullo scenario, non collisioni originali recuperate. I volumi sono semplificati; i dettagli dell'erba, del bordo roccioso e del ponte richiedono ulteriore calibrazione. Il ponte è percorribile ma non ancora animato.

## Verifica e anteprime

`tests/test_continuation.c` copre collegamento avanti/indietro, cammino sulla pendenza in entrambi i sensi, salto del vuoto e ritorno, urto contro il pilastro, caduta/respawn, assenza di risalita attraverso la roccia e guardia condivisa. I test delle vite includono ora tutte e sei le aree.

Il controllo mGBA raggiunge la nuova zona usando i normali input dal percorso esistente. Verifica la trasformazione del portale, campioni del framebuffer contro lo sfondo integrato, la salita, i due salti, la pausa e il ritorno con gemme e sconfitte conservate. Non vengono scritte posizioni o stati di gameplay dall'esterno.

`previews/continuation_gameplay.gif` registra il tragitto nella ROM nativa, senza interpolazione o fotogrammi inventati. Le catture `continuation_entry.png`, `continuation_slope.png`, `continuation_bridge.png` e `continuation_pause.png` provengono dall'emulatore.

## Stima complessiva

Questo traguardo porta la stima ponderata dal **9% al 10%**: +0,5 punti al motore per il supporto al piano inclinato e ai volumi della nuova area, +0,5 al Mondo 1 per l'estensione percorribile verificata. I pesi delle categorie rimangono invariati. È una stima editoriale, non una misura del tempo necessario per finire.

Restano il percorso completo, gli altri livelli e mondi, i boss, i comportamenti mancanti degli avversari, le animazioni degli scenari, interfaccia e audio da completare. Hardware reale non collaudato.
