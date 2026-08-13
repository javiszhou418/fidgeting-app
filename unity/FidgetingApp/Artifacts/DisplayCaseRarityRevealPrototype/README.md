# Display-case rarity reveal prototype

This is an Editor-only, disposable visual study. It instantiates the existing
`PremiumDisplayCase.prefab` and `ThreeBladeDisplayPrize.prefab` read-only in an
unsaved preview scene. It does not replace a shipping scene, prefab, material,
model, runtime component, or prize asset, and it is excluded from device builds.

## Rarity study

| Product rarity | Demo color | Hex |
| --- | --- | --- |
| Standard | Blue | `#3399FF` |
| Refined | Green | `#33E094` |
| Signature | Purple | `#A35CFF` |
| Heirloom | Gold | `#FFA329` |

The neutral default case is preserved as a fallback. Rarity color is applied
with temporary `MaterialPropertyBlock` values to named renderer roles: fastener
caps and collars, graphite/velvet background, the recessed inner capsule, and a
weak acrylic rim/base tint that preserves transparency. Accent and light-pass
lights belong to the prototype only.

## Single-draw reveal

The six-second, 30 fps study follows this authored order:

1. Case back-facing (`0.00–0.80 s`)
2. Flip to front (`0.80–1.80 s`)
3. Prize readable (`1.80–2.70 s`)
4. Case parts explode (`2.70–4.10 s`)
5. Exploded hold and transition to prize-only (`4.10–4.45 s`)
6. Prize-only light pass (`4.45–5.75 s`), then completed hold

## Preview and evidence

- `default-and-rarity-contact-sheet.png`: neutral case plus all four rarity colors.
- `heirloom-gold-reveal-storyboard.png`: the six reveal beats.
- `heirloom-gold-single-draw-reveal.mp4`: complete short animation.
- `material-boundary-audit.json`: renderer-role audit and promotion boundary.
- `prototype-tests.xml`: isolated Unity EditMode result (2/2 passed).
- `prototype-generation.log`: isolated Unity generation log.

Raw frame sequences are intentionally omitted from this checked artifact.

## Interfaces required for a future shipping implementation

1. A data-only `RarityVisualProfile Resolve(GachaRarity)` source of truth.
2. A role-based `ApplyRarityVisual(profile)` presentation API that uses property
   blocks and never mutates shared materials.
3. Explicit `GachaRevealDirector` phases for back-facing, flip, readable,
   explode, prize-only, light-pass, and complete.
4. A `Begin(outcome, prizeNode)` entry point that keeps prize ownership with
   the caller and never edits the prize model.
5. A phase/progress callback to native UI for synchronization without moving
   animation timing into SwiftUI.
6. A neutral fallback profile and an acrylic-tint ceiling that preserves the
   physical case's transparent/material response.
