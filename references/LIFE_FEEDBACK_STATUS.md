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

This session did not compile a new GBA ROM or run mGBA: the ARM compiler and
mGBA development library are absent locally, and sudo installation is unavailable.
Existing screenshots and the Nine Areas Revisit Verified ROM predate this fix.
GitHub CI and hardware validation are not claimed. Nine partial viewports,
provisional collision geometry, missing flying enemy and next ramp, incomplete
worlds, bosses, animation and audio remain unchanged.
