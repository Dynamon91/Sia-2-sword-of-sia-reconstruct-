# Salvataggio SOUND e INTRO su file e migrazione SRAM

Aggiornamento del 15 novembre 2026. La stima complessiva resta al 16%: il ripristino della sequenza non completa un livello né un mondo.

Le preferenze SOUND e INTRO sono registrate in una struttura SRAM v2 con checksum e scrittura a commit marker. I nuovi salvataggi e quelli non validi avviano con SOUND e INTRO attivi.

I record v1 creati dai build precedenti vengono migrati al primo avvio: SOUND conserva il valore salvato, INTRO viene riattivato perché il filmato è tornato disponibile. Il risultato viene scritto in v2; da quel momento INTRO può essere spento dal menu OPTIONS e la scelta viene mantenuta.

tools/save_reload_check.c usa un file SRAM temporaneo di 32 KiB e istanze mGBA separate. Verifica entrambe le opzioni dopo la riapertura con SOUND/INTRO spenti e accesi, quindi corrompe il checksum e controlla i valori predefiniti. build/options_disk_reload.png mostra il menu renderizzato dopo la riapertura.

Il workflow richiede il risultato PASS prima di includere il pacchetto. La prova hardware su cartuccia reale non è stata eseguita.
