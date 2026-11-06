# Collisioni delle rocce — 6 novembre 2026

La terza area aveva soltanto un piano di appoggio: un salto mancato poteva
attraversare il lato della roccia. Ora il blocco destro (x=96, y=115 fino a
fondo schermo) ferma gli attraversamenti laterali. I due blocchi della quinta
area usano la stessa risoluzione dei lati.

Un salto da sotto non attraversa più il fondo dei tre blocchi solidi. L'urto
annulla la velocità verticale senza assegnare lo stato a terra, quindi non
consente un salto aggiuntivo in aria. Sotto la roccia il movimento rimane libero.
Gli appoggi dall'alto usano il passaggio fra posizione precedente e successiva;
il semplice contatto con lo spigolo non viene scambiato per sovrapposizione.

Questa modifica usa le superfici già tracciate nel progetto. I rettangoli sono
ancora approssimazioni: non certificano collisioni pixel-perfect rispetto al
video. Le sporgenze sottili, il soffitto irregolare della terza area, le altre
mappe, l'interfaccia e le animazioni complete restano da ricostruire.

Test CPU con ASan/UBSan: urti laterali, salti liberi sopra il bordo, atterraggio
alla massima velocità, contatto esatto/subpixel, urti inferiori, impossibilità
di saltare dopo l'urto inferiore, caduta e respawn. Tutti i test precedenti di
combattimento, vite, gemme e transizioni restano attivi.

Verifica ROM: compilazione ARM7TDMI e intestazione GBA riuscite. L'intera prova
mGBA passa, compreso un salto mancato provocato tramite input normali: urto
laterale, caduta, una vita persa, respawn e gemme conservate. Screenshot reale:
previews/cliff_side_collision.png. Risultati in COLLISION_TEST_REPORT.txt.
Hardware GBA e caricamento del file di salvataggio da disco non verificati.
