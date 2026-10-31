# Lady Sia 2 — ricostruzione GBA v0.6

Aprire `Lady_Sia2_v06.gba` in un emulatore GBA. Questa versione include titolo,
menu, introduzione, otto pagine di storia e **due schermate collegate del primo livello, con il primo ponte giocabile**. Non è ancora il livello completo o il gioco completo. Anche l'interfaccia resta
parziale: vita, indicatore blu inferiore e schermate non mostrate richiedono
ulteriori verifiche; non sono stati assegnati valori o significati inventati.

## Novità v0.6 — controllo delle posizioni

- Misurato lo spostamento del riferimento in comune tra i due sfondi: la stessa
  isola risulta traslata di -152 pixel X e +60 pixel Y nella vista del ponte.
- L'ingresso al ponte e il ritorno non riposizionano più Sia in coordinate fisse:
  mantengono posizione relativa, parte frazionaria e velocità. Il cambio di
  inquadratura è ancora discreto, non uno scorrimento continuo della mappa.
- Piano di appoggio del ponte riallineato da Y=101 a Y=100, coerente con il piano
  della piattaforma alta nella trasformazione osservata.
- Corretto il pixel di scarto dell'ancoraggio quando si specchia lo sprite di Sia.
- Separato il cielo superiore dal resto della scena: rimosso l'allungamento
  artificiale delle nuvole durante la salita della camera. Le zone nascoste
  dietro gli oggetti sono ancora stimate, non asset originali recuperati.
- A camera ferma, la composizione conserva esattamente lo sfondo precedente,
  con verifica dei pixel in VRAM al di fuori di Sia e della gemma dinamica.
- Separati passaggi tra le aree e riapparizione dopo una caduta: soltanto la
  riapparizione usa un punto di recupero fisso.
- Mantenuti tutti i contenuti del prototipo v0.5: menu, intro, otto pagine di
  storia, ritratto/dialoghi, popup gemme, audio, due aree, scala, ponte, raccolta,
  ritorno con gemme conservate, pausa e ripristino.

Il rapporto `POSITION_AUDIT_v06.md` descrive prove, coordinate e limiti. Il JSON
omonimo conserva la misura; `posizioni_prima_dopo_v06.png` mostra due confronti
tra catture reali della v0.5 e della v0.6. La mappa di collisione originale non
è recuperata: il confronto riguarda la geometria visibile delle aree inserite.

## Contenuto mantenuto

Titolo con grafica dal video e menu navigabile PLAY / OPTIONS / CREDITS, come
quello visibile a 00:08. Opzioni SOUND e INTRO, lettore della storia tramite
Select, schermata di crediti della ricostruzione e menu di pausa.

Le schermate OPTIONS, PAUSE e CREDITS sono nuove: il loro contenuto originale non è
stato verificato. Nel sorgente successivo alla v0.6, SOUND e INTRO vengono salvati in SRAM con controllo del record. La ROM v0.6 inclusa precede questa modifica: occorre ricompilare. Persistenza in emulatore e su hardware ancora da verificare.

## Limiti importanti del contenuto

Il livello è limitato a **due aree larghe 240 pixel ciascuna**, con un cambio
di inquadratura e movimento verticale limitato della camera. Il percorso dopo
il primo ponte, i nemici, gli NPC, gli altri oggetti, i combattimenti completi
e la conclusione del livello non sono ancora giocabili. L'attacco mostra una posa, senza applicare danno a nemici.
Il contatore mostra soltanto le due gemme implementate; non indica
il totale del livello originale.

L'intro usa 588 immagini indicizzate 240 × 160 campionate dal video, con il suo
audio. È una prima riproduzione da registrazione, **non una ricostruzione nativa
del motore delle scene**. Alcune sovrimpressioni di Papacube rimangono nelle
immagini del frontend/intro; non sono l'HUD del gioco. Nell'area giocabile sono
state sostituite da porzioni di cielo approssimate e dal nuovo contatore.

L'audio è PCM mono a 16.384 Hz dal video, riprodotto dal Direct Sound GBA.
Comprende anche gli effetti registrati nelle azioni di Papacube: questi effetti
non seguono le nuove azioni del giocatore. Non è una soundtrack isolata o
trascritta nei formati originali. SOUND OFF permette di disattivarla. La pausa
ferma e riprende il flusso audio della stanza. R ripristina le aree e le
gemme ma non riavvia la registrazione musicale. L'audio del titolo è un estratto
di 8 secondi senza loop ricostruito.

La lista `CONTENUTI_WALKTHROUGH.md` distingue contenuto implementato, materiale
presente solo come riferimento e lavoro ancora da svolgere. Non viene dichiarata
una percentuale affidabile dell'intero gioco a partire da un solo livello video.

## Comandi

| Schermata | Comandi |
| --- | --- |
| Titolo | A / Start: menu |
| Menu | Su / giù: scelta; A / Start: conferma; B: titolo; Select: storia |
| Intro | A: pausa/riprendi; Start: salta ai dialoghi di arrivo |
| Storia | A / destra: avanti; B / sinistra: indietro; Start / Select: menu |
| Dialoghi di arrivo | A / Start: prossima battuta, poi area giocabile; B: menu |
| Opzioni | Su / giù: scelta; A / sinistra / destra: cambia; B: menu |
| Crediti | A / B / Start: menu |
| Area giocabile | Sinistra/destra: muovi; A: salto; B: posa di attacco |
| Scala | Su: sali; Giù: scendi; A: salta dalla scala |
| Cartello | Giù nelle vicinanze: comandi; A / B: chiudi |
| Area giocabile | R: riparti e azzera le gemme; Start: pausa; Select: menu |
| Pausa | A / Start: riprendi; B / Select: menu |

Per provare subito il gameplay: dal menu entrare in OPTIONS, impostare INTRO
su OFF, tornare a PLAY e avanzare le due battute con A. Salire sulla scala centrale per prendere la
prima gemma, saltare sulla piattaforma alta a destra e proseguire verso il bordo
destro per raggiungere il ponte. Dall'isola del ponte, camminare verso sinistra
per tornare alla prima area.

## Compilazione

Inclusi codice C/ARM, convertitori e tutti gli asset binari incorporati nella
ROM. Per evitare una seconda copia degli stessi 29 MB, uno script li estrae
dalla ROM inclusa e ne verifica gli hash. Servono Make, Python 3 e GNU Arm
Embedded GCC con binutils arm-none-eabi-.
Non sono necessari newlib, SDK proprietari o ROM commerciali.

```sh
python tools/unpack_assets.py
make
# Oppure:
make PREFIX=/percorso/arm-none-eabi-
```

Output: `build/sia2_lab.gba`; nel pacchetto è anche presente come
`Lady_Sia2_v06.gba`. La ROM resta sotto 32 MiB. Il linker copia circa 6 KiB di
codice in IWRAM all'avvio, con stack separato, e mantiene gli asset in ROM.

Rigenerazione degli asset (richiede ffmpeg, Pillow, NumPy, SciPy e DejaVu Sans
Mono, più il video fornito dall'utente):

```sh
python tools/convert_walkthrough.py '/percorso/al/walkthrough.mp4'
python tools/convert_room.py '/percorso/al/walkthrough.mp4'
python tools/convert_bridge.py '/percorso/al/walkthrough.mp4'
python tools/convert_ui.py '/percorso/al/walkthrough.mp4'
python tools/convert_layers.py
make -B
# Controllo indipendente della registrazione tra gli sfondi (Pillow e NumPy):
python tools/audit_positions.py
```

Lo script unpack_assets.py non richiede il video, Pillow o altri pacchetti.
I convertitori del video usano 0:v:0, non la copertina PNG del contenitore. I manifest in
`assets` specificano timestamp e approssimazioni. Il filmato originale non è
duplicato nel pacchetto.

## Verifiche

```sh
ASAN_OPTIONS=detect_leaks=0 make test
# Con header e libreria mGBA installati:
gcc -Wall -Wextra -Werror tools/frontend_check.c src/game.c -lmgba -o build/frontend_check
./build/frontend_check build/sia2_lab.gba
```

- GCC ARM 13.2.1; checksum e intestazione GBA verificati.
- Test su PC con ASan e UBSan: terreno, salto, scala nei due versi e salto dalla
  scala, raccolta unica/ripristino, piattaforme, camera, cartello e limiti.
- Test mGBA 0.10.2: percorso completo del frontend e azioni della prima area,
  compresi transito sul ponte, seconda gemma, ritorno con gemme conservate,
  riapparizione dopo caduta, fine dell'intro e termine dell'audio del livello.
  Verificate anche continuità delle coordinate nei due passaggi, ancoraggi delle
  pose specchiate, caricamento dei 6 KiB di tile OBJ, cursore,
  ritratto, le cifre 1/2 e la scomparsa del contatore. Conteggio esatto nel rapporto.
- Acquisizioni reali di schermate e campioni audio dall'emulatore. Le PNG sono
  ingrandite senza interpolazione; non sono mockup o immagini generate.
- Nessuna prova su console GBA reale o flashcart. Il dato di prestazione da
  fermo non garantisce tutte le prestazioni su hardware reale o in scene future.

`STORIA_VERIFICATA.md` contiene la trascrizione parziale. Il font bitmap deriva
da DejaVu Sans Mono, con licenza allegata. Il gioco e la registrazione restano
dei rispettivi titolari. Riferimento principale: walkthrough W1L1 di Papacube
fornito dall'utente. Riferimenti tecnici: gbadev-org/gbadoc, gbafix di devkitPro
e API pubblica del core mGBA.

Interfaccia: riferimenti tecnici per OBJ/palette/mapping in https://gbadev.net/tonc/objbg.html e https://gbadev.net/tonc/regobj.html.

## Distribuzione GitHub

La ROM v0.6 è conservata senza modifiche in quattro parti binarie nella cartella `rom-parts`, per rispettare il limite di caricamento. Dopo aver scaricato ed estratto il repository, eseguire `python3 tools/unpack_assets.py`: ricompone `Lady_Sia2_v06.gba`, ne verifica SHA-256 e ripristina gli asset. Non serve il compilatore per questa operazione. La pipeline Actions pubblica inoltre la ROM ricompilata.

## Aggiornamento sorgenti: opzioni persistenti

Aggiunti salvataggio automatico di SOUND/INTRO e ripristino all’avvio. Record SRAM di 8 byte, versione, controllo dei valori e byte di verifica; dati assenti o non validi ripristinano SOUND ON / INTRO ON. Il marcatore di validità viene scritto per ultimo. È un formato della ricostruzione, non quello del gioco originale. Non salva progressi o gemme.

Test host con ASan/UBSan superati per tutte le quattro combinazioni, memoria vuota, corruzione di ciascun singolo bit e record non completato. Gameplay esistente ancora verificato dai test host. Non è stata eseguita una nuova compilazione ARM né una prova mGBA in questa sessione. Le ROM e le preview v0.6 incluse restano quelle precedenti.
