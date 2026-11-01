# Danno, cadute e Game Over

Collegata alla ROM una condizione reale di sconfitta: le cadute consumano energia, lo zero blocca la simulazione e apre GAME OVER; A/Start ricomincia azzerando il percorso, B torna al menu. Aggiunta API game_damage con saturazione, protezione temporanea dai colpi ripetuti e blocco delle azioni dopo la sconfitta.

I valori 3 punti iniziali, 1 danno da caduta e 60 aggiornamenti di protezione sono parametri provvisori del prototipo, NON statistiche originali dedotte dal video. La schermata Game Over è una nuova interfaccia del prototipo: non replica ancora il Continue osservato nel livello 3.

L’API di danno è pronta, ma nessun nemico visibile è ancora collegato: non è dichiarato un combattimento completo. Tutti i video del Mondo 1 restano il riferimento per mappa, avversari, animazioni e interfacce da integrare.
