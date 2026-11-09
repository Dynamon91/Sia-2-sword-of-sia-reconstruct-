# Low passage after the lever

On the lower landing, hold DOWN and LEFT to crawl beneath the rock. DOWN is
only needed to enter the low stance. Releasing it under the ceiling keeps Sia
low; jump and attack are suppressed there. At either clear end, releasing DOWN
allows standing without changing the feet position. The new seventeenth partial
viewport follows the lower strip to the left; move RIGHT with DOWN to return.
The far left boundary remains the current route limit, not a completed level.
The upward return to the original lever island is still not authored.

Two prone poses come from the supplied video at 185 and 186.1 seconds. They are
manually masked, mirrored without interpolation and quantized into the existing
palette, with zero transparent and UI colors excluded. The observed contact
point is seven pixels below the provisional walk plane in both exposures; the
same render bias is retained. The crawl speed is 208/256 pixels per native update (about 48.5 px/s),
estimated from the 53-pixel anchor displacement over 1.1 seconds. Hitboxes and
animation timing remain provisional. A 20-pixel body replaces the 40-pixel standing body only here.

The next viewport uses two independent lower-terrain registrations agreeing on
(+83,-63), producing common-world origin (-790,204). The actor region is restored from the prior exposure using lower-terrain
registration. Covered upper rock and sky are estimated from the visible edge;
lower-terrain tracking is not treated as proof of an upper-rock transform.
A reversible camera guide interpolates between the two observed camera origins
using world x and the normalized sprite anchor; it is not a recovered timed
camera script. All camera movement stays bounded to six pixels per update. The
left edge of the recorded view limits further camera panning.

After opening the lever, a precomputed world bank gives the later exposure
priority in its recorded rectangle, removing old thorns/rock that previously
covered it. Sky at the boundary is feathered; observed foreground is retained.
The earlier world bank is kept before activation. This uses 3.24 MB extra ROM,
not another full world buffer in working RAM. No old strip bitmap is drawn over this bank: that would reintroduce old
spike silhouettes. Aligned atlas DMA rows avoid the former per-pixel overlay
cost.

C tests cover lowered collision bounds, fixed feet, forced crouching, blocked
jump/attack, safe standing, both registered portals, return, pit respawn, reset,
area/air restrictions and the camera guide. Native mGBA uses controller input
to traverse and return, compares both poses in both directions against the
framebuffer (including transparent pixels), pauses and checks persistent gems,
enemies and lever state. The host snapshot only isolates this regression branch;
it is not a game teleport. Existing upper-drop safety checks remain enabled.

Intermediate thorn motion, thorn damage, the following route and complete
levels/bosses are unfinished. Collision geometry and camera guide remain
provisional. Hardware is untested. Current numeric results accompany the build.

## Local checkpoint evidence

9 November 2026: 16% weighted estimate, from 15.25% (+0.25 engine and
+0.5 World 1 partial-route content). Seventeen sanitizer-enabled C programs,
five Python registration/dependency tests, asset conversion checks, native GBA
build, full mGBA suite and disk SRAM reopen pass. Native scrolling records
6,115 updates in 6,115 active frames; new areas record 419/419 and 252/252.
Directional samples: 1,999 right, 1,473 left, 1,832 idle. There are 107 real
ROM screenshots and eleven lossless motion exports. The crawl sequence has
555 native frames (9,290 ms as GIF). This is local evidence; CI for the new
commit is checked separately, and hardware remains untested.
SHA-256 ROM: cd930064744af8bd034727122038ab06d016b7b2e0661917f506358b03979973.
