# Camera continua e raccordi fra le viste

8 novembre 2026. **14,5% complessivo stimato, invariato.**
Questa correzione migliora le transizioni; non completa nuovi livelli.

La camera ora segue Sia in uno spazio comune alle quattordici viste. Il cambio
dell'area usata dalle collisioni non sostituisce più l'intera immagine e non
reimposta la camera. Sia, gemme e guardie vengono proiettate nello stesso spazio;
il loro spostamento rimane continuo nei portali della rampa, delle isole e della
zona della leva, anche nelle transizioni verticali e nei ritorni.

I ritorni ponte/scogliera e scogliera/prima guardia conservano inoltre la
posizione con precisione subpixel: sono rimossi i riposizionamenti fissi che
aggiungevano circa 10 e 8 pixel di salto nei due ritorni. Le traslazioni delle
prime sezioni della scogliera restano provvisorie, non misurate come i raccordi
successivi. Le collisioni e la geometria dei livelli non diventano definitive.

## Rendering e limiti visivi

Un atlante deterministico usa i fondali già ripuliti, con ordine di composizione
fisso indipendente dall'area di gameplay. Quattro banchi allineati consentono
copie DMA a 32 bit anche con camera spostata di uno, due o tre pixel. Il renderer
usa ARM in IWRAM; gli sprite vengono scritti a coppie, preservando trasparenza,
ritaglio e specchiatura. La camera non blocca i controlli durante lo scorrimento.
Pausa e dialoghi congelano il movimento; reset e respawn riposizionano la camera
intenzionalmente con la nuova posizione di Sia.

Le differenze del cielo fra fotogrammi video producevano rettangoli visibili
nell'atlante. Il convertitore raccorda solo il cielo vicino ai bordi delle viste,
proteggendo il terreno e le piattaforme tramite maschere. Il manifest registra
130.187 pixel di cielo riparati e verifica che i pixel di terreno protetti
rimangano identici. Questi raccordi sono ricostruzioni, non cielo originale
recuperato. Gli angoli non registrati estendono un profilo di cielo osservato;
restano soggetti a rifinitura visiva. Le nuvole delle prime due viste continuano
ad animarsi con i banchi e le maschere verificati.

## Verifiche locali

- Quindici programmi C superati con AddressSanitizer e UndefinedBehaviorSanitizer.
  Il nuovo test verifica i tredici raccordi nello spazio comune, la continuità
  subpixel delle quattro direzioni dei portali iniziali e il seguito camera
  indipendente dal numero dell'area. Quattro test Python di registrazione passano.
- Atlante, maschere e banchi DMA riproducibili con
  `python3 tools/prepare_scroll_assets.py --check`; palette condivisa verificata.
- ROM compilata con GCC ARM 13.2.1; suite mGBA 0.10.2 completa superata. Le
  posizioni dei fotogrammi effettivamente presentati sono controllate, comprese
  le pose della risalita e il fondale proiettato con confronto pixel per pixel.
  Tutte le 320 fasi delle nuvole iniziali rimangono verificate.
- Durante 1.512 fotogrammi attivi nelle aree 7–13 sono osservati 1.512 aggiornamenti
  presentati. I cambi di area attraversati mantengono passi camera entro sei pixel
  per asse e fotogramma, senza reset camera al portale. Questo è un risultato
  della sequenza locale provata, non una garanzia prestazionale su ogni situazione
  o su hardware reale.
- La regressione conserva salti, quattro guardie indipendenti, gemme, ritorni,
  rivisite, vite, game over, pausa e reset. La riapertura SRAM con nuovi core mGBA
  passa. Le otto animazioni sono riesportate dai framebuffer della nuova ROM e
  verificate senza modificare i pixel catturati.

Nessun collaudo hardware è dichiarato e questi risultati non sono attribuiti a
GitHub CI. Leva, barriera, percorso successivo, altri livelli e boss rimangono
incompleti; audio, animazioni e fedeltà visiva richiedono ancora lavoro.

Le GIF collegate documentano questa correzione; alcune PNG storiche restano
come riferimenti dei milestone precedenti. Il pacchetto usa le PNG generate
dal collaudo corrente, evitando di riutilizzare catture storiche.
