# Build senza intro — 1 novembre 2026

Modifica applicata alla revisione GitHub con cinque aree, due guardie, quattro gemme e cicli di camminata/attacco. Conservati questi sistemi; nessun ritorno alla v0.6.

Rimossi riproduzione INTRO, opzione INTRO, 588 fotogrammi e audio relativo dalla nuova ROM. Vecchi salvataggi con INTRO ON non riattivano il filmato. SOUND rimane persistente.

Rimossa la fascia superiore nera di 12 pixel dai nove fermi immagine del frontend; cursore del menu riallineato. Logo circolare escluso: la porzione nascosta è stimata estendendo la prima riga scoperta. Non è un recupero fedele dei pixel coperti. Gli sfondi giocabili già ripuliti restano invariati.

Verifiche: GCC ARM, intestazione GBA, test ASan/UBSan, audit posizioni e animazioni, mGBA per menu/salvataggio/opzioni, tre cadute/game over/retry, guardie/danno/attacco, cinque aree, quattro gemme e persistenza. Screenshot da ROM reale emulata. Hardware GBA non provato.

Restano da fare: mappe e boss completi dei mondi 1/2, animazioni integrali e scenari animati fedeli, interfaccia originale completa, ricostruzione accurata delle parti coperte. I PNG del mondo 2 sono riferimenti e non livelli giocabili. Nessuna percentuale globale è stimata senza un inventario completo dei contenuti.

Ricompilazione: python3 tools/unpack_assets.py; python3 tools/clean_frontend.py; python3 tools/repair_sprite_edges.py; make; ASAN_OPTIONS=detect_leaks=0 make test. Per le acquisizioni usare tools/frontend_check.c e mGBA.
