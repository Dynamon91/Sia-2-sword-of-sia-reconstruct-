# Stato integrazione del livello completo

Aggiunto `src/level_progress.c`: stato condiviso per gemme, avversari sconfitti, vita, cronometro, checkpoint e conclusione. Gli identificatori restano stabili cambiando area, così il ritorno in una zona non può ricontare un oggetto. La capacità di 128 elementi per categoria è un limite tecnico, non il numero di oggetti osservati nel video. Vita iniziale e coordinate vengono passate dal chiamante; nessuna statistica originale è dichiarata recuperata.

Test host con ASan/UBSan: raccolta unica di tutti gli identificatori, ritorno fra aree, valori fuori limite, pausa, danno senza underflow, fine partita e reset.

Questo modulo è preparato e testato, ma non è ancora collegato alla ROM. Non introduce ancora nemici visibili, nuove aree, IA, danni del combattimento o schermata risultati. Serve collegarlo alla mappa e alle entità ricostruite dal video; non sostituisce il gameplay attuale. Musica rinviata come richiesto.
