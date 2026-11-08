# Salto fra le isole dopo la rampa

8 novembre 2026. **13,5% complessivo stimato**, rispetto al 13% precedente.
Il primo livello ora collega dodici inquadrature parziali.

Dalla nuova isola della rampa proseguire a sinistra: la camera mostra il vuoto
fra due isole. Saltare a sinistra per raggiungere l'isola opposta; Su+A consente
di salire al ripiano superiore provvisorio. Dal ripiano, spostarsi a destra e
lasciarsi cadere sull'isola bassa, poi saltare a destra per tornare alla rampa.
Camminare nel vuoto consuma una vita e riposiziona Sia sull'isola di ingresso;
le gemme raccolte e le guardie sconfitte restano conservate.

## Provenienza e limiti

Il fotogramma a 175 secondi viene dal video originale W1L1 con SHA-256
`7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51`.
Due dettagli statici indipendenti registrano (+76,+44) dalla vista a 174 secondi.
Il convertitore ricerca tutte le traslazioni intere e richiede errore RGB medio
inferiore a 8/255 e margine dal secondo risultato superiore a 3/255.
Il manifest conserva hash, dettagli e risultati della registrazione.

Sia e spada sono rimossi dal fondale; l'isola coperta viene ripristinata dalla
vista precedente tramite la traslazione misurata. Cielo occultato, banner e
logo vengono ricostruiti come cielo stimato. Le superfici delle due isole e del
ripiano alto sono provvisorie e attraversabili dal basso. Le gemme visibili
sono rimosse dal fondale e non ancora raccoglibili: il prototipo conserva cinque
gemme. Il nemico volante e la vista successiva con la leva restano da integrare.
Nessun altro mondo o boss diventa completo con questa estensione.

## Verifiche

- Tredici programmi C superati localmente con AddressSanitizer e
  UndefinedBehaviorSanitizer; nuovo test con salti nei due sensi, ripiano alto,
  ritorno, input opposti, caduta e respawn. Quattro test Python di registrazione
  superati; conversione del nuovo fondale riproducibile.
- ROM GBA compilata localmente con GCC ARM 13.2.1. Suite frontend mGBA 0.10.2
  completa superata: la nuova area si raggiunge usando solo i pulsanti, senza
  scrivere coordinate. Verificati portale misurato, due salti sul vuoto, ripiano,
  ritorno, cinque gemme e tre guardie sconfitte conservate, nessuna vita persa.
- Il ramo isolato di caduta dopo la rampa ora verifica il respawn nella nuova
  area 11 e ripristina poi lo snapshot completo. La regressione continua sul
  percorso precedente. La verifica del ritorno sulla pendenza precedente tiene
  conto del singolo pixel di dislivello percorso prima del cambio camera.
- Riapertura SRAM con nuove istanze mGBA superata. Screenshot e animazione della
  nuova area sono catture della ROM compilata; le sette animazioni sono esportate
  dai framebuffer nativi e verificate senza alterarne i pixel.

Questi sono risultati locali, non una dichiarazione di GitHub CI o di collaudo
su hardware. La stima ponderata aggiunge 0,5 punti al contenuto del Mondo 1;
non misura il tempo rimanente. Restano da completare livelli, boss, animazioni,
interfaccia e audio e da rifinire le collisioni.
