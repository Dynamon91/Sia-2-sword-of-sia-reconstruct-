# Ripristino del motore e prototipo leva/barriera

Il commit eadca9a aveva sostituito src/game.c con sole due funzioni statiche.
Il motore completo viene ripristinato dal suo genitore, mantenendo lo stato
persistente aggiunto al ramo di lavoro.

La pressione di B viene calcolata una sola volta in game_step e passata alla
leva. Un pulsante già tenuto premuto non attiva la leva quando si entra nella
zona; salto e direzioni non la attivano. Il limite chiuso dell'area 12 risolve
l'attraversamento a x=130 in coordinate subpixel, senza riportare indietro
un personaggio già dall'altro lato. La leva è raggiungibile prima del limite.
Attivazione e apertura sopravvivono alla morte e alla rivisita; R cancella
lo stato insieme al resto della partita.

Questa è una riparazione del prototipo del ramo Copilot: posizione della zona
d'interazione e limite della barriera sono provvisori. Non sono stati recuperati
animazione della leva, grafica mobile della barriera o comportamento originale.
I fondali restano statici in questi elementi. Non viene aggiunto un livello né
incrementata la stima complessiva del 14,5%.

I test C coprono limite chiuso, attivazione, apertura, ritorno, rivisita,
morte/reset, pulsanti mantenuti, azioni fuori zona e assenza di riposizionamento
dal lato opposto. La regressione mGBA usa i pulsanti per raggiungere il limite
chiuso, premere B e attraversare prima di verificare guardia e ritorni.
I risultati eseguiti sono riportati nel messaggio di consegna; nessun collaudo
hardware viene dichiarato.

## Risultati locali

Quindici programmi C passano con AddressSanitizer e UndefinedBehaviorSanitizer;
quattro test Python passano. Atlante riproducibile verificato. ROM compilata
con GCC ARM 13.2.1; suite mGBA 0.10.2 e riapertura SRAM superate.
Sono osservati 5.060 aggiornamenti presentati su 5.060 fotogrammi attivi
nelle aree 1–13 della sequenza provata. Le otto animazioni sono riesportate
dai framebuffer nativi senza alterarne i pixel.
SHA-256 ROM: 3e8d63c3a05d0f3250666136b58b61ca1fc512c5c6b202fc9d021394f7ad6711.
Questi risultati sono locali, non risultati GitHub CI.
