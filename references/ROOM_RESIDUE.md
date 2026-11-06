# Pulizia del frammento nero nella prima area

Rimossi cinque pixel scuri alle coordinate x=56..60, y=114 dallo sfondo indicizzato della prima area. Erano rimasti nel ritaglio temporale del personaggio registrato. Il cielo coperto è stimato mediando i colori delle righe adiacenti e scegliendo il colore più vicino nella palette esistente.

La procedura è ripetibile e non modifica di nuovo i pixel già puliti. Le composizioni a telecamera ferma restano identiche al nuovo sfondo indicizzato. La correzione viene applicata anche durante la ricostruzione su GitHub, rigenerando i livelli dello scenario. La percentuale complessiva rimane al 9%.
