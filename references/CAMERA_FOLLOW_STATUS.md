# Seguito della telecamera confrontato con il video

9 novembre 2026. **15% complessivo invariato.** Questa è una prima taratura
del seguito, non una dichiarazione di corrispondenza completa con l'originale.

La precedente fascia orizzontale 80–160 lasciava Sia vicino a x=160 quando
andava a destra. Nei riferimenti a 183 e 184 secondi Sia rimane circa nel terzo
sinistro dell'immagine: la camera mostra più spazio davanti alla direzione
di marcia. Ora il movimento verso destra porta gradualmente il riferimento
del corpo verso x=80; quello verso sinistra usa x=128 come stima iniziale.
La stima sinistra deriva da pose raccolte in camminata accovacciata e richiede
ancora controllo durante la camminata in piedi. Le annotazioni e le relative
tolleranze sono in CAMERA_FOLLOW_OBSERVATIONS.json.

Il seguito dipende dalla velocità effettiva, non dal solo tasto o orientamento:
Sia bloccata contro una parete e input opposti non fanno ruotare la camera.
Quando il movimento orizzontale termina, la camera mantiene l'offset corrente
entro i margini di sicurezza. Un movimento breve può terminare prima del
raggiungimento del punto di inquadratura. Inversioni, salti e portali conservano
un limite di sei pixel per asse e aggiornamento, senza riposizionamento della
camera al cambio di area. Tale limite e le soglie verticali restano provvisori;
velocità della fisica, easing e punti di arresto non sono dichiarati originali.

## Passaggi di zona e finto loading

Il numero dell'area serve alle collisioni; da solo non deve introdurre uno
stacco dell'immagine. Nelle quindici viste parziali attuali rimane lo spazio
continuo già composto. Non sono aggiunti stacchi neri o caricamenti arbitrari.
I passaggi di finto loading dell'originale dovranno essere annotati con i loro
fotogrammi, punti di attivazione e durata prima di essere riprodotti. Questa
modifica non rimuove né certifica sequenze originali non ancora integrate.

## Verifiche

I test C controllano convergenza verso i due punti di inquadratura, tenuta da
fermo anche cambiando orientamento, limite dei passi e quattordici trasformazioni
dei portali. La regressione mGBA osserva il corpo e la camera nei fotogrammi
presentati, contando i tratti in cui il seguito raggiunge i due punti e
verificando la tenuta orizzontale durante la sosta. Pause, ritorni e respawn
mantengono i rispettivi comportamenti già previsti.

I risultati effettivi sono riportati nella consegna. Non vengono dichiarati
test hardware o risultati CI del nuovo commit prima di osservarli.

## Risultati del checkpoint

Sedici programmi C passano con AddressSanitizer e UndefinedBehaviorSanitizer.
Suite mGBA 0.10.2 completa e riapertura SRAM superate. Nei campioni nativi
sono contati 1.967 fotogrammi assestati sul punto destro, 1.464 sul sinistro
e 1.701 soste con camera orizzontale ferma. Lo scorrimento conserva 5.406
aggiornamenti su 5.406 fotogrammi attivi nella sequenza provata.
Le nove animazioni sono riesportate dai framebuffer senza alterare i pixel.
Questi sono risultati locali; CI del nuovo commit e hardware non vengono
dichiarati verificati in questa nota.
SHA-256 ROM: 0e13be3c8d98fe6d8367b08bf9e8646ae736757cfbd4a922a32bced5e70373bf.
