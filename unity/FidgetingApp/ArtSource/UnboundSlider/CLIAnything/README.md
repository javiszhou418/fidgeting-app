# Unbound Slider — CLI Anything DCC candidate

This folder contains the stateful CLI Anything project and its deterministic
Blender companion for a candidate replacement of the fifth
`magnetic-slide-tile` product.

## Source files

- `UnboundSliderWhiteModel.blend-cli.json` — stateful CLI scene, materials,
  hierarchy, assembly frame 1, and exploded frame 40.
- `UnboundSlider_CLI.blend` — authoritative Blender source generated from the
  CLI contract.
- `UnboundSlider_CLI.fbx` / `.glb` — visual exchange assets.
- `UnboundSlider_CLI_Collision.fbx` — independent low-complexity collision
  exchange asset.

The exact builder is
`/Users/jiawei.zhou/Documents/Fidgeting app/tools/blender/build_unbound_slider_cli.py`.

## Locked visual geometry

- Nominal envelope: 52 × 36 × 14 mm, R4.8 outer corners.
- Each main opening is a goggle profile: two complete R4.2 circles with equal
  centre height, joined by one 3.5 mm straight waist.
- The upper/lower goggle openings are related by 180° centre symmetry.
- Upper/lower trapezoid windows remain separate from the main openings.
- Left/right rounded triangular apertures share the horizontal midline.
- The independent middle plate carries 24 real chevron ribs and a centre screw.
- Six visual magnet stations match the shipping six-detent mechanism count;
  motion and Haptics continue to read `LinearMagneticDetentProfile`.

The supplied photograph/video does not define manufacturing tolerances, press
fits, mass, or hidden internal dimensions. This is production artwork and a
nominal mechanical visualization, not fabrication CAD.

## Regenerate

```bash
cli-anything-blender --json --project "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/UnboundSliderWhiteModel.blend-cli.json" scene info
"/Applications/Blender.app/Contents/MacOS/Blender" --background --python "/Users/jiawei.zhou/Documents/Fidgeting app/tools/blender/build_unbound_slider_cli.py"
```

Blender validation and nine real renders are written to
`unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/`. Exchange assets and
PBR source maps stay in this ArtSource folder; the builder deliberately does
not copy anything into `Assets/` while the Unity visual gate is failed.

## Current gate status

The deterministic DCC geometry passes envelope, symmetry, manifold, zero-area,
and mobile triangle-budget validation. An isolated Unity candidate also passed
10/10 focused EditMode checks. However, the fifth real shipping-scene preview
still clipped the right-half metal highlight and lost face/middle-layer detail.
It is therefore **not integrated and excluded from the current release**. The
rejected Unity preview and test XML are preserved under
`Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/`.
