# Raccordi della parete superiore

15 novembre 2026. Stima complessiva invariata: **16%**. Questa correzione grafica
non aggiunge livelli o modifica le collisioni.

Il cielo di riempimento agli angoli dell'atlante interrompeva la parete con due
grandi rettangoli durante il salto verso la quinta gemma e la discesa. Le porzioni
senza riferimento vicino alla parete ora estendono il bordo della vista superiore.
Sono colori ricavati dal riferimento, ma i dettagli nascosti restano stimati.
Nessun pixel già coperto da una vista viene sostituito da questa estensione.

Fra le viste registrate del ponte, della parete e della rampa (aree 6–10), i pixel
visibili di un altro fotogramma hanno precedenza sui primi 14 pixel verticali
ricostruiti per rimuovere il banner. Sono sostituiti 6.524 pixel di intestazione;
questa priorità evita anche il taglio del bordo dell'isola superiore. La priorità
fra due porzioni osservate resta fissa. Il raccordo del cielo protegge il terreno.

La correzione rigenera entrambi i banchi del mondo e conserva le dimensioni ROM
degli asset. Il renderer e i buffer RAM restano quelli già usati dal progetto.
Il manifest espone 55.830 pixel di bordo esteso, di cui 27.209 protetti come parete.

Le regressioni statiche controllano la continuità della parete negli angoli esposti
dal salto/discesa e la conservazione di una porzione osservata. Il controllo mGBA
confronta anche i framebuffer del salto verso la quinta gemma e del ritorno con
l'atlante proiettato. I risultati effettivi accompagnano la build verificata.

Restano da rifinire gli altri raccordi del video, i dettagli coperti e la fedeltà
generale. Geometria e camera sono provvisorie; livelli, nemici e boss sono
incompleti. Nessun collaudo su hardware reale è dichiarato.

## Evidenza della build

GitHub Actions, esecuzione 43714120052 sul commit
`36b17ffca60f8dc2559797b82d8787efe4183c36`: pipeline completa superata.
Passano i due controlli statici della parete, la riproducibilità degli asset,
la compilazione nativa, la regressione mGBA e la riapertura SRAM. Il rapporto
include il confronto del framebuffer durante salto e discesa. L'intro mantiene
588 fotogrammi verificati, audio, pausa e passaggio al caricamento.

La ROM occupa 21.228.356 byte e produce 110 screenshot. SHA-256:
`4fe557cf2232356c6eb7d0362e278779f7f82c5ac3ec5342f05bead8252fdc0b`.
Le catture versionate `upper_wall_jump.png`, `upper_wall_descent.png` e
`upper_wall_landing.png` provengono da questa ROM. La preview di confronto
accosta due catture reali senza modificare i pixel di gioco.
