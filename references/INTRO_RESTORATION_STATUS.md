# Intro ripristinata e pulizia grafica

PLAY avvia il filmato registrato: 588 fotogrammi, 240×160, 6 fps per 98 secondi. A mette in pausa o riprende, START salta direttamente alla schermata Please wait; al termine del filmato si vede la stessa schermata di caricamento.

La barra nera superiore e l’avatar circolare in alto a destra sono mascherati su tutti i fotogrammi. Le 148 righe osservate restano alle coordinate originali; non vengono stirate o ricampionate. La fascia superiore viene estesa dalla prima riga libera e la zona dell’avatar dalla riga sottostante libera. I pixel nascosti dalla registrazione sono stime e non sono presentati come dettagli originali recuperati. La grafica di gioco ai bordi rimane invariata.

Il flusso video usa blocchi GBA LZ77 indicizzati: il primo fotogramma è completo, i successivi sono differenze XOR dal precedente. Il buffer di lavoro rimane in EWRAM; l’emulatore confronta i pixel visibili con i frame puliti. Il pacchetto include la ROM solo dopo i controlli mGBA di intro, comandi, passaggio al caricamento e dimensione massima GBA.

La versione SRAM v2 migra i vecchi record v1 con INTRO attivo e conserva la preferenza SOUND. Dopo la migrazione, INTRO può essere disattivata da OPTIONS.

La stima complessiva resta al 16%; mappe successive, animazioni mancanti, movimento/danno delle spine e hardware reale restano da completare o verificare.
