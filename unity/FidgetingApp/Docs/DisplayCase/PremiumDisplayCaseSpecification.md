# Premium Display Case / Collector Slab

The shipping premium display case is one reusable vertical Collector Slab for
all six products. It uses a stepped frosted-polycarbonate shell, a physical top
label, a black flocked display chamber, and one narrow rarity foil line. The old
four black fasteners and compact center capsule are intentionally absent.

The case owns packaging, label presentation, lighting, parallax, reveal motion,
and content fitting. It never owns or remodels a prize. Geometry, pivots,
parents, colliders, mechanism state, and interaction remain with the canonical
shipping product.

## Runtime contract

```csharp
PremiumDisplayCase displayCase = PremiumDisplayCaseFactory.Instantiate(parent);
displayCase.setCapsulePreset(
    PremiumDisplayCaseCapsulePreset.CollectorSlabLarge);
displayCase.SetCollectorLabel(new PremiumDisplayCaseCollectorLabel(
    productName,
    editionName,
    level,
    firstObtainedDate,
    authoritativeCollectibleId));
displayCase.setContent(productSnapshot, profile.ContentOptions);
displayCase.onRevealComplete += HandleRevealComplete;
displayCase.play();
```

`setContent` receives an already-instantiated Unity `Transform` or `GameObject`.
The case temporarily reparents it and restores its original parent, local pose,
scale, active state, and ownership when replaced or destroyed. Passing `null`
restores the development placeholder. The case never destroys caller-owned
content.

The exact anchor remains `contentSlot`:

```text
contentSlot
└── ContentRevealRoot
    └── ContentOrbitRoot
        └── ContentFitRoot
            └── renderer-only shipping product snapshot
```

The snapshot preserves shared meshes, materials, renderer property blocks and
source-root-relative transforms, but excludes cameras, particles, lines,
grounding stages, physics, audio, input and runtime scripts.

## Physical dimensions and content fit

`CollectorSlabLarge` is a `180 × 198 × 48 mm` rounded-rectangle display chamber
with a `16 mm` corner radius. The Blender shell is `216 × 304 × 59 mm`; its top
physical label is `184 × 58 mm`.

Content is centered on all three axes and uniformly scaled. XY bounds are the
authoritative visible-composition constraint with 30% total padding, yielding a
70% target fill on the limiting display-plane dimension. Z bounds do not shrink
the visible collectible: all six authored products are already thinner than the
48 mm chamber, while their 90-degree presentation transform can map a planar
dimension into world Z during measurement. Scale remains uniform; no product is
stretched.

Collector Slab profiles disable autonomous idle rotation. They retain the
authoritative front-facing orientation (`90,-8,0`, or `-90,-8,0` for the fan
card so its A/Q/K face remains visible).

## Physical label and persisted data

The top label is built from real case geometry and `TextMesh` marks, so it is
lit with the slab instead of behaving like a floating UI overlay. It contains:

- canonical English product name;
- edition / finish;
- first authoritative acquisition or discovery date;
- rarity tier and current level;
- stable collectible ID only when an authoritative value exists;
- the highest applicable Toy Badge treatment.

Core model discovery dates and gacha prize acquisition timestamps use a
versioned schema. New records persist the first timestamp only. Existing v1
ownership migrates safely with an unknown date and renders `ACQUIRED —`; the
runtime never substitutes the current date or a conceptual sample number.

Tier color is restricted to the label frame and a single narrow foil band:
Standard cool silver, Refined blue titanium, Signature champagne gold, and
Heirloom smoked violet. These are metallic material signals, not emission.

## Materials and lighting

The shell shader exposes frosted transmission, broad edge sheen and subtle
isotropic micro-scratches. The display chamber uses black flocking; the label is
warm neutral stock with dark print. Default lighting is a restrained warm key,
cool fill and muted burgundy rim against a dark wine background.

Three approved real products share a refined mobile metal response without
geometry changes:

- `MAGNETIC TRINITY`: bead-blasted titanium body, broad matte highlights;
- `MIRROR QUAD`: satin steel body with restrained polished/radial accents;
- `GRAPHITE DUO`: `#3A3D40`, metallic `1`, roughness `0.76`, isotropic grain.

The other three products retain their already approved shipping materials.

## Blender layers and interaction

`ArtSource/DisplayCase/PremiumDisplayCase.blend` is the editable source of
truth. The FBX keeps eight stable prize-agnostic interaction layers for backward
compatibility, while their physical contents are now:

1. frosted polycarbonate front shell;
2. physical label stock and foil frame;
3. transparent molded spacer frame;
4. rounded display-chamber rim and rarity foil band;
5. black flocking insert;
6. frosted rear shell;
7. rear stepped reinforcement frame;
8. front stepped reinforcement frame.

The runtime exploded/assembly controller and `contentSlot` layer attachment are
unchanged. Native controls continue to provide back, drag orbit, pinch zoom,
exploded progress, replay and reset. The case presentation never writes prize
physics, mechanism state or Haptic events.

## Shipping assets and validation

- Runtime prefab: `Assets/Resources/Gacha/PremiumDisplayCase.prefab`
- Blender source: `ArtSource/DisplayCase/PremiumDisplayCase.blend`
- Blender build: `ArtSource/DisplayCase/build_premium_display_case.py`
- Blender validator: `ArtSource/DisplayCase/validate_premium_display_case.py`
- Unity FBX: `Assets/_DisplayCase/Models/PremiumDisplayCase.fbx`
- Preview scene: `Assets/_DisplayCase/Scenes/PremiumDisplayCase.unity`
- Runtime source: `Assets/_DisplayCase/Runtime/`
- Shell shader: `Assets/_DisplayCase/Shaders/PremiumAcrylicLiquidGlass.shader`
- Tests: `Assets/_DisplayCase/Tests/Editor/PremiumDisplayCaseTests.cs`
- Six-product previews:
  `Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/`

Required visual evidence is generated from shipping Unity with a real graphics
device, never `-nographics`. Each of the six product folders contains authored
hero, top, left oblique, right oblique, low angle and phone hero captures.
Concept images are not shipping evidence and are not copied into the approved
Design Bible asset set.
