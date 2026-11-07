# Verifica della seconda visita alla piattaforma superiore

8 novembre 2026. Stima complessiva invariata: **12%**. Nove inquadrature parziali, cinque gemme e tre guardie; nessuna nuova area implementata in questo checkpoint.

Il controllo mGBA ora risale alla nona inquadratura una seconda volta attraverso i soli pulsanti, attraversa di nuovo la posizione della quinta gemma e torna alla zona inferiore. Verifica che contatore di gioco e progresso rimangano a cinque, che il numero OBJ del contatore rimanga quello della cifra 5, che vite e cadute non cambino e che la terza guardia resti sconfitta. Non scrive posizioni o stato di gameplay nella ROM.

Il confezionamento richiede anche il nuovo rapporto PASS della seconda visita: il precedente controllo della prima raccolta da solo non basta più. Corretto inoltre il messaggio del test delle vite: copre nove aree.

Verifica locale: undici programmi di test nativi con AddressSanitizer e UndefinedBehaviorSanitizer superati (rilevamento leak disabilitato per la compatibilità del runtime); quattro test Python di registrazione superati; conversioni riproducibili dei fondali sesta/nona area e ponte/parete e audit delle posizioni superati. ROM GBA ricompilata con GCC ARM 13.2; test frontend mGBA e riapertura SRAM con istanze nuove superati. 76 catture reali esportate. `previews/upper_revisit.png` proviene da questa esecuzione; la GIF del ponte include ora anche la seconda visita.

Questo checkpoint verifica i contenuti esistenti e non aumenta la percentuale. Collisioni, salto alto e ricostruzioni delle parti nascoste degli sfondi rimangono provvisori. Nemico volante, rampa successiva, livelli completi, mondi e boss, animazioni/audio completi e collaudo hardware restano incompleti. Nessun risultato di GitHub CI viene attribuito ai test locali.
