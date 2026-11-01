# Health and lives integration — 2026-11-01

Continues the five-area GitHub build after reference consolidation. The v07
life-loss behavior is now adapted to the existing enemies, animation clocks,
collectibles and progress system; no earlier source tree was substituted.

- Start with three lives and three HP (prototype values, not verified original balance).
- Enemy contact reduces HP, with 60 simulation frames of damage immunity.
- Lethal contact consumes one life and respawns in the current area with full HP.
- Falling consumes one life regardless of current HP or damage immunity.
- Respawn clears motion, attack and climbing, then grants 90 frames of immunity.
- Collected gems and defeated enemies survive a respawn.
- At zero lives the game freezes in Game Over. Retry resets the complete run.
- A compact HP/lives readout is visible. This is provisional HUD art.

Tests cover lethal damage in all five areas, pit/immunity interactions, preserved
progress, game-over freezing and reset. The emulator also exercises real guard
contact until a life is lost, respawn, subsequent sword combat, three fatal
falls, retry, and the existing five-area route.

No new levels or bosses were added. Full Worlds 1 and 2, complete animated scenery
and visual accuracy remain unfinished. Hardware GBA and disk save reload are
not verified. The new ROM is a test build, not a complete reconstruction.

Validation: ARM7TDMI build, all five ASan/UBSan CPU test executables and full
mGBA integration passed. See HEALTH_LIVES_TEST_REPORT.txt. The screenshot
previews/health_lives.png shows actual guard damage (HP 2, lives 3).
