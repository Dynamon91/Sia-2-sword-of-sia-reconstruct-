# Recorded crawl roof header

15 November 2026. Overall weighted completion remains **16%**. This repairs
the existing crawl passage and does not add completed level content.

The later viewport's recording banner hides its first fourteen rows. Extending
row 14 upward had stretched the roots into vertical columns and cut a straight
edge through the upper rock. The new repair recovers **1,317 foreground pixels**
from the 185-second exposure, instead of inventing another rock outline.

Whole RGB patches are unreliable here because the clouds move independently
and root shapes repeat. The new exhaustive matcher scores only warm interior
foreground pixels, excluding target rectangles touching the banner or avatar.
Two disjoint source boxes agree on (+83,-63), independently confirming the
lower-terrain registration:

| Source box, x0/y0/x1/y1 | Foreground samples | Best RGB MAE | Runner-up RGB MAE |
| --- | ---: | ---: | ---: |
| 83 / 77 / 99 / 85 | 37 | 5.207207 | 11.873874 |
| 94 / 85 / 113 / 99 | 33 | 6.393939 | 13.424242 |

Each accepted patch requires at least thirty foreground pixels, error below
9/255 and runner-up separation above 3/255. A real repeated-root counterexample
is retained and rejected: it prefers (+51,-63), but errors 5.000000 and
5.646465 are too close to distinguish it from the correct occurrence.

Source rectangle (0,63,157,14) maps to the recording-covered target rectangle
(83,0,157,14). Warm and neutral dark source colors define the recovered rock
mask. Its pixels retain the exact indices of the registered lower-landing
asset. The remaining **881 sky pixels** are harmonic estimates, using a visible
clear-sky strip at x=100..131; old-exposure clouds are never copied. The patch
also clears the former stretched-root columns inside this hidden rectangle.
It changes no visible target pixels below row 14, no ground and no sprite.

The separate 4,672-byte overlay uses the existing sparse, parity-aligned DMA
format. The sky repair is drawn first and the recovered header second. Both
shared-world banks and the earlier sky repair stay byte-identical. This adds
ROM data without adding another world or framebuffer buffer in working RAM.

Local checks use GCC ARM 12.2.1 and mGBA 0.10.5. Nineteen Python tests pass,
including source-registration, rejected-ambiguity, exact-index and repair-bounds
checks. The full native suite verifies all 588 intro frames, menu, gameplay,
camera, controls, transparent sprites, death and persistence. The recovered
header and unaffected world are checked against actual VRAM beneath the roof
and at the far exit. Scrolling remains 6,115/6,115 active updates, including
419/419 in the lower landing and 252/252 in the far passage. Disk SRAM reopen
checks pass. GitHub CI checks the saved source separately.

Local ROM: 21,310,612 bytes. SHA-256:
`65d330b8e8bb353fafd516c9049795aa6b82641b5ec63977799fe5f185cc573b`.
`previews/crawl_roof_repaired.png` is an actual ROM capture.

Other unrecorded corners and joins, the header left of x=83, intermediate
thorn motion/damage and the subsequent route remain unfinished. The sky behind
the recording is still an estimate. Collision geometry is provisional and real
hardware is untested.
