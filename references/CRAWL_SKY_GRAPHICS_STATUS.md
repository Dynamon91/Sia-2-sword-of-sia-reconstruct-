# Crawl passage sky repair

15 November 2026. The overall weighted completion estimate remains **16%**.
This corrects graphics in the existing seventeenth partial viewport and adds
no completed level content.

The earlier actor removal copied a registered 50-by-28 terrain rectangle from
the previous exposure. Lower-terrain registration does not register parallax
clouds, so the copied sky above the floor left a rectangular patch. The runtime
now replaces only its 50-by-18 sky region with a harmonic estimate constrained
by adjacent sky; floor colors are excluded from the fill. The recovered floor
at row 55 and below remains unchanged.

The recording-covered header sky and avatar sky use nearest sky-compatible
shared-palette colors, eliminating warm ordered-dither speckles. There are
4,424 repair pixels within a 240-by-55 bounding rectangle at shared-world
(790,176). A sparse mask leaves all other atlas pixels untouched, including
recorded roots and terrain. Both shared world banks and the registered source
background binary retain their previous hashes.

Opaque row runs have two aligned source copies for even and odd camera
positions. DMA transfers only those runs, with clipped edge pixels handled
separately; there is no extra framebuffer or full-world working buffer. The
encoded overlay is 9,712 ROM bytes. An initial dense scan caused missed native
updates and was replaced before delivery.

Local verification: GCC ARM 12.2.1, mGBA 0.10.5. Fifteen Python tests, including
four sky regressions, and seventeen sanitizer-enabled C programs pass. The
native suite checks all 588 intro frames, menu positions, controls, terrain
and sprite pixels, route traversal, pause, death and persistence. It also
compares the sparse overlay and unaffected world pixels with actual VRAM
beneath the roof and at the far exit. Scrolling records 6,115 updates in
6,115 active frames; the lower landing records 419/419 and the far passage
252/252. Fresh-core disk SRAM reopen checks pass.

Local ROM: 21,305,900 bytes, SHA-256
`9de56bf4e1fd3073e9d118f81796293c6aec392ff54f70fc9512b38907688418`.
GitHub CI is verified separately for the saved source commit.

The repaired sky is an estimate, not recovered original artwork. Upper-rock
joins and the extended hidden header still need reference-based refinement;
this milestone does not claim to remove every scenery seam. Intermediate thorn
motion/damage, the following route and complete levels remain unfinished.
Collision geometry is provisional and real hardware is untested.
