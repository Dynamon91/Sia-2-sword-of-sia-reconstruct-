# Tentativo di separazione musica / effetti

Fonte: registrazione mono del livello già nel progetto, 251 s a 16384 Hz.

Si stima lo sfondo ricorrente confrontando finestre spettrali distanti almeno 5 s. Non è il recupero delle tracce originali. Non è solo una rimozione delle componenti percussive: cerca anche componenti ripetute, ma può comunque alterare batteria e strumenti.

## Ascolto

`comparison_source_music_residual.wav` contiene, nell’ordine: 15 s di sorgente, 0,5 s di silenzio, 15 s di musica stimata, 0,5 s di silenzio, 15 s di residuo, 0,5 s di silenzio. Lo stesso guadagno è applicato a tutte le versioni. La posizione precisa del passaggio è nel rapporto. I tre file `event_comparison_*` sono ascoltabili separatamente.

`preview_*_30s.wav` confronta invece i primi 30 s del livello. `music_background_trial.wav` contiene la stima musicale completa.

Sei coppie `candidate_*_source.wav` / `candidate_*_residual.wav` permettono di confrontare la registrazione con il suono candidato estratto, ciascuno di 0,9 s. Il residuo può contenere note o percussioni: nessun candidato è stato classificato come salto, gemma, attacco o altro. I timestamp nel video sono nel JSON.

## Verifiche e limiti

Controllati formato, durata, valori finiti, assenza di saturazione del file e identità numerica sorgente = musica + residuo prima della conversione PCM. Queste verifiche non misurano la qualità della separazione. I file non sono stati giudicati all’ascolto.

Gli effetti ricorrenti possono restare nella musica; i passaggi musicali unici possono finire nel residuo. Servono confronto con le azioni del video, rifinitura e verifica del loop prima dell’uso. Non sono stati integrati nella ROM.

Rigenerazione (NumPy, SciPy): `OPENBLAS_NUM_THREADS=1 python3 tools/separate_recording.py assets/audio_level.pcm --out music/separation_trial`.
