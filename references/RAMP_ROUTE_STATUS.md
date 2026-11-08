# Percorso della rampa: undici inquadrature parziali

8 novembre 2026. **13% complessivo stimato**, rispetto al 12% precedente.
Due nuove inquadrature estendono il percorso giocabile del primo livello.
Il livello completo, gli altri mondi e i boss restano incompleti.

Dalla piattaforma superiore, camminare a sinistra: Sia attraversa la prima
nuova inquadratura, risale la rampa di legno e raggiunge l'isola della seconda.
Camminando a destra si torna alla piattaforma precedente; da lì rimangono
disponibili la quinta gemma e la discesa al percorso inferiore. Cadere a sinistra
dell'isola nuova consuma una vita e riposiziona Sia sull'isola, conservando gemme
e guardie sconfitte. Salto e pausa restano disponibili.

## Provenienza e limiti

I fotogrammi a 173 e 174 secondi provengono dal video originale W1L1 con SHA-256
`7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51`.
Due dettagli statici per coppia misurano (+58,-15) da 166 a 173 secondi e
(+108,+93) da 173 a 174 secondi. La conversione cerca tutte le traslazioni intere,
richiede concordanza fra i dettagli, errore RGB medio inferiore a 8/255 e margine
dal secondo risultato superiore a 3/255. I risultati e gli hash dei fotogrammi
sono in `assets/ramp_route_manifest.json`.

Le superfici di collisione sono provvisorie: la rampa è una pendenza attraversabile
dal basso, senza un volume originale recuperato. Il cielo occultato è stimato;
parti dell'isola e della rampa sono ripristinate dai fondali adiacenti tramite le
traslazioni misurate. Sia, indicatore gemme, banner e logo della registrazione
sono rimossi dal fondale giocabile. La piccola gemma visibile a 174 secondi è
rimossa e non è ancora un oggetto raccoglibile. Il salto verso il successivo
gruppo di isole e il nemico volante rimangono da implementare.

## Verifiche eseguite

- Dodici programmi C con AddressSanitizer e UndefinedBehaviorSanitizer superati
  localmente, inclusi quattro attraversamenti della rampa, salto, caduta, reset e
  respawn in tutte le undici aree (`ASAN_OPTIONS=detect_leaks=0 make test`).
- Conversione riproducibile di entrambi i fondali e registrazioni verificate.
- ROM GBA compilata con GCC ARM 13.2; prova frontend completa mGBA superata.
  La nuova sezione viene raggiunta e percorsa con i soli pulsanti. Verificati
  portali nelle due direzioni, arrivo sull'isola, pausa e ritorno al percorso
  inferiore senza perdita di vite, cinque gemme e tre guardie sconfitte conservate.
- La prova della caduta usa un ramo isolato con snapshot completo dell'emulatore;
  controlla vita consumata, HP ripristinati e respawn sull'isola. Poi ripristina
  lo snapshot per proseguire la regressione. Non scrive coordinate di gameplay.
- Riapertura SRAM con nuove istanze mGBA superata. Le anteprime provengono dalle
  catture reali della nuova ROM; il filmato della rampa non include il ramo isolato
  della caduta. La GIF del ponte termina prima della nuova escursione sulla rampa.

La percentuale è una stima ponderata, non una misura del tempo rimanente.
Nessun collaudo hardware effettuato; i risultati locali non vengono attribuiti
a GitHub CI.
