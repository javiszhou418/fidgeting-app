# Dragon Scale EDC — CLI Anything 85 mm shipping candidate

This folder contains the reference-matched Blender source now wired into the
shipping Unity `gold-four-wing` slot. The stable product ID is retained for
save compatibility; neither authored three-blade scene is replaced.

## Files

- `DragonScaleEDC_CLI.blend-cli.json` — stateful cli-anything-blender project
  containing the mechanical hierarchy and core PBR material values.
- `DragonScaleEDC_CLI_85mm.blend` — authoritative DCC source.
- `DragonScaleEDC_CLI_85mm.fbx` — visual exchange asset.
- `DragonScaleEDC_CLI_85mm.glb` — visual exchange asset.
- `DragonScaleEDC_CLI_85mm_Collision.fbx` — independent low-complexity
  collision exchange asset.

The deterministic generator is
`/Users/jiawei.zhou/Documents/Fidgeting app/tools/blender/build_dragon_scale_cli.py`.

## Reference basis

- Overall width: 85.0 mm
- Finger-cap diameter: 44.2 mm (`0.52W`)
- Rotor body depth: 7.65 mm (`0.09W`)
- Assembled depth: 17.0 mm (`0.20W`)
- Blade angles: 90°, 210°, 330°
- Bearing: 22 × 8 × 7 mm

The supplied artwork does not specify manufacturing tolerances, mass, press
fits, fasteners, or hidden internal dimensions. This candidate is a visual and
nominal-dimension reconstruction, not production CAD.

## Regenerate and verify

```bash
blender --background --python "/Users/jiawei.zhou/Documents/Fidgeting app/tools/blender/build_dragon_scale_cli.py"
```

Validation and seven real Blender renders are written to
`unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/`.

Current status: wired into
`Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity`, full EditMode regression
passed 300/300, and five shipping-scene approval views are available under
`Artifacts/DragonScaleCLIShippingPreview/`. Device installation remains blocked
until the user explicitly approves those Unity previews.
