# Primo bordo dopo la leva: quindicesima vista parziale

8 novembre 2026. **15% complessivo stimato**, da 14,75%. Il contenuto del
Mondo 1 acquisisce 0,25 punti per una vista parziale collegata e verificata;
non diventa completo un livello, un mondo o un boss.

Dalla seconda vista della leva, avvicinarsi a x circa 170 e saltare a destra.
Durante il salto si raggiunge il bordo della nuova vista; rilasciare il
movimento per atterrare sulla stessa isola. Da terra, andare a sinistra per
tornare alla leva. Proseguire oltre il bordo fa cadere Sia e consuma una vita;
il respawn avviene nella nuova vista. Gemme, nemici sconfitti e leva attivata
restano conservati. Non esiste ancora un attraversamento giocabile fino alla
striscia con le spine: il vuoto non viene sostituito con terreno inventato.

Il fotogramma originale a 183 s è registrato rispetto a 180 s con (-144,-8),
usando due dettagli disgiunti del terreno e controllo indipendente via 182 s.
La nuova origine nello spazio comune è (-963,372). Il cambio d'area mantiene
la posizione subpixel e non reimposta la camera. La posa abbassata della leva
resta proiettata nello stesso spazio e non viene disegnata sopra Sia.

Il fondale rimuove Sia dalla registrazione. Terreno coperto viene ripristinato
dalla vista precedente ripulita tramite la traslazione misurata; cielo ancora
occultato è stimato. Il tetto coperto da banner/avatar viene ripristinato dal
fotogramma a 184 s registrato con (-160,+32); il cielo superiore non ripreso
rimane stimato. Il manifest conserva sorgenti, registrazioni e limiti.

Il piano di cammino vicino al bordo segue un profilo provvisorio coerente
nelle due viste, con punti (184,149), (200,153), (216,155), (219,157) nella
vista della leva. Nella vista successiva usa esattamente la traslazione del
profilo precedente. Il volume del soffitto è un rettangolo provvisorio; radici
decorative e bordo superiore non diventano automaticamente piattaforme.
La geometria non è una mappa originale recuperata.

## Verifiche locali

- Sedici programmi C con ASan/UBSan: ingresso aereo, continuità del profilo e
  della posizione, atterraggio, ritorno, fianco/sottosoffitto, direzioni opposte,
  caduta/respawn, reset e persistenza. Vite verificate in tutte le quindici aree.
- Conversione del nuovo fondale, atlante e posa della leva riproducibili;
  quattro test Python di registrazione passano.
- Il test mGBA usa pulsanti per raggiungere la nuova vista, atterrare, mettere
  in pausa, cadere e ritornare alla leva. Verifica fondale e posa della leva
  contro il framebuffer nativo, senza scrivere coordinate di gameplay.
  La sequenza è isolata con uno snapshot completo dal percorso di regressione
  precedente; la sua GIF registra il percorso continuo, non il ripristino.

I risultati effettivamente eseguiti sono riportati nella consegna. Non vengono
dichiarati test hardware o CI del nuovo commit prima di osservarli. Striscia
con le spine, suo movimento, animazione intermedia della leva e seguito del
livello restano incompleti.

## Risultato del collaudo corrente

La suite locale termina con successo: 5.406 aggiornamenti presentati in
5.406 fotogrammi attivi nelle aree 1–14. I sedici programmi C passano,
compresa la continuità del piano di cammino condiviso. La riapertura SRAM
con nuove istanze mGBA passa. Le nove animazioni vengono esportate dai
framebuffer senza alterare i pixel; quella del nuovo bordo registra 269
fotogrammi nativi continui. SHA-256 ROM:
e02bb041122e3a7854e16a90043af3bb08a049c0644fa96263872b4b860cf3f0.
