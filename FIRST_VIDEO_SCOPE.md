# Obiettivo: ricostruire l’intero primo video

Priorità indicata dall’utente: percorso completo e contenuti del primo video come un unico obiettivo. Musica e separazione degli effetti rinviate. Le prove audio esistenti restano fuori dalla ROM.

## Blocchi del percorso da collegare

Gli intervalli seguenti servono a navigare il riferimento: non sono confini della mappa originale recuperati.

| Riferimento video approssimativo | Contenuti visibili | Stato della build |
| --- | --- | --- |
| 00:00–01:54 | Titolo, menu, storia e arrivo | Parziale; filmato INTRO rimosso su richiesta |
| 01:54–02:10 | Prima stanza, scala, gemme, piattaforma alta e primo ponte | Due aree già giocabili; geometria parziale |
| 02:10–02:45 | Dislivelli, combattenti armati, gemme, scale e altri ponti | Sei inquadrature parziali collegate, nuova salita/vuoto/avvio del ponte; percorso intermedio e scale da completare |
| 02:45–03:25 | Percorso verticale, sporgenze, indicazioni contestuali e combattimento | Da ricostruire e collegare |
| 03:25–03:55 | Scale, passaggi sotto piattaforme, oggetti e combattenti | Da ricostruire e collegare |
| 03:55–04:20 | Istruzioni per Water/Air/Fire e incontro con creatura quadrupede | Da trascrivere e implementare; non attribuire effetti senza verifica |
| 04:20–05:20 | Rami verticali, scale, piattaforme, creature volanti e combattenti | Da ricostruire e collegare |
| 05:20–06:00 | Risalita, oggetti sospesi, ultimi combattimenti e uscita | Da ricostruire e collegare |
| Circa 06:00–fine | Risultati: tempo, conteggi e valutazione | Da implementare con valori del gameplay, non copiati dalla partita video |

## Lavoro congiunto richiesto

- Mappa globale: identificare le zone ripercorse, registrare le traslazioni e collegare tutte le aree senza duplicare i ritorni come stanze nuove.
- Movimento e collisioni: terreno, scale, sporgenze, salti, cadute e transizioni coerenti lungo tutto il percorso.
- Entità: distinguere avversari, oggetti e figure interattive; ricostruire animazioni, colpi, danni e ricompense osservabili.
- Interfacce: vita e indicatori, gemme, dialoghi contestuali, istruzioni delle tecniche, pausa e risultati coerenti con lo stato reale.
- Progressione: rendere percorribile il tragitto completo prima di dichiarare completato il livello.
- Verifica: test di ogni collegamento e percorso dall’arrivo ai risultati, con catture della ROM compilata.

I fotogrammi in `reference/w1l1_reference.zip` sono riferimenti con timestamp, non scene già integrate né una mappa di collisione. Il video non consente di dedurre automaticamente contenuti nascosti, script completi o tutti gli esiti possibili. Nessuna percentuale di completamento inventata.
