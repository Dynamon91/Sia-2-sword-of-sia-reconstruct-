# Pickup feedback after losing a life

8 November 2026. Overall completion estimate remains **12%**.

Losing a life now clears the temporary gem pickup notification. Previously its
timer survived a lethal hit or pit fall, so the pickup counter could still be
displayed after respawn. Collected gems and defeated enemies remain preserved.
The notification also clears on the final life, before the frozen game-over state.

Validation: all eleven native C test programs pass locally with AddressSanitizer
and UndefinedBehaviorSanitizer (`ASAN_OPTIONS=detect_leaks=0 make test`). The lives
test now covers notification cleanup after lethal damage in all nine areas,
pit respawn and final-life game over, while checking persistent progress.

The follow-up session restored GCC ARM 13.2 and mGBA 0.10.2 in a local directory
from verified Ubuntu package bytes. The ROM now compiles locally. A new mGBA
branch saves a complete emulator snapshot at the fourth pickup, walks into the
pit using controller input while the notification is active, then checks hidden
gem/digit OBJ slots, restored HP, four persistent gems and retained defeats.
It restores the snapshot before continuing the normal nine-area regression.
No gameplay coordinates or telemetry are written by this branch.
`previews/pickup_death_respawn.png` is a real capture from the new build.
The full frontend suite and fresh-core SRAM reload tests passed locally, with
77 exported screenshots and all five continuous animation sequences verified.
GitHub run 42426601076 also succeeded for the preceding gameplay-fix commit
afaa59c; that result does not validate the new test and packaging changes.

Animation reports now include the GIF byte count and SHA-256, and packaging
rejects mismatched bytes in addition to stale ROM provenance. GIF output is
written in bounded chunks and installed atomically before frame verification.

Hardware validation is not claimed. Nine partial viewports,
provisional collision geometry, missing flying enemy and next ramp, incomplete
worlds, bosses, animation and audio remain unchanged.
