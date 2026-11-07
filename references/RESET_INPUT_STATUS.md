# Reset senza azioni involontarie

Aggiornamento del 7 novembre 2026. Avanzamento complessivo: **9% stimato**, invariato per questa correzione circoscritta.

## Errore riprodotto

Tenendo A (salto), B (attacco) o entrambi durante il ripristino della partita con R, il primo aggiornamento successivo trattava il tasto ancora premuto come una nuova pressione. `game_reset` azzerava infatti anche la memoria degli input precedenti. La prova aggiunta a `tests/test_game.c` fallisce sulla versione precedente.

## Correzione

Il percorso RESET continua ad azzerare la partita, ma registra i tasti già premuti come consumati. Salto e attacco richiedono rilascio e nuova pressione. Il movimento direzionale continuo mantiene il comportamento esistente; il reset resta disponibile anche dopo il game over.

## Verifica

- Test della logica con sanitizzatori: A, B e A+B tenuti durante e dopo il reset; nessuna azione automatica; salto e attacco nuovamente disponibili dopo il rilascio.
- Test della ROM in mGBA: R+A+B per 20 fotogrammi, posizione iniziale stabile, personaggio a terra, nessun attacco, tre vite; poi nuove pressioni per verificare salto e attacco.
- `previews/reset_held_actions.png` è una cattura reale della ROM durante questa prova.
- Il confezionamento richiede `PASS reset input integration:` oltre agli altri risultati già obbligatori.

Il tasto R è un comando di sviluppo della ricostruzione, non una funzione originale confermata dal video. Nessun nuovo livello o asset grafico viene dichiarato completato. Hardware GBA reale non collaudato.
