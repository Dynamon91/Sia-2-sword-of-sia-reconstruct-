# Ponte e parete: settima e ottava area giocabile

Aggiornamento del 7 novembre 2026. Il primo livello passa da sei a **otto inquadrature parziali collegate**, con una terza guardia prototipo. La stima complessiva passa dal **10% all'11%**: +0,5 punti al motore per la terza entità persistente e i nuovi volumi/collegamenti, +0,5 al Mondo 1 per l'estensione percorribile verificata. I pesi delle categorie non cambiano.

## Percorso disponibile

Dalla sesta area, raggiungere il ponte con A+destra e continuare a destra. Si entra nel tratto del ponte del riferimento a 161 s: la terza guardia può infliggere danno da contatto ed essere sconfitta con la spada. Proseguendo si sale sul terreno successivo e si entra nella zona a 164 s, fino alla parete. È possibile tornare indietro conservando gemme, vite e nemici sconfitti.

La parete ferma il personaggio e costituisce l'attuale limite della ricostruzione. Il percorso superiore e le azioni/tecniche successive non sono ancora implementati. Questo aggiornamento non completa il primo livello.

## Stato del prototipo

- I due collegamenti usano le registrazioni dei riferimenti: sesta→settima (−170,+9), settima→ottava (−168,+7), con trasformazioni inverse al ritorno.
- I piani di appoggio, le pendenze, i volumi e la parete sono **provvisori**. Sono verificati come percorso giocabile, non come collisioni originali recuperate. La parete arresta anche l'animazione di corsa quando non ci si sposta.
- La terza guardia ha identità persistente 2, due HP provvisori, pattugliamento e danno da contatto. Riutilizza lo sprite della prima guardia come prototipo. La sconfitta resta valida attraversando le aree e dopo il respawn; R ripristina tutte e tre le guardie.
- Le due nuove aree usano sfondi convertiti dal video. Terreno e parti del ponte vengono recuperati da inquadrature registrate. Cielo occultato, fascia superiore e piccole parti della parete sono stimati. Banner, logo e attori del filmato non fanno parte dello sfondo giocabile.
- Ponte, scenari e terza guardia non hanno ancora tutte le animazioni/comportamenti originali.

## Verifica

`tests/test_bridge_run.c` controlla i due portali in entrambi i sensi, il cammino continuo, la parete, combattimento/identità della terza guardia, persistenza dopo morte, cadute nelle due nuove aree e reset. Il test delle vite copre tutte e otto le aree.

Il test mGBA percorre il tragitto con input normali: ingresso sul ponte, spada contro la terza guardia, ingresso nell'ottava area, confronto di pixel del nuovo sfondo, contatto con la parete, pausa e ritorno completo. Controlla le traslazioni, quattro gemme conservate e tre nemici sconfitti. Non scrive posizioni o stati di gameplay dall'esterno.

`previews/bridge_run_gameplay.gif` contiene la registrazione continua della ROM nativa: combattimento, salita, parete, pausa e ritorno. Ogni fotogramma acquisito viene mantenuto nei colori originali, con sola fusione dei duplicati identici e temporizzazione GIF. Le PNG sono catture reali, non mockup.

## File e riproduzione

`tools/convert_bridge_run.py --check` verifica i due sfondi, la palette e i manifest dai riferimenti versionati. Il workflow GitHub esegue anche questa prova. La ROM include `bridge_run_background` e `riser_background` tramite `src/assets.s`.

Restano da completare il tragitto successivo, i livelli e i boss di tutti i mondi, le abilità, le altre entità, le animazioni, l'interfaccia e l'audio. Hardware reale non ancora collaudato.
