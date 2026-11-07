# Priorità del comando indietro nei menu

Aggiornamento del 7 novembre 2026. Avanzamento complessivo invariato al **9% stimato**.

## Errore riprodotto nella ROM

Con B+A premuti insieme nel menu principale, il codice prima usciva verso il titolo e poi eseguiva anche la conferma, avviando l'arrivo. La prova mGBA sulla build precedente attende il titolo (stato 0) e trova invece l'arrivo (stato 6). Nelle opzioni lo stesso ordine di elaborazione consentiva di modificare SOUND e SRAM dopo aver scelto di tornare indietro.

## Correzione

In MENU e OPTIONS, B viene elaborato prima degli altri comandi e termina immediatamente la gestione dello schermo per quel fotogramma. L'annullamento prevale quindi su conferma e navigazione: non avvia la partita, non sposta la selezione e non cambia le impostazioni. Questa è una regola deterministica della ricostruzione; non è presentata come una combinazione verificata sul gioco originale.

## Verifica

Il controllo nativo mGBA esercita B insieme ad A, START, SELECT e ciascuna delle quattro direzioni, sia dal menu principale sia dalle opzioni. Controlla la destinazione corretta, la posizione della selezione principale e SOUND/SRAM invariati. I comandi vengono inviati attraverso i tasti dell'emulatore; nessuna scrittura ai campi di stato del gioco.

`previews/options_cancel.png` è la cattura reale del ritorno al menu dopo la prova. Il confezionamento richiede `PASS menu cancel integration:` insieme ai controlli già previsti di gameplay, reset e riapertura del file SRAM. Il collaudo su hardware reale resta da eseguire.
