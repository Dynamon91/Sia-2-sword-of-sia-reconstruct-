# Interfaccia di gioco — 6 novembre 2026

Rimosso il riquadro nero HP/L dalla scena giocabile. Quel riquadro era un
indicatore provvisorio della ricostruzione, non un elemento verificato nel video.
HP e vite restano attivi e sono consultabili nella pausa, con valori della
partita corrente. Le posizioni del contatore gemme, il ritratto dei dialoghi e
il cursore già ricavati dal video restano invariati.

La pausa resta una schermata provvisoria: non viene presentata come grafica
originale recuperata. Il comportamento originale dell'indicatore blu e della
salute non è ancora identificato. Non sono state inventate nuove icone da
attribuire al gioco originale.

La verifica dello sfondo in emulatore ora controlla anche la regione prima
coperta dal riquadro HP/L. Cadute, danni, game over e collisioni restano coperti
dalla prova completa della ROM.

Compilazione ARM7TDMI e prova completa mGBA superate. Screenshot acquisiti dalla
ROM: previews/ui_clean_gameplay.png e previews/ui_pause_stats.png. Hardware GBA
non verificato. Il lavoro è una correzione dell'interfaccia provvisoria, non la
ricostruzione completa dell'HUD originale.
