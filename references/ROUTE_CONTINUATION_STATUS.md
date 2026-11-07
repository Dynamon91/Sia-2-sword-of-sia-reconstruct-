# Prosecuzione W1L1: registrazione del terreno fra 155 e 164 secondi

Aggiornamento del 7 novembre 2026. Le misure documentate qui preparavano il prossimo tratto. La sesta area è ora integrata con collisioni provvisorie: vedere `CONTINUATION_PLAYABLE_STATUS.md` (**10%** complessivo stimato).

Sono stati analizzati nove fotogrammi del video originale del primo livello. I riferimenti versionati hanno risoluzione 240×125: le prime 35 righe del fotogramma normalizzato 240×160 sono escluse, rimuovendo banner e logo della registrazione. Non sono sfondi pronti per il gioco: contengono ancora Sia, nemici, proiettili e indicatori del gameplay registrato.

## Misure ripetibili

Gli spostamenti descrivono un punto del terreno dal fotogramma di partenza a quello di arrivo, in pixel; y positivo indica il basso. Non sono velocità del giocatore o coordinate originali della mappa.

| Video, da → a | Δx | Δy | Esito |
| --- | ---: | ---: | --- |
| 155 → 157 s | −20 | 0 | Due ritagli del terreno concordi |
| 155 → 158 s | −140 | +8 | Due ritagli del terreno concordi |
| 158 → 159 s | −48 | +17 | Due ritagli del terreno concordi |
| 159 → 160 s | −54 | +34 | Due ritagli del terreno concordi |
| 160 → 161 s, vecchi ritagli | — | — | Respinti: includono cielo variabile |
| 160 → 161 s, pilastro statico | −116 | −25 | Due ritagli disgiunti concordi |
| 161 → 162 s | −24 | −1 | Due ritagli del terreno concordi |
| 162 → 163 s | −116 | +7 | Due ritagli del terreno concordi |
| 163 → 164 s | −28 | +1 | Due ritagli del terreno concordi |

`tools/audit_route_continuation.py` cerca ogni posizione intera possibile dei due ritagli di ciascuna coppia. Accetta una coppia solo se i due risultati concordano e ciascun errore medio RGB rispetta il limite dichiarato: 5/255 per i ritagli esistenti, 6/255 per i due piccoli dettagli del pilastro. Il pilastro richiede inoltre almeno 3/255 di distacco dal secondo miglior risultato. Il risultato conserva anche il secondo punteggio migliore, per rendere visibili le ambiguità. I ritagli sono scelti manualmente sul terreno, fuori da attori, cielo e interfaccia. Non è una ricostruzione automatica del livello.

L'audit verifica gli hash dei riferimenti e dei pixel. `manifest.json` conserva anche nome/hash del video, tempi e rettangoli in coordinate 240×160. `--video PERCORSO` verifica la provenienza dei pixel senza modificare i riferimenti. `--preview` genera una tavola di riferimenti etichettati; non genera una preview della ROM.

## Ripetere il controllo

```bash
python3 tools/audit_route_continuation.py --output build/route-registration.json
```

Richiede Python, NumPy e Pillow. La verifica opzionale dal video richiede anche FFmpeg e le dipendenze di `convert_room.py`. Il workflow GitHub esegue l'audit sui riferimenti versionati. `reference/w1l1_continuation/audit.json` conserva il risultato del checkpoint.

## Limiti e prossimo intervento

Il collegamento 160→161 s è ora misurato sul pilastro statico: due ritagli disgiunti di 6×8 e 7×7 pixel indicano entrambi (−116,−25), con errori medi 5,285 e 4,483/255 e secondi risultati rispettivamente 32,660 e 13,503/255. I vecchi ritagli restano respinti perché comprendono cielo e porzioni non stabili: non sono stati sostituiti silenziosamente con un esito positivo.

L'audit compone solo collegamenti accettati, calcola le traslazioni inverse e rifiuta cicli incoerenti. I nove riferimenti appartengono ora a un solo gruppo; dal riferimento a 155 s a quello a 164 s la traslazione composta è (−526,+41) pixel. Questa è una registrazione delle inquadrature, non una mappa di collisione. Quattro test automatici controllano catene, inversione, collegamenti respinti e cicli coerenti/incoerenti.

`reference/w1l1_continuation/bridge_alignment.png` mostra i due dettagli usati sui fotogrammi reali, con etichetta NOT ROM. L'incertezza dovuta alla compressione e alla normalizzazione rimane indicata nel manifest.

Il prossimo intervento è ricostruire la geometria percorribile e ripulire gli elementi dinamici. Il ponte, la zona coperta dai nemici, la geometria di collisione, le superfici in pendenza, gli oggetti e i comportamenti degli avversari richiedono ulteriori misure e ricostruzione prima dell'integrazione. La ROM contiene ora sei inquadrature parziali, con la prosecuzione integrata in forma provvisoria. Il percorso completo e tutti i mondi restano incompleti.
