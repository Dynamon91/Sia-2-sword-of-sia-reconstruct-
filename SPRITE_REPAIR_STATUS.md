# Sprite and backdrop repair

- Fixed opaque black guard pixels being converted into palette entry 1 (a light color). Opaque actors now use nearest colors only from entries 1..239; zero is exclusively transparent, and UI colors are excluded.
- Removed captured snow and sky from the outside alpha boundary of all four Sia poses and the running pose. Interior highlights are preserved; this is not recovery of original sprite sheets.
- Replaced the large flat guard-area patches with terrain observed at video 144s and 146s, registered to 145s by (-116,+12) and (+8,-21). Recording overlays and their upper white border are excluded from this backdrop.
- Asset repair runs after restoring the archived ROM assets, preventing the CI restore step from undoing fixes.
- Still incomplete: full walk/attack/enemy animation, exact parallax behind video overlays, full route and worlds. The guard remains a single pose and health/combat tuning remains provisional.

Validation: host gameplay/settings/progress tests with ASan/UBSan, opaque sprite palette audit, then compiled ROM integration and actual mGBA screenshots in CI. This is not a claim of zero defects or original-asset fidelity.
