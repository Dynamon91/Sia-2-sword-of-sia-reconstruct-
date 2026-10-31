# Verifica delle posizioni — v0.6

Ambito: due aree attualmente implementate, confrontate con il video fornito.
Non è una certificazione della mappa completa o dei collider originali invisibili.

| Elemento | Prima | Correzione v0.6 | Verifica |
| --- | --- | --- | --- |
| Ingresso al ponte | Sia forzata a (60,61) | Coordinate trasformate di (-152,+60), con frazioni e velocità conservate | Test di continuità in simulazione e mGBA |
| Ritorno alla prima area | Sia forzata a (208,0) | Trasformazione inversa (+152,-60) | Test del ritorno con gemme conservate |
| Piano di appoggio del ponte | Y=101 | Y=100, coerente con la piattaforma alta dopo il cambio di coordinate | Registrazione dell'isola e prove di atterraggio |
| Pose specchiate di Sia | L'ancora si spostava di un pixel | Origine corretta per mantenere l'ancora X=24 del fotogramma 48 px | Proprietà dell'ancoraggio verificata su tutta la larghezza dello schermo |
| Cielo durante la salita della camera | Fascia ripetuta e riempimento che allungavano le nuvole | Cielo superiore separato dal resto della scena | Catture prima/dopo e verifica dello sfondo a camera ferma |
| Ritratto, icona gemme, cifre e cursore | Coordinate derivate dai ritagli | Mantenute: (0,102), (95,11), (129,29), (16,44) | Test OAM e confronto visivo già conservati |

L'ingresso nominale passa da (60,61) a circa (73–74,60), a seconda della frazione
di posizione al bordo. Nel ritorno, la correzione nominale è di circa 24 pixel
rispetto alla posizione fissa precedente. Questi valori descrivono il prototipo,
non coordinate estratte dalla ROM originale.

La misura della stessa isola negli sfondi ha selezionato (-152,+60), con mediana
dell'errore assoluto RGB 5,67 su canali a 8 bit; la seconda ipotesi ha errore 13,33.
Questo è un confronto di colori per stimare lo spostamento, **non un errore di
posizione di 5,67 pixel**. Compressione del video e bordi antialias limitano la
precisione. Il campione e l'intervallo di ricerca sono nel JSON allegato.

La nuova composizione del cielo conserva tutti i pixel degli sfondi precedenti
quando la camera è a zero. Verificato prima nella conversione e poi direttamente
in VRAM in mGBA, escludendo il rettangolo di Sia e la gemma disegnata separatamente.
Le maschere e il cielo nascosto dietro gli oggetti sono stimati; la parallasse
completa originale non è stata recuperata. Il cambio fra viste resta discreto.

Tutti i contenuti già inseriti sono mantenuti. Le sezioni successive, la geometria
completa, gli NPC/nemici e il comportamento originale degli indicatori ancora
sconosciuti restano da ricostruire e verificare.
