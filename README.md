# Lady Sia 2: Sword of Sia — GBA Reconstruction

Ricostruzione nativa per Game Boy Advance basata sui video di riferimento del gioco non pubblicato, registrati da Papacube. **Progetto in sviluppo.**

<!-- PROJECT_PROGRESS -->
![Avanzamento complessivo stimato: 16%](docs/progress.svg)

**Progetto completo: circa 16%** — stima ponderata, non misura del tempo rimanente. [Criteri e stato delle singole parti](docs/PROGRESS.md).
<!-- /PROJECT_PROGRESS -->

## Base del progetto: menu e intro verificati

**Il menu principale e l’intro ripulita costituiscono la base verificata da cui proseguire la ricostruzione.** Il ramo `main` raccoglie questa base insieme al percorso parziale del Mondo 1.

- **Menu:** PLAY, OPTIONS e CREDITS, con cursore alle coordinate native misurate nel riferimento: x=16, y=44/68/92. Navigazione, ritorno circolare e priorità di B durante l’annullamento sono verificati nella ROM.
- **Intro:** 588 fotogrammi a 240×160 e 6 fps, per 98 secondi, con audio. PLAY avvia il filmato; A mette in pausa/riprende; START passa al Please wait originale. Il termine naturale porta allo stesso caricamento.
- **Preferenze:** SOUND e INTRO si salvano in SRAM e vengono ricaricate dopo la chiusura e riapertura dell’emulatore.

![Menu principale: cattura reale della ROM verificata in mGBA](previews/menu_v06.png)

![Intro ripulita: testo e scena notturna acquisiti dalla ROM in mGBA](previews/intro_cleanup_comparison.png)

La barra e l’avatar della registrazione sono rimossi. I pixel osservati mantengono posizione e palette; le piccole zone coperte sono ricostruite dai bordi visibili e rimangono stime dichiarate. Le schermate OPTIONS, pausa e crediti sono ancora interfacce provvisorie.

La priorità è confrontare la grafica con i riferimenti e con catture reali della ROM, correggendo artefatti e posizioni errate senza alterare i pixel osservati. [Menu: misure e controlli](references/MENU_CURSOR_ALIGNMENT_STATUS.md) · [Intro: sorgenti, pulizia e limiti](references/INTRO_RESTORATION_STATUS.md).

## Stato del percorso giocabile

Sono collegate **17 inquadrature parziali del primo livello del Mondo 1**, con movimento controllabile, salti, prese ai bordi, collisioni provvisorie, cinque gemme, quattro guardie prototipo, danni, cadute, vite e Game Over.

La leva si attiva con A a terra nelle vicinanze e conserva lo stato durante il respawn. Dopo la discesa sul piano inferiore, Giù+sinistra permette di strisciare nel passaggio basso; Giù+destra torna indietro. Sotto il soffitto Sia resta bassa e si rialza dove c’è spazio. La camera segue il personaggio nello spazio comune alle viste.

Il livello completo, i boss, gli altri livelli e mondi, il movimento/danno delle spine e diverse animazioni restano da ricostruire. Geometria, dettagli coperti e alcune tarature della camera sono provvisori. Le musiche usano ancora la registrazione mista disponibile.

- [Leva e riscontro visivo](references/LEVER_VISUAL_STATUS.md)
- [Passaggio basso, controlli e riferimenti](references/CRAWL_STATUS.md)
- [Parete superiore e raccordi del fondale](references/UPPER_WALL_GRAPHICS_STATUS.md)
- [Cielo del passaggio basso: riquadro e puntinatura corretti](references/CRAWL_SKY_GRAPHICS_STATUS.md)
- [Camera e continuità delle viste](references/CONTINUOUS_CAMERA_STATUS.md)
- [Persistenza e recupero delle preferenze](references/SAVE_RELOAD_STATUS.md)

## Verifica e build

La pipeline [Validate GBA reconstruction](https://github.com/Dynamon91/Sia-2-sword-of-sia-reconstruct-/actions/workflows/validate.yml) esegue controlli delle sorgenti e degli asset, test con sanitizzatori, compilazione ARM7TDMI, regressione mGBA e riapertura del file SRAM. Il pacchetto `Lady-Sia2-GBA-build` viene pubblicato negli artifact solo dopo il superamento dei controlli.

La base di codice verificata nel checkpoint [99fe7d3](https://github.com/Dynamon91/Sia-2-sword-of-sia-reconstruct-/commit/99fe7d31fe1732919e91b709178c59e522a4f625) controlla **tutti i 588 fotogrammi presentati dell’intro**, le tre selezioni del menu e il percorso giocabile. [Esecuzione CI superata](https://github.com/Dynamon91/Sia-2-sword-of-sia-reconstruct-/actions/runs/43725681183).

Il pacchetto comprende la ROM, 115 screenshot reali, animazioni del gameplay, `TEST_REPORT.txt`, `BUILD_INFO.json` e checksum. I dati della build corrente si trovano nel suo artifact. **Hardware GBA reale non ancora verificato.**

## Controlli di base

| Contesto | Comando | Azione |
| --- | --- | --- |
| Menu | Su / Giù | Seleziona PLAY, OPTIONS o CREDITS |
| Menu | A / START | Conferma |
| Menu e opzioni | B | Torna indietro |
| Intro | A | Pausa / ripresa |
| Intro | START | Passa al caricamento |
| Gioco | Frecce, A, B | Movimento, salto e attacco |
| Gioco | START / SELECT | Pausa / menu |
| Gioco | R | Ripristina la partita di test |

Le capacità e i comandi provvisori specifici delle nuove sezioni sono descritti nei rispettivi documenti di stato.
