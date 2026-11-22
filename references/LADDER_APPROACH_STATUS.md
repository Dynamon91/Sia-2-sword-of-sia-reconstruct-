# Route from the tunnel to the ladder foot

22 November 2026. Overall weighted completion: **16.5%**. This adds two partial
views to the existing route, giving **19 connected views** and **five prototype
guards**. It does not complete the first level.

Continue LEFT after standing at the far tunnel exit. Defeat the next guard with
B and continue LEFT to the rock wall at the ladder foot. RIGHT returns to the
tunnel. The same guard is shared between both views: defeat, gems and the opened
lever survive return/revisit and life loss during the current run. R resets the
run. SRAM still stores SOUND/INTRO preferences, not level progress.

## Reference and graphics

The source video SHA-256 is `7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51`.
Six normalized video exposures (186.1, 187.5, 189.8, 190.5, 190.75 and 191 s)
provide the two backgrounds and their restoration donors. Five translations
are independently checked with two terrain patches each; the ladder rungs are
not used to infer camera motion. Low-contrast lower-strip pairs require an RGB
MAE below 5 and separation above 2 from the runner-up; the upper wall pairs use
separation above 3. Measurements are retained in the asset manifest.

| View | Origin | Observed RGB pixels unchanged outside repair | Registered replacements | Estimated pixels |
| --- | --- | ---: | ---: | ---: |
| ladder_hall | [-698, 204] | 28176 | 3337 | 6887 |
| ladder_foot | [-582, 261] | 31818 | 3984 | 2598 |

Actor and recording rectangles are excluded from every donor. Missing sky uses
harmonic fill without importing old parallax clouds. A small occluded right rail
fragment repeats two observed 11-pixel rung intervals (238 and 210 repair pixels
in the two source assets); it remains an estimate. Hidden header detail, the
clipped upper guard foot and remaining joins are also estimates. Repair masks
and source hashes accompany the converter. Shared palette conversion uses no
dithering. The fifth guard reuses an earlier recorded guard pose: its animation,
patrol and combat timing remain provisional.

After opening the lever, later route rectangles take priority in the world
atlas. The old tunnel sky/roof overlay is clipped where these later views expose
previously covered pixels. Otherwise it would draw straight header seams over
newly observed scenery. Runtime drawing still uses the existing aligned atlas
banks and sparse DMA runs, without allocating another framebuffer or world bank
in working RAM.

## Gameplay and verification

Provisional floor y=55 in the corridor translates to y=112 at the ladder foot.
The two portals translate by (+92,0) and (+116,+57), preserving fixed-point world
position in both directions. The rock wall begins at local x=132 in the final
view. A provisional reversible vertical camera guide reveals the lower shaft.
The obsolete x=-790 tunnel camera clamp has been removed: it caused a 35-pixel
jump on return from the new views. Camera motion remains bounded to six pixels
per update.

Local GCC ARM 14.2.1 and mGBA 0.10.5 checks pass: 18 C programs with address and
undefined-behavior sanitizers (leak detection disabled for this runtime), 19
Python tests, the asset converters, native ROM compilation, all 588 displayed
intro frames, existing gameplay, two-way new portals, fifth-guard combat,
persistent defeat, native background pixels, pause and return/revisit. Disk
SRAM reopening passes with fresh emulator cores. CI is checked separately from
these local results.

```text
Level performance: 180 logic updates in 180 emulated display frames
Scrolling performance: 6493 displayed updates in 6493 active scrolling frames
Area 1 performance: 1014 updates in 1014 active frames
Area 2 performance: 574 updates in 574 active frames
Area 3 performance: 734 updates in 734 active frames
Area 4 performance: 375 updates in 375 active frames
Area 5 performance: 504 updates in 504 active frames
Area 6 performance: 322 updates in 322 active frames
Area 7 performance: 278 updates in 278 active frames
Area 8 performance: 455 updates in 455 active frames
Area 9 performance: 48 updates in 48 active frames
Area 10 performance: 142 updates in 142 active frames
Area 11 performance: 466 updates in 466 active frames
Area 12 performance: 34 updates in 34 active frames
Area 13 performance: 288 updates in 288 active frames
Area 14 performance: 210 updates in 210 active frames
Area 15 performance: 419 updates in 419 active frames
Area 16 performance: 305 updates in 305 active frames
Area 17 performance: 103 updates in 103 active frames
Area 18 performance: 222 updates in 222 active frames
Directional framing: 2095 right-anchor, 1623 left-anchor, 1946 idle frames
```

ROM: 21,314,512 bytes. SHA-256:
`7410c6abd35384e574d11b1ab4e774b8c6a08824f717afce6d5b654a2b28206c`.

The GCC 14 build uses 27,928 of the linker's 28,672 IWRAM bytes. Cold reset/
respawn code and noncritical text interfaces execute from ROM, leaving the
active renderer and physics in IWRAM. This resolves the initial compiler-version
memory overflow without reducing assets or changing the loading timing.

`previews/ladder_foot_reached.png` and `previews/ladder_approach_gameplay.gif`
are actual native emulator captures of this ROM. No generated gameplay imagery
is used.

## Remaining work

The ladder is visible but cannot yet be climbed. The upper guard, upper route,
intermediate thorn movement/damage, remaining levels and bosses are unfinished.
Collision geometry, camera guide, covered scenery and animation timing still
need refinement against the video. Real GBA hardware has not been tested.
