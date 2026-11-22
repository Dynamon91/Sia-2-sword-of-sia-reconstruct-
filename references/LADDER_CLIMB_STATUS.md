# Ladder climb, mounted sword and upper platform

22 November 2026. Overall weighted project completion: **18%**. This is a partial reconstruction, not a claim of pixel-perfect completion or a finished level.

## Playable behavior

The route now contains **21 connected partial views**, six prototype guards and five gems. From the ladder foot, press UP to climb and DOWN to descend. DOWN also mounts the ladder from its upper platform. Release directions to stay attached. LEFT/RIGHT aim the mounted sword; B attacks. A jumps away; DOWN+A drops. The upper platform supports walking right into the next registered view and returning left. The subsequent floating-island route is not authored yet.

Four distance-driven climb poses and three dedicated mounted sword phases are extracted from the supplied video. A swing pauses vertical climbing. The sixth guard uses a captured pose, a provisional patrol and two-hit combat. Gems, defeated-enemy flags and the opened lever persist on revisit and life loss within a run; R starts a new run. SRAM stores SOUND/INTRO only.

## Source evidence and declared estimates

Original video SHA-256: `7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51`.

The converter checks thirteen registrations, each using two disjoint static patches; repeated rungs are not used to choose translations. Body masks exclude visible rungs, sky, floor and enemy hit stars. No generated artwork or enlarged sprite assets are integrated. The native shared palette uses opaque indices 1..239 and transparent zero.

| Transition | Measured translation |
| --- | --- |
| Foot to upper ladder view | (-30, +60) |
| Upper to next platform view | (-12, +31) |

| New view | Observed RGB pixels preserved | Registered foreground replacements | Estimated pixels | Derived ladder pixels within estimates |
| --- | ---: | ---: | ---: | ---: |
| ladder_upper | 27596 | 4253 | 6551 | 572 |
| ladder_upper_exit | 30069 | 3870 | 4461 | 0 |

Recording overlays and actors are excluded from each donor. Later jumping footage exposes the tower header; that donor is restricted to the tower. Missing sky uses a clear strip capped above terrain, avoiding a ground-colored smear. The lower approach also uses an additional 189-second exposure. Persistently hidden rung fragments reuse the cleaned lower view and remain estimates rather than recovered original pixels.

The blue floating object's behavior is not established or implemented; it is removed from static scenery. Patrol, collision profiles, sword reach, camera guide, animation timing and covered scenery still need refinement. Thorn movement/damage, complete levels, bosses and later worlds remain unfinished.

## Verified native build

Local validation passes: 19 C programs with address/undefined-behavior sanitizers (leak detection disabled for this runtime), 19 Python tests, deterministic asset/atlas checks, GCC ARM 14.2.1 build, mGBA 0.10.5 gameplay suite and separate disk-SRAM reopening.

The native test reaches the ladder through controller inputs, checks all four climb poses and all three mounted attack phases in both directions including transparent background pixels, defeats the sixth guard, walks the upper portals both ways, pauses while mounted, descends and jumps away without losing health or lives. Host snapshots isolate branches of the regression; they are not game portals.

All 588 displayed intro frames, menu cursor, original loading and earlier route regressions still pass. Terrain sampling, guard control and collection execute from ROM, keeping intro decoding, dialog rendering and blitting in IWRAM. Large transparent sword margins use exact per-row opaque bounds to avoid dropped logic updates.

```text
Level performance: 180 logic updates in 180 emulated display frames
Scrolling performance: 6940 displayed updates in 6940 active scrolling frames
Area 17 performance: 103 updates in 103 active frames
Area 18 performance: 403 updates in 403 active frames
Area 19 performance: 235 updates in 235 active frames
Area 20 performance: 31 updates in 31 active frames
Directional framing: 2103 right-anchor, 1632 left-anchor, 2040 idle frames
```

ROM: 21,364,000 bytes. SHA-256: `873af1b458ef484acb09145e4f91cc04272c8336cf37df20054b3675ee5ebd52`.
IWRAM code: 28,280 / 28,672 linker bytes; the 4 KiB stack reservation is retained. EWRAM background buffers are unchanged.

128 PNG captures and thirteen continuous lossless GIFs come from the compiled ROM. The exporter verifies every decoded GIF timing interval against its captured native RGB frame, including after lossless optimization.

Screenshots: `previews/ladder_climb_middle.png`, `previews/ladder_mounted_attack.png`, `previews/ladder_upper_arrival.png`, `previews/ladder_upper_exit.png`, `previews/ladder_descent.png`, `previews/ladder_climb_return.png`. Motion: `previews/ladder_climb_gameplay.gif`.

GitHub CI is checked separately after publication. Real GBA hardware is not yet tested.
