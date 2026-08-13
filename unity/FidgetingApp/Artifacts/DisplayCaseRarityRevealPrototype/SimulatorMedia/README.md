# Neutral display-case reveal media for the isolated Simulator demo

This directory contains a disposable, Editor-only media handoff. It does not
change the shipping display-case prefab, scene, runtime, prize model, catalog,
or gacha data chain.

## Recommended asset

- `display-case-neutral-reveal-540x720.mp4`
- H.264 High, yuv420p, 540 x 720, 30 fps, 180 frames, 6.00 seconds
- 293,558 bytes, about 391 kb/s, no audio, fast-start metadata
- Exact 3:4 frame; the 720 x 960 Unity source was uniformly scaled by 0.75

The six 900 x 1200 PNG files under `keyframes/` are the corresponding visual
beats:

1. 0.30 s — case back faces the viewer
2. 1.28 s — case flips toward the front
3. 2.25 s — prize is readable
4. 3.95 s — case parts separate while the prize remains intact
5. 4.90 s — only the recentered prize remains
6. 5.38 s — neutral white light pass completes

## No-stretch SwiftUI handoff

Use an `AVPlayerLayer` wrapper with `videoGravity = .resizeAspect` in a view
whose aspect ratio is `3 / 4`. This is the safest default and never changes the
model proportions. `.resizeAspectFill` is also non-distorting, but should only
be used when the containing card is itself 3:4; a wider banner will crop the
top and bottom. Never use `.resize`.

For a single-draw interaction, create one `AVPlayerItem`, seek to zero when a
draw begins, and play once. After playback ends, keep the final frame visible
or replace the player with `keyframes/06-light-pass-complete.png`. Do not loop
the shipping reveal. With Reduce Motion enabled, show
`keyframes/03-prize-readable.png`, then cross-fade to
`keyframes/05-prize-only.png`.

## Visual audit

- All 180 Unity source frames are exact 3:4 and were audited before H.264
  encoding.
- Minimum detected content margins at 720 x 960 are 58 px left, 62 px right,
  116 px top, and 104 px bottom. The most expansive frame therefore keeps at
  least 8% horizontal and 10.8% vertical clearance.
- The neutral readable frame has average saturation 4.34 versus 13.25 in the
  original gold prototype. The neutral light-pass frame has average saturation
  1.56 versus 2.56. White prize facets retain a small specular peak; the broad
  gold/orange color field is gone.
- `display-case-neutral-reveal-contact-sheet.png` is the review sheet.
- `neutral-simulator-tests.xml` records the isolated prototype tests: 2/2
  passed.

Generated from the isolated prototype menu command
`Fidgeting/Prototype/Display Case Rarity/Generate Neutral Simulator Media`.
The raw 180-frame sequence remains in the disposable isolation and is not
copied into the repository.
