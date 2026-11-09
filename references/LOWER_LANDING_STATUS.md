# First landing below the lever

The route now has a sixteenth partial viewport. From the first post-lever edge,
walk right to about x=90 and release movement. The drop reaches the lower plane
at local x≈180 and y=118 (feet). This is a one-way descent in the current build;
the following left route and its return route are not yet authored. Walking off
the right edge still consumes a life and respawns on this lower landing. Gems,
defeated guards and lever state persist. The camera follows the same common
world; no black transition, teleport to a destination or loading effect is used.

The 183→185 video pair has two disjoint terrain samples agreeing on (+90,-105)
with strong best-match margins. They establish origin (-873,267). The older
182→185 registration remains rejected for its one-pixel disagreement; this does
not relax or average that audit. The player region is restored from the 186.1 s
frame through a second independent (+83,-63) terrain registration. Three edge
columns, the covered recording header and upper sky are estimates. Sky behind
the old tall thorns is estimated from nearby sky; transparent patch pixels
preserve the surrounding atlas and avoid a rectangular sky seam.

The lower floor y=118, its right edge x=192, the low rock and drop trigger
are provisional authored geometry, not a recovered original map. A low rock
volume stops leftward movement at x=164, before the
unimplemented crawling passage. The right landing is playable; the low passage
is not traversable with the current standing body. When the lever is open,
a shared-world patch displays the observed lower
strip pose from 185 s, replacing the earlier tall thorns. The final pose is
captured scenery; no intermediate thorn movement is inferred. Crawling,
thorn collision, intermediate thorn motion, the next leftward
section and a playable upward return are unfinished. They are not certified by
this landing. The current standing/walking poses are reused on the new plane.

Tests exercise exact subpixel world continuity and retained downward velocity,
landing, floor bounds, reset, deaths in all sixteen areas and persistent run
state. Native mGBA uses controller input for the drop, ground walking, pause,
pit and lower respawn; it checks the world framebuffer against the atlas. Its
host snapshot restoration only isolates the regression branch and is not a
player-accessible return feature. Hardware remains untested.

## Verified checkpoint

9 November 2026: weighted estimate 15.25% (previously 15%). One quarter point
is added for the connected partial landing, not for a complete level. Sixteen
sanitizer-enabled C programs, four Python registration tests, asset conversion
and position audits, native GBA compilation, full mGBA suite and disk SRAM
reopen pass locally. The suite samples 5,597 updates in 5,598 active scrolling
frames, including 153 updates in 154 frames in the new viewport. One presented
frame repeats; the test does not claim a perfect frame rate. Directional camera
samples: 2,026 right, 1,468 left, 1,810 idle. Ten motion exports retain every source RGB pixel.
There are 102 real ROM screenshots. CI for this new commit is not yet observed.
SHA-256 ROM: 021cbacf952e1339e58444b92fa881df1dd1ca36686f5661a932b4d4fc6e8608.
