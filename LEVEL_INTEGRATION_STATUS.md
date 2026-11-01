# Stato integrazione

Lo stato condiviso è ora collegato a Game e alla ROM: gemme con identificatori persistenti, area e tempo attivo. Il ripristino azzera raccolte e tempo; pausa e dialoghi sospendono il conteggio perché non eseguono game_step. I campi gemme/collected precedenti restano adattatori per il renderer delle prime due aree.

I campi vita, nemici, checkpoint di recupero e conclusione sono ancora predisposizioni: non sono collegati a combattimento o progressione. La vita è inizializzata a zero e non mostrata; il cronometro è indipendente dalla vita, e il chiamante dovrà sospenderlo nello stato morte futuro. Il punto di recupero esistente usa ancora il comportamento v0.6.

Test host: raccolta e ritorno fra aree, coerenza contatori, reset, limiti. Aggiunte verifiche mGBA per pausa e contatori condivisi. Nuove aree, personaggi e risultati restano da integrare. Musica rinviata.
