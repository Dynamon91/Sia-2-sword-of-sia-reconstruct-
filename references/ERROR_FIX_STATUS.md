# CI and lower-drop safety fixes

9 November 2026. Overall estimate remains 15.25%; these fixes add no level content.

The previous GitHub validation stopped at lever_pose_manifest.json. Adding the
lower viewport changed the complete world atlas hash, while the actual lever
patch binary and PNG were unchanged. The converter now records its sampled
40x44 atlas region and palette instead of the unrelated complete atlas. Exact
patch and manifest checks remain enabled. A regression mutates a distant atlas
byte and requires identical outputs, then mutates the sampled region and
requires a changed dependency fingerprint. CI runs this regression before the
existing lever conversion check.

A second error was reproduced in physics: moving left while dropping from the
post-lever edge could enter area 15 at x=162.75, inside the provisional low
rock ending at x=164. The drop portal now accepts only the safe footprint
x=[74,102) of the preceding viewport. A leftward miss stays outside the lower
rock, falls and respawns at the upper edge. The valid one-way descent and
subpixel world projection remain intact. C tests cover the missed drop, safe
boundary, death and persistence. The native regression exercises a leftward
miss using controller input, without writing gameplay coordinates.

The delivery includes exact test results and real captures from the rebuilt
ROM. Hardware is untested. Standing/crawling passage, moving thorn mechanics,
following route and complete levels remain unfinished; collision geometry is
still provisional. No new loading or zone cuts are introduced.
