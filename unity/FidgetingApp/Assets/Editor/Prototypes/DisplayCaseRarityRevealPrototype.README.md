# Display-case rarity reveal prototype

This folder is an Editor-only, deletable visual study. It instantiates the
existing `PremiumDisplayCase.prefab` and `ThreeBladeDisplayPrize.prefab`, then
uses temporary `MaterialPropertyBlock` values and prototype-owned lights. It
does not save a Unity scene, prefab, material, model, or runtime component.

Prototype mapping:

- Standard -> blue
- Refined -> green
- Signature -> purple
- Heirloom -> gold

The six-beat demo is: case back-facing, flip to front, prize readable, eight
case layers explode, only the prize remains, and a narrow light pass completes
the reveal.

Promotion boundary for a future shipping implementation:

1. Add a data-only `RarityVisualProfile` resolved from `GachaRarity`.
2. Add a role-based, property-block application API on the display-case
   presentation layer; do not duplicate or mutate shared materials.
3. Extend `GachaRevealDirector` with explicit flip, explode, prize-only, and
   light-pass phases while preserving caller ownership of the prize.
4. Publish phase/progress through the native bridge so SwiftUI can synchronize
   controls without owning Unity animation timing.
5. Keep acrylic tint weak and preserve the neutral physical case as the
   fallback/default profile.
