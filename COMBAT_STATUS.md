# Primo nemico collegato alla ROM GBA

Quarta area ricavata dal video W1L1 a 145 s. Il ritaglio del guardiano è tracciato manualmente: una sola posa, non uno spritesheet originale recuperato. Sfondo coperto da Sia e dal nemico interpolato, palette condivisa con la prima area. Collisioni del terreno approssimate dalla vista.

Il nemico pattuglia, riceve al massimo un danno per ogni attacco distinto, lampeggia quando colpito e scompare alla sconfitta. Il contatore persistente impedisce il ritorno del nemico passando fra aree. Il contatto danneggia Sia con protezione temporanea; il danno letale usa il Game Over già implementato. Il ripristino ricrea il nemico e azzera la partita.

Valori provvisori: 2 colpi per il nemico, pattuglia 0,25 pixel per aggiornamento fra X140 e X210; 1 danno da contatto, 3 punti di energia per Sia. Non sono statistiche originali verificate. Animazioni nemico e attacco, IA completa, effetti e HUD originali restano da ricostruire.

La transizione dall’area a 127 s a questa vista a 145 s salta il corridoio intermedio non implementato: il percorso completo e continuo non è dichiarato ricostruito. Tutti i livelli e il boss del Mondo 1 restano nello scopo, ma non sono ancora giocabili.
