# Lady Sia 2: Sword of Sia — GBA Reconstruction

**🚧 WORK IN PROGRESS — Ricostruzione ancora in sviluppo.**

<!-- PROJECT_PROGRESS -->
![Avanzamento complessivo stimato: 9%](docs/progress.svg)

**Progetto completo: circa 9%** — stima ponderata, non misura del tempo rimanente. [Criteri e stato delle singole parti](docs/PROGRESS.md).
<!-- /PROJECT_PROGRESS -->

![Anteprima degli asset attualmente integrati](previews/readme_frontend.png)

Anteprima degli asset di titolo, menu e scene attualmente integrati, ripuliti dagli overlay della registrazione. Le zone originariamente coperte sono ricostruite e approssimate.

An ongoing reconstruction of Lady Sia 2: Sword of Sia for Game Boy Advance, based on the gameplay video references recorded by Papacube.

The current build includes a partial reconstruction of World 1 with controllable gameplay, collisions, pickups, damage, falling and game over. Levels, sprite and scenery animations, and the original interface are still being reconstructed and refined. This project is incomplete and does not represent the finished original game.

Latest playable change: three observed jump poses now follow rising, the apex and falling. The complete sword and foot alignment are preserved in both directions. Native mGBA checks compare the sprite and transparent background pixels, and cover landing, pause and airborne attacks. [Details and limits](references/JUMP_STATUS.md).

![Two jumps in both directions recorded continuously in mGBA](previews/jump_gameplay.gif)

Jump to catch the first-room rock ledges, then press Up/A to pull up or Down to let go. Four video-derived poses are integrated and tested. [Details and limits](references/LEDGE_STATUS.md).

![Ledge catch and pull-up recorded in mGBA](previews/ledge_gameplay.gif)
