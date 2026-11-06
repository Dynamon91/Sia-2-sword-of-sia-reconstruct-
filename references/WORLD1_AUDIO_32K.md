# Mondo 1 livello 1 — separazione da sorgente video

Prova a 32768 Hz, mono PCM16, estratta direttamente dal video tra 114 e 365 secondi: durata esatta 251 secondi. Evita il passaggio attraverso il PCM8 della ROM e il padding tecnico finale. Questo conserva più dettaglio in ingresso; non dimostra una migliore separazione percettiva.

Il pacchetto contiene mix sorgente, stima musicale, residuo completo e anteprime confrontabili. Stessa durata, stesso guadagno, nessun clipping, errore massimo della somma di 1 unità PCM16. Il residuo contiene ancora insieme effetti, ambiente e possibile musica. Qualità percettiva e loop da verificare; nessuna integrazione nella ROM.
