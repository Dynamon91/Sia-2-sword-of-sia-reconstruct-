# Presa al bordo e risalita — build di prova

La prima roccia del video W1L1 viene raggiunta saltando, aggrappandosi al bordo e tirandosi su. La vecchia salita continua con Su/Giù è stata sostituita da questa sequenza nella prima area.

- A: salto. La presa avviene durante la discesa se le mani raggiungono uno dei due bordi configurati.
- Durante la presa: Su oppure una nuova pressione di A avvia la risalita; Giù, Sinistra o Destra lasciano la presa.
- Senza input Sia resta appesa. La pausa congela la sequenza; il danno interrompe la presa.
- La risalita blocca movimento e attacco fino all'appoggio. Una breve attesa impedisce di riaggrapparsi subito dopo aver lasciato il bordo.

Quattro pose sono ricavate dal video a 120,72, 120,88, 120,96 e 121,04 secondi. Lo spostamento verticale della telecamera (7 o 11 pixel) viene compensato, mantenendo l'ancoraggio al bordo. La prima posa rappresenta la presa; le altre tre la risalita. Silhouette, finestra di aggancio e durata della sequenza sono stime di ricostruzione; non sono dati originali recuperati.

## Verifica

- Test CPU con AddressSanitizer e UndefinedBehaviorSanitizer: portata del salto, attraversamento del punto di presa, mancato aggancio fuori portata, sosta, rilascio, danno, atterraggio e secondo bordo.
- Prova mGBA tramite soli input: presa, sosta, pausa/ripresa, rilascio e risalita. Tutte le pose sono confrontate con i pixel del framebuffer della ROM.
- Test precedenti su cinque aree, gemme, combattimento, collisioni, vite e game over mantenuti.
- Asset: quattro fotogrammi distinti, indice zero trasparente, nessun uso dei colori riservati all'interfaccia e margini del ritaglio trasparenti.

## Limiti

La presa è configurata sui due bordi misurati della prima area. Non è ancora estesa alle altre mappe. Il gioco rimane composto da cinque viewport parziali del primo livello; gli altri mondi e i boss non sono integrati. Audio separato e animazioni degli scenari restano in lavorazione. Hardware GBA reale non provato.

La stima complessiva passa dall'8% al 9%: un punto della categoria motore/sistemi è assegnato alla presa e risalita ora integrate e testate. I pesi restano una convenzione di pianificazione, non una misura del tempo rimanente.
