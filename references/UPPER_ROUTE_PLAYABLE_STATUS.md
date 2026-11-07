# Piattaforma superiore: nona inquadratura giocabile

8 novembre 2026. Nove inquadrature parziali del primo livello sono ora collegate. La stima editoriale passa dall'11% al **12%**: +0,5 punti al motore per salto alto e camera verticale, +0,5 al Mondo 1 per piattaforma superiore e quinta gemma verificati. Pesi invariati. Il livello e tutti i mondi rimangono incompleti.

Dalla parete dell'ottava inquadratura arretrare di qualche passo, poi premere **Su+A+sinistra**. Si atterra sulla piccola isola superiore. Dalla parte destra dell'isola saltare con **A+destra** verso la quinta gemma. La discesa riporta alla zona sottostante senza consumare vite. Il salto normale A mantiene la fisica precedente. Il salto alto Su+A è un comando **provvisorio** limitato alle aree 7 e 8: non è una ricostruzione certificata dell'abilità originale.

La nuova inquadratura usa il riferimento a 166 s, con registrazione (+35,+81) rispetto a 164 s e trasformazione inversa in discesa. Velocità verticale e raccolte sono preservate. Appoggi, rampa, volumi, soglie camera e altezza del salto sono provvisori; il tratto successivo lungo la rampa resta da implementare.

`tools/convert_upper_route.py --check` ricrea sfondo e cifra 5 da riferimenti versionati. La cifra 5 proviene dal video a 139 s. Parti dell'isola occultate dal personaggio vengono recuperate dal riferimento a 164 s; cielo, fascia superiore e parete occultati sono stimati. Il nemico volante è rimosso dallo sfondo e **non ancora implementato**. Il manifest esplicita questi limiti. Nessun banner o logo della registrazione è incluso nello sfondo giocabile.

`tests/test_upper_route.c` verifica salto normale, passaggio in salita, atterraggio, gemma con identità stabile, ritorno senza perdita di vite, mancata duplicazione della raccolta, respawn superiore e reset. Il test delle vite copre nove aree. mGBA raggiunge la nuova zona usando esclusivamente comandi, raccoglie la quinta gemma, verifica sfondo nativo, indice OBJ e dati VRAM della cifra 5, quindi torna attraverso le aree precedenti conservando gemme e sconfitte. Nessuna posizione o stato di gameplay viene iniettato.

La GIF `previews/bridge_run_gameplay.gif` registra continuamente combattimento sul ponte, parete, salita, raccolta, discesa e ritorno. PNG e GIF derivano dalla ROM compilata: nessun mockup, interpolazione o compositing del gameplay. Il confezionamento richiede un rapporto mGBA positivo e preview con hash della ROM corrente.

Hardware reale, animazioni complete, abilità originali, nemico volante, livelli e boss restano da completare. Audio e interfaccia sono ancora parziali.
