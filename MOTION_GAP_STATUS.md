# Native motion, collectibles and fifth viewport

Implemented:
- Three distinct recorded running poses, sampled at W1L1 142.90, 142.95 and 143.05 seconds. The cycle runs only while moving on a surface; idle/jump/ladder states remain separate. Boot anchors are normalized after masking.
- Three recorded sword phases from 137.9, 138 and 138.2 seconds, normalized to right-facing. Attack direction is held for the swing. Damage is enabled only during the visible strike (ticks 8 through 4), once per enemy per swing.
- Fifth partial viewport from 155 seconds, connected to the existing guard scene with the measured foreground transform (-158,+18). Two island tops, a genuine gap, solid rock sides, fall damage and local respawn are active.
- A second independently tracked guard using its own recorded cutout. Prototype patrol/contact/sword behavior; the recorded ranged attack is not yet implemented.
- Four gems with stable IDs and persistence on revisits and falls. New gem placements are taken from the guard and gap scenes. The count is for this partial build, not the original video's full-level total.
- Native OBJ popup digits 3 and 4 extracted at 132.5/134 seconds, using the existing interface palette.

Validation:
- ASan/UBSan gameplay tests include phase-specific hits, both registered portal directions, a successful gap jump/pickup, a failed jump against the rock side, fall damage, and independent enemy/gem persistence.
- Animation asset audit checks buffer sizes, distinct poses, palette bounds, transparency and boot anchors.
- mGBA integration exercises the actual ROM, records every new walk/attack phase, checks native OBJ digit tiles, crosses the gap, defeats the second guard, falls and returns to the previous viewport.

Remaining limitations:
- This is five partial viewports of W1L1, not five complete levels. Existing earlier transitions still skip unreconstructed corridor sections. W1L2, W1L3, W1L4 and boss remain references, not playable levels.
- Compressed video poses with hand masks are not original sprite sheets. Exact animation timing and full enemy/ladder/hurt animations remain incomplete.
- Terrain hidden by recordings and original collision rules cannot be inferred perfectly. Upper sky overlays are approximated. New sign/energy-ball tutorial mechanics are not implemented.
- Music remains the previously integrated mixed recording; no separated soundtrack is claimed.
