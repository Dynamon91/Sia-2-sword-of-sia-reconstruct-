# Prosecuzione W1L1: registrazione del terreno fra 155 e 164 secondi

Aggiornamento del 7 novembre 2026. **9% complessivo stimato**, invariato: questo lavoro prepara il prossimo tratto, senza aggiungere aree giocabili o modificare la ROM.

Sono stati analizzati nove fotogrammi del video originale del primo livello. I riferimenti versionati hanno risoluzione 240×125: le prime 35 righe del fotogramma normalizzato 240×160 sono escluse, rimuovendo banner e logo della registrazione. Non sono sfondi pronti per il gioco: contengono ancora Sia, nemici, proiettili e indicatori del gameplay registrato.

## Misure ripetibili

Gli spostamenti descrivono un punto del terreno dal fotogramma di partenza a quello di arrivo, in pixel; y positivo indica il basso. Non sono velocità del giocatore o coordinate originali della mappa.

| Video, da → a | Δx | Δy | Esito |
| --- | ---: | ---: | --- |
| 155 → 157 s | −20 | 0 | Due ritagli del terreno concordi |
| 155 → 158 s | −140 | +8 | Due ritagli del terreno concordi |
| 158 → 159 s | −48 | +17 | Due ritagli del terreno concordi |
| 159 → 160 s | −54 | +34 | Due ritagli del terreno concordi |
| 160 → 161 s | — | — | Respinto: errore elevato e traslazioni non concordi |
| 161 → 162 s | −24 | −1 | Due ritagli del terreno concordi |
| 162 → 163 s | −116 | +7 | Due ritagli del terreno concordi |
| 163 → 164 s | −28 | +1 | Due ritagli del terreno concordi |

`tools/audit_route_continuation.py` cerca ogni posizione intera possibile dei due ritagli di ciascuna coppia. Accetta una coppia solo se i due risultati concordano e ciascun errore medio RGB è al massimo 5/255. Il risultato conserva anche il secondo punteggio migliore, per rendere visibili le ambiguità. I ritagli sono scelti manualmente sul terreno, fuori da attori, cielo e interfaccia. Non è una ricostruzione automatica del livello.

L'audit verifica gli hash dei riferimenti e dei pixel. `manifest.json` conserva anche nome/hash del video, tempi e rettangoli in coordinate 240×160. `--video PERCORSO` verifica la provenienza dei pixel senza modificare i riferimenti. `--preview` genera una tavola di riferimenti etichettati; non genera una preview della ROM.

## Ripetere il controllo

```bash
python3 tools/audit_route_continuation.py --output build/route-registration.json
```

Richiede Python, NumPy e Pillow. La verifica opzionale dal video richiede anche FFmpeg e le dipendenze di `convert_room.py`. Il workflow GitHub esegue l'audit sui riferimenti versionati. `reference/w1l1_continuation/audit.json` conserva il risultato del checkpoint.

## Limiti e prossimo intervento

Restano due gruppi separati di riferimenti: il tratto 160→161 s non va colmato con una traslazione stimata come se fosse verificata. Il ponte, la zona coperta dai nemici, la geometria di collisione, le superfici in pendenza, gli oggetti e i comportamenti degli avversari richiedono ulteriori misure e ricostruzione prima dell'integrazione. La ROM rimane limitata alle cinque inquadrature parziali già presenti. Il percorso completo e tutti i mondi restano incompleti.
