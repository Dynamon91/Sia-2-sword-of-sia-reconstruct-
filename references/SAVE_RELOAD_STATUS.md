# Salvataggio SOUND su file e ripresa del progetto

Aggiornamento del 7 novembre 2026. Avanzamento complessivo invariato al **9%**: questa verifica non aggiunge livelli o animazioni.

## Verifica aggiunta

`tools/save_reload_check.c` avvia la ROM compilata con mGBA e un file SRAM temporaneo dedicato, di 32 KiB. Usa il menu del gioco per spegnere SOUND, chiude completamente il core e avvia una nuova istanza sulla stessa ROM e sullo stesso file. Controlla che SOUND rimanga spento e che audio e intro siano disattivati. Riaccende SOUND dal menu e verifica il valore dopo una nuova chiusura/riapertura. Infine salva di nuovo SOUND spento, corrompe il checksum sul disco e verifica che un altro avvio ripristini SOUND acceso e INTRO disabilitato.

La prova non usa uno stato rapido dell'emulatore e non sovrascrive i salvataggi personali: crea un file temporaneo distinto e lo elimina al termine. `build/options_disk_reload.png` mostra il menu effettivamente renderizzato dopo la riapertura con SOUND spento.

Il workflow GitHub esegue la prova dopo i controlli di gameplay. Il confezionamento richiede il relativo risultato PASS prima di dichiarare `disk_save_reload_tested: true`. Il test del reset e la prova di corruzione in memoria restano nel controllo frontend precedente.

## Compilazioni incrementali

Il Makefile genera e legge le dipendenze dei file C con `-MMD -MP`: una modifica a un header incluso indirettamente, come `level_progress.h` attraverso `game.h`, ricompila anche il frontend. L'obiettivo predefinito rimane la ROM completa.

## Ripristino

I sorgenti, gli asset versionati e i controlli vengono conservati nel repository. Da un checkout pulito il workflow ripristina gli asset incorporati, applica la pulizia, compila la ROM, esegue i test e produce il pacchetto `Lady-Sia2-GBA-build`. Ogni pacchetto riporta commit sorgente, hash ROM e checksum dei file. Per recuperare una versione collaudata, usare il commit e l'artefatto di un'esecuzione con esito positivo.

## Limiti

La prova copre file SRAM con nuove istanze del core mGBA, non l'hardware GBA reale, altre applicazioni emulatore, un processo interrotto durante la scrittura o la persistenza di avanzamento/vite. Il formato corrente memorizza le impostazioni; non salva la partita. Nessuna nuova scena o animazione viene dichiarata completata.
