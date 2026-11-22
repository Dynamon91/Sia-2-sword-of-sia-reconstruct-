# Avanzamento complessivo

**16.5% — stima editoriale ponderata, aggiornata il 2026-11-22.**

Non misura il tempo rimanente né la percentuale di pixel originali recuperati. I pesi sono una convenzione di pianificazione e potranno essere rivisti se cambia lo scopo. Un riferimento video archiviato non conta come livello implementato.

| Parte | Punti acquisiti / peso | Stato verificato |
|---|---:|---|
| Motore e sistemi di gioco | 9.25 / 15 | Controlli, combattimento con cinque guardie, vite/game over, camera continua e strisciamento verificati; ritorno dalla scala al tunnel senza scatti. Inizializzazione e interfacce non critiche spostate in ROM per compilare anche con GCC ARM 14. Geometria, IA e tempi ancora provvisori. |
| Mondo 1 e boss | 6 / 20 | Diciannove inquadrature parziali collegate: dal passaggio basso si raggiunge la quinta guardia e il piede della scala, con ritorno e sconfitta persistente durante la partita. Cinque gemme conservate. Salita della scala, percorso seguente, livelli e boss incompleti. |
| Mondo 2 e boss | 0 / 15 | Riferimenti disponibili; contenuti non integrati. |
| Mondo 3 e boss | 0 / 15 | Video indicizzati; contenuti non integrati. |
| Mondo 4, boss finale, finale e crediti | 0 / 15 | Video indicizzati; contenuti non integrati. |
| Fedeltà visiva, interfaccia, animazioni e audio | 0.25 / 15 | Menu, intro restaurata, pose aeree/risalita, nuvole e leva abbassata verificati nella ROM. Due nuovi fondali derivati da sei esposizioni del video; attori esclusi dai donatori. I pixel visibili dei nuovi fondali sono conservati fuori dalle maschere; cielo, parti coperte, piccolo frammento ripetuto della scala e raccordi restano stime dichiarate. Animazioni, barriera mobile, interfaccia e separazione audio incomplete. |
| Riferimenti, validazione e consegna finale | 1 / 5 | Riferimenti ricevuti fino al finale e test del prototipo; collaudo completo e hardware mancanti. |

Aggiornare docs/progress.json solo dopo risultati verificati, poi eseguire `python3 tools/update_progress.py`. Audio sperimentale non integrato e materiali di riferimento non equivalgono a contenuti finiti.
