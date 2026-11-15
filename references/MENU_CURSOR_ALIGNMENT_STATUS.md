# Allineamento del cursore al menu registrato

15 novembre 2026. Stima complessiva invariata: **16%**.

Il riferimento UI del video a 8 secondi documenta l'origine del cursore a
(16,44), con un passo verticale di 24 pixel. Il renderer applicava ancora la
trasformazione del vecchio ritaglio 240x148 verso 240x160, portando le tre righe
a y=34,60,86. Il cursore appariva quindi 10, 8 e 6 pixel troppo in alto.

Il menu usa ora le coordinate native y=44,68,92, senza trasformazione. Il ritaglio
di riferimento del cursore, i suoi pixel, la palette e il fondale non cambiano.
Le coordinate derivano da `assets/ui_manifest.json` e dal ritaglio documentato in
`tools/convert_ui.py`; non sono una nuova posizione scelta visivamente.

Il controllo mGBA attraversa le tre selezioni tramite i comandi e confronta le
coordinate OAM con le misure del riferimento. Verifica tile, dimensione, cursore
unico e ritorno circolare con Su/Giù. Il pacchetto include tre catture reali del
menu. Le prove di annullamento simultaneo restano attive.

Le schermate OPTIONS, pausa e crediti sono ancora interfacce provvisorie. La
geometria dei livelli e le parti nascoste della grafica restano da rifinire.
Questo intervento corregge un errore misurabile e non completa nuovi livelli.
Nessun test su hardware reale è dichiarato.
