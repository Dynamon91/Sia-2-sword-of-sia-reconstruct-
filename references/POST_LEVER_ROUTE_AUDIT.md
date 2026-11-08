# Raccordi dopo la leva: controllo prima della nuova mappa

8 novembre 2026. **14,75% complessivo invariato.** Nessuna nuova area
giocabile è aggiunta da questo checkpoint. La ROM valida resta quella
del commit dd380ecb.

Il video W1L1 fornito è stato verificato contro SHA-256
7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51.
Sono versionati i nuovi riferimenti a 183, 184 e 185 secondi, con hash nel
manifest. I fotogrammi a 180 e 182 secondi sono quelli già nel repository.

| Video, da → a | Traslazione in pixel | Risultato |
|---|---|---|
| 180 → 182 s | −1, 0 | Due dettagli statici concordi |
| 180 → 183 s | −144, −8 | Due dettagli del terreno concordi |
| 182 → 183 s | −143, −8 | Due dettagli concordi; chiude il triangolo precedente |
| 183 → 184 s | −160, +32 | Due dettagli disgiunti delle radici concordi |
| 182 → 185 s | −53, −114 oppure −53, −113 | Respinto: discrepanza verticale di un pixel |

Ogni ritaglio accettato ha errore RGB medio inferiore a 9/255 e distacco dal
secondo risultato superiore a 3/255. I due ritagli di ciascuna coppia sono
disgiunti. Il controllo verifica anche la composizione 180→182→183 contro
180→183. Traslazioni di dettagli video non equivalgono a spostamenti del
giocatore, collisioni recuperate o portali già giocabili.

La coppia respinta è importante: entrambi i dettagli superano da soli i limiti
di qualità, ma non concordano. Il convertitore non media né arrotonda la
differenza per ottenere un falso successo. Il rapporto conserva entrambi
i risultati e un controllo di regressione richiede che il caso resti respinto.
Resta da separare il movimento dei vari elementi dal seguito della camera
e completare la catena del tratto con le spine. Nessuna piattaforma mobile
viene trasformata automaticamente in terreno fisso.

Ripetere con `python3 tools/audit_post_lever.py --check`. Il workflow esegue
il controllo prima di compilare il gioco. Il rapporto completo è
`reference/w1l1_postlever/audit.json`; il convertitore non modifica la ROM.
Il controllo e la sua ripetizione locale sono passati. I due controlli GitHub
del precedente commit dd380ecb sono passati; nessun risultato CI viene
attribuito preventivamente al nuovo checkpoint.

L'anteprima è una tavola di riferimenti video, non una cattura di nuova build.
Mostra solo le righe 46–159 per escludere banner e avatar della registrazione.
I riferimenti integrali restano immutati per conservare misure e provenienza.
