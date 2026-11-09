# Authentic level-entry wait

The supplied World 1 Level 1 video contains a black entry wait with “Please wait”
at the bottom left. It is now used only when PLAY enters the level. The removed
intro movie stays excluded. Normal portals between the fifteen partial gameplay
viewports retain continuous camera movement and active physics.

At 30 source fps, frames [3211,3306) cover the wait: five black frames, 86 frames
with text, then four black frames. This is 95/30 seconds. Resampling to the GBA
refresh gives 10 + 171 + 8 = 189 native frames. The captured frame at 107.3 s
supplies the observed text pixels; recording overlay rows 0..45 are cleared.
The indexed asset has 153 exact GBA colors. Its manifest records source hashes,
intervals and scope. Reproduce with tools/convert_loading.py; --check rejects
asset or manifest drift.

The native emulator check compares all 38,400 displayed bitmap indices in each
phase and the full text palette, checks hidden objects and frozen game ticks,
and holds A/B/SELECT/START through the wait to test skip and input isolation.
The first arrival dialogue must still be selected after the wait.

No other gameplay-zone loading interval is certified by this change. Later
reference freezes can also be dialogues or pickups and must be reviewed before
adding waits. Collision geometry, camera easing and incomplete routes remain
provisional. Overall weighted completion remains 15%; hardware is untested.

## Local checkpoint evidence

Sixteen sanitizer-enabled C programs pass. The complete mGBA suite and disk
SRAM reopen pass. The wait traverses 189 timer ages; the native-frame observer
samples it 190 times (one repeat at presentation), within the three-frame
observation tolerance. All three phases and held-input checks pass. Camera
regression retains 5,406 updates in 5,406 active frames, with 1,967 right-anchor,
1,464 left-anchor and 1,701 idle samples. There are 98 real ROM screenshots.
SHA-256 ROM: 593fb5dd348cea8e2f24284d71511b0ddf24733423a7d6ac325bf1b16c3c1825.
CI of this change is pending until observed; no hardware claim is made.
