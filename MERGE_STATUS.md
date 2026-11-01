# Existing-build consolidation — 2026-11-01

Baseline: `be562fd7f02f4f6ca500bb2f39272f1e0418a701` on `main`.
Compared against `Lady_Sia2_GBA_v07.zip`, SHA-256
`77cae906b5ca6c2147bdd58b8b8e84dcac0bf706d68fb6b5397b409a5e250835`.

The GitHub build is the continuing gameplay baseline. The v07 package contains
an earlier two-area implementation; copying its source over main would remove
three areas, two guards, animated gems, motion cycles and persistent progress.
No runtime source or gameplay asset was replaced with that older implementation.

Merged `reference/worlds_v07/`: ten supplied video contact sheets and their
timestamp/source inventory, covering World 1 and World 2 (four levels and one
boss each). These are reference material, not newly implemented levels.
Existing references remain intact.

Both builds remove intro playback and provide game over/retry. Their damage
models differ: v07 has separate three-life/three-HP counters; main uses the
existing three-health combat/fall model. The latter remains unchanged to keep
the current combat and tested behavior. The v07 damage model has not been merged.

Worlds 1 and 2 are still incomplete. Five partial W1L1 areas are playable;
complete maps, bosses and full visual fidelity remain outstanding.
This consolidation does not represent new gameplay content or a completed port.

## Verification in this session

ARM7TDMI compilation, four ASan/UBSan CPU test executables, position and
animation audits, and the full mGBA frontend integration test passed.
See `reference/worlds_v07/BASELINE_TEST_REPORT.txt`.
ROM SHA-256: `6826ac92c984ef004238de405d2d74152e09deeff5adff93370d0e6812729231`.
`previews/consolidated_build.png` is a fresh emulator capture.
Real GBA hardware and disk save reload were not tested.
