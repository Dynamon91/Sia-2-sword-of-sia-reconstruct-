# Lady Sia 2 — prima ricostruzione musicale

Bozza automatica derivata dalla registrazione del primo livello già nel progetto: 251 secondi, 958 eventi di nota. Non è un recupero dello spartito, del driver o dei campioni originali.

- `preview_source_30s.wav`: primi 30 secondi della registrazione mista.
- `preview_harmonic_30s.wav`: stesso tratto con attenuazione delle componenti percussive. Può ancora contenere effetti di gioco; non è una soundtrack isolata.
- `preview_reconstruction_30s.wav`: stesse tempistiche, note stimate risuonate con nuovi timbri additivi.
- `level1_transcription_draft.mid`: trascrizione modificabile, non quantizzata. I 120 BPM sono soltanto una base temporale MIDI, non il tempo originale identificato.
- `level1_resynthesis_draft.wav`: prima risintesi completa, 251 secondi.
- `level1_harmonic_reference.wav`: riferimento armonico completo.
- `reconstruction_report.json`: metodo, hash sorgente, eventi e limiti.
- `file_validation.json`: controlli tecnici dei file, non giudizi di fedeltà musicale.

Servono correzione all’ascolto di note e ottave, ricostruzione di strumenti/percussioni e verifica del loop prima dell’integrazione GBA. La ROM continua a usare la registrazione precedente. Non sono stati ricostruiti titolo e intro. Nessuna fedeltà esatta è dichiarata.

Rigenerazione dalla radice del repository (NumPy e SciPy):

```sh
python3 tools/unpack_assets.py
OPENBLAS_NUM_THREADS=1 python3 tools/reconstruct_music.py assets/audio_level.pcm --out music
```
