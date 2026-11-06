# Animation movement control — 6 November 2026

Continues the saved five-area health/lives build at 62bca82778ddddfc0cca836655a66ab3ceac0a58.

Running animation now advances by actual subpixel movement after collision and
viewport clamping. Holding a direction at an outer wall no longer cycles running
poses while Sia is stationary. Partial final steps contribute their actual
movement. Turning preserves stride cadence; stopping, jumping and entering a
ladder clear the running phase. Normal running retains the existing three poses
and approximate six-frame cadence. Combat's existing visible hit window is unchanged.

The earlier ten-pose animation experiment was never committed or packaged and
was lost during workspace maintenance. This build does not include that experiment.
Jump, climbing and guard sprite expansions still need recovery/re-extraction from
the supplied video. Full levels, bosses, original timing and complete scenery
animation remain unfinished. No new playable areas or newly extracted poses are
claimed in this update.

Validation: all five CPU test executables pass with ASan/UBSan, including new
wall, partial-step, turn and ladder checks. Motion asset and position audits pass.
The ARM7TDMI ROM compiles and its GBA header verifies.

The full mGBA frontend test passed, including five areas, combat, death/retry,
settings persistence and the new wall-idle check. See ANIMATION_CONTROL_TEST_REPORT.txt.
previews/animation_wall_idle.png is a fresh screenshot from the compiled ROM.
Hardware GBA and disk save reload remain untested.
