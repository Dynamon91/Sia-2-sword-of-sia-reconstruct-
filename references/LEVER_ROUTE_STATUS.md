# Zona della leva e quarta guardia

8 novembre 2026. **14,5% complessivo stimato**, rispetto al 13,5% precedente.
Due viste aggiuntive portano il primo livello a quattordici inquadrature parziali.
Il livello completo, gli altri mondi e i boss restano incompleti.

Dal ripiano alto dopo il salto fra le isole, proseguire a sinistra: due cambi
camera raggiungono la zona della leva. Una quarta guardia pattuglia la
piattaforma e può danneggiare Sia ed essere sconfitta con la spada. Camminando
a destra si ritorna al ripiano; una nuova visita conserva gemme e guardia
sconfitta. La parete sinistra impedisce di attraversare lo scenario. Un salto
mancato oltre il bordo destro della seconda vista consuma una vita e riposiziona
Sia nella stessa vista, conservando i progressi.

**La leva è ancora uno scenario statico.** Attivazione, barriera di spine e
percorso successivo non sono implementati. Nessun oggetto nuovo viene contato
come gemma: il totale del prototipo resta cinque.

## Provenienza e limiti

Fotogrammi a 175, 178 e 180 secondi del video W1L1 con SHA-256
`7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51`.
Due dettagli del terreno registrano (+118,+3) da 175 a 178 secondi; due dettagli
statici distinti della leva registrano (+44,+86) da 178 a 180 secondi.
Il convertitore cerca tutte le traslazioni intere, richiede concordanza,
errore RGB medio sotto 8/255 e margine dal secondo risultato sopra 3/255.
Hash, dettagli e risultati sono in `assets/lever_route_manifest.json`.

Guardia e giocatore sono rimossi dai fondali. Terreno coperto viene ripristinato
tramite le traslazioni misurate dalle viste adiacenti; cielo, banner e logo
occultati sono ricostruiti come stime. Il tratto di parete e roccia nel banner
rimosso deriva dal bordo visibile sottostante. Le collisioni sono provvisorie.
La quarta guardia usa lo sprite video già integrato della seconda guardia e
una pattuglia/IA provvisoria; non è una nuova animazione originale recuperata.

## Verifiche locali

- Quattordici programmi C superati con AddressSanitizer e
  UndefinedBehaviorSanitizer. Il nuovo test verifica i portali nei due sensi,
  la quarta guardia indipendente, sconfitta persistente, gemma conservata,
  parete solida, caduta/respawn, direzioni opposte e reset. Vite e respawn sono
  verificati in tutte le quattordici aree. Quattro test Python di registrazione
  e conversione riproducibile dei nuovi fondali superati.
- ROM compilata con GCC ARM 13.2.1. Suite frontend mGBA 0.10.2 completa superata.
  Un ramo parte da uno snapshot completo sul ripiano alto, raggiunge entrambe
  le viste con i soli pulsanti, sconfigge la guardia, mette in pausa, ritorna e
  rivisita. Conserva cinque gemme, quattro sconfitte e tutte le vite. Poi
  ripristina lo snapshot per proseguire la regressione precedente con tre
  sconfitte. Nessuna coordinata di gameplay viene scritta dal test.
- La verifica nativa delle nuove viste non viene confusa con la regressione
  principale: l'animazione della zona della leva mostra il ramo continuo prima
  del ripristino. La nuova caduta sul bordo è verificata nel test C; non viene
  presentata come prova input-only mGBA della nuova area.
- Riapertura SRAM con nuove istanze mGBA superata. Le otto animazioni vengono
  riesportate dai framebuffer nativi e controllate senza modificarne i pixel.
  Gli screenshot nuovi corrispondono alla ROM compilata in questa sessione.

Nessun risultato locale viene attribuito a GitHub CI o a hardware reale.
La stima ponderata aggiunge 0,25 punti ai sistemi e 0,75 al contenuto del Mondo 1;
non misura il tempo rimanente. Restano livelli, boss, leva/barriera, ulteriori
gemme e nemici, animazioni, interfaccia, audio e rifinitura delle collisioni.
