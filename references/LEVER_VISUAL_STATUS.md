# Posa abbassata della leva originale

8 novembre 2026. **14,75% complessivo stimato**, da 14,5%: +0,25 punti
alla fedeltà visiva per il riscontro visivo dell'attivazione verificato.
Nessun nuovo livello diventa completo.

Il video W1L1 fornito ha SHA-256
7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51.
Il fotogramma a 182 s mostra la leva abbassata. Due ritagli statici indipendenti
misurano (-1,0) rispetto al fotogramma a 180 s; errore RGB medio sotto 9/255
e distacco dal secondo risultato sopra 3/255. Il nuovo riferimento viene
versionato, con hash e misure in assets/lever_pose_manifest.json.

Il renderer sovrappone una patch trasparente di 40×44 pixel alle coordinate
(64,104) dell'area 13, nello stesso spazio della camera continua. Le maschere manuali identificano le impronte delle due maniglie e i pixel
metallici. La posa abbassata usa pixel osservati a 182 s. Soltanto il cielo
prima nascosto dalla maniglia alzata viene stimato interpolando i colori
ai bordi dell'atlante corrente: usare il cielo di un fotogramma successivo
lasciava un'impronta visibile e quella variante è stata scartata.
Sono 362 pixel opachi quantizzati nella palette condivisa, indici 1–239;
zero è trasparente. Base della leva e terreno esterni alla maschera restano
quelli dell'atlante. La stima del cielo occultato resta una ricostruzione.
L'ordine di disegno conserva Sia davanti alla leva.

L'attivazione con B cambia tra due pose osservate. Non viene dichiarato
recuperato il movimento intermedio o il suo tempo originale. La barriera di
spine mobile e il percorso successivo restano da integrare; barrier_open è
ancora solo stato logico. Il raggio di interazione e le collisioni restano
provvisori. Reset e morte seguono lo stato della partita già verificato.

## Verifiche locali

- Convertitore riproducibile con --check; registrazioni, palette e dimensioni
  controllate. La copia del video coincide con l'hash originale.
- ROM compilata con GCC ARM 13.2.1. Suite mGBA 0.10.2 completa superata:
  il percorso a pulsanti attiva B vicino alla leva, allontana Sia e confronta
  ogni pixel opaco visibile della patch con il framebuffer nativo.
- 5.176 aggiornamenti presentati su 5.176 fotogrammi attivi delle aree 1–13
  nella sequenza provata. Controlli, combattimento, ritorni e reset conservati.
- Le otto animazioni sono riesportate dai framebuffer senza modificarne i pixel.
  Gli screenshot mostrano la ROM compilata. Risultati locali; CI del nuovo
  commit e hardware non vengono dichiarati superati in questa nota.
