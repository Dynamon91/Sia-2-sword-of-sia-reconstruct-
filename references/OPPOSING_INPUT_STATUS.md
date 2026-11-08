# Opposing directions at area boundaries

8 November 2026. Overall completion estimate remains **13%**.

Holding LEFT and RIGHT together now cancels horizontal camera transitions,
matching the already cancelled player movement. Previously both direction
flags were accepted by the portal checks, so standing at the ramp thresholds
could change areas while the player was stationary. Every horizontal portal
now requires exactly one direction. Single-direction transitions still work
when the player reaches the screen clamp.

Validation: the new regression fails against the preceding game.c and passes
with the fix. It holds both directions for ten frames at six positions across
areas 8, 9 and 10 and checks unchanged position, area, ground contact and zero
horizontal speed. All twelve native C test programs passed locally with
AddressSanitizer and UndefinedBehaviorSanitizer, including normal round trips.

No new ARM compilation, emulator run or hardware validation was performed in
this session. Existing ramp previews depict the preceding build, not this fix.
The remaining gap, flying enemy, sixth collectible, complete levels, bosses,
visual refinement and audio remain unfinished. This correction does not add
completed level content or raise the weighted completion estimate.
