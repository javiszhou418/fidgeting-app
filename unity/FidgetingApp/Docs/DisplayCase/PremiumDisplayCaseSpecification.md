# Premium Display Case

The premium display case is a reusable gacha presentation component. Its
shipping style is a slim clear-acrylic rectangle with four oversized black cap
fasteners, chrome collars, a graphite insert, and a compact central capsule.
It owns the case, lighting, parallax, and reveal motion, but never owns a
particular prize design. An oversized opaque outer box is explicitly excluded.

## Runtime contract

The shipping prefab is loaded through:

```csharp
PremiumDisplayCase displayCase = PremiumDisplayCaseFactory.Instantiate(parent);
displayCase.setCapsulePreset(PremiumDisplayCaseCapsulePreset.CircularStandard);
displayCase.setContent(importedGltfRoot, PremiumDisplayCaseContentOptions.Default);
displayCase.onRevealComplete += HandleRevealComplete;
displayCase.play();
```

`setContent` receives an already-instantiated Unity `Transform` or `GameObject`
that represents the root of a glTF import. URL fetching and glTF parsing stay in
the caller so the case does not depend on a specific importer package. Passing
`null` restores the development coin placeholder.

The case temporarily reparents external content for presentation and restores
its original parent, local pose, scale, and active state when it is replaced or
the case is destroyed. It never destroys caller-owned content.

## Content slot

The exact anchor is named `contentSlot` and is centered in the neutral capsule.
Three internal wrappers separate reveal scale, idle rotation, and fit transform:

```text
contentSlot
└── ContentRevealRoot
    └── ContentOrbitRoot
        └── ContentFitRoot
            └── runtime glTF root or development placeholder
```

All enabled child renderers are measured after parenting. Collider bounds are a
fallback for renderer-free nodes. The measured bounds are uniformly scaled to
the capsule's diameter and depth with 8% total padding, and their center is
translated to the capsule origin on all three axes. Idle rotation is enabled by
default at one revolution per 4 seconds and can be disabled per content item.

## Capsule presets

The neutral capsule can be circular or rounded-square. Diameter and depth are
runtime parameters clamped to safe authored ranges. Shipping presets are:

| Preset | Shape | Diameter | Depth |
| --- | --- | ---: | ---: |
| Circular Compact | Circular | 72 mm | 20 mm |
| Circular Standard | Circular | 84 mm | 26 mm |
| Circular Deep | Circular | 84 mm | 36 mm |
| Rounded Square Standard | Rounded square | 84 mm | 26 mm |
| Rounded Square Deep | Rounded square | 84 mm | 38 mm |

No capsule contour follows a prize silhouette.

## Motion and rendering ownership

The reveal is a finite 2.20-second deterministic sequence: the clear rear
reinforcement layer separates, the acrylic case rises with a restrained overshoot, the liquid
glass appears with a diagonal sweep, the content resolves, and the case-owned
lights pulse before settling. `onRevealComplete` fires exactly once per `play()`.

Parallax consumes the app's existing filtered `SceneParallaxInput` stream. The
adapter does not start or stop Core Motion. Four authored depth layers move at
different amplitudes: the outer box counters the tilt, acrylic moves slightly,
the inner lining moves farther, and the content slot moves farthest. A maximum
4.8-degree case rotation keeps the effect readable without making the object
feel loose.

The acrylic shader is neutral and texture-free. Its Fresnel edge, virtual
specular bands, reveal sweep, and subtle tilt response are case properties. Case
lights never use a content texture or prize-specific baked reflection.

## Blender layers and native manipulation

`ArtSource/DisplayCase/PremiumDisplayCase.blend` is the editable source of
truth. `build_premium_display_case.py` rebuilds that source and exports the FBX
consumed by Unity. The FBX contains eight stable, prize-agnostic layers:

1. clear front acrylic plate;
2. four removable black cap fasteners with chrome collars;
3. clear acrylic spacer frame;
4. compact clear neutral capsule;
5. graphite insert with a real capsule aperture;
6. clear rear acrylic plate;
7. inset graphite tray, fully inside the acrylic outline;
8. clear rear reinforcement frame.

Unity reapplies the Blender-to-Unity axis mapping after unpacking the FBX so
Blender +Z is Unity +Y and Blender -Y faces the shipping camera. The runtime
interaction controller keeps the content slot attached to layer 4 while the
eight authored case layers move through a deterministic 1.35-second exploded
or assembly sequence.

The shipping SwiftUI overlay supplies a top-left back button, drag-to-orbit,
pinch-to-zoom, an exploded-progress slider, assembly replay, and view reset.
These gestures send semantic values to `FidgetAppCoordinator`; Unity remains
the owner of the 3D transforms. Orbit is clamped to 34 degrees yaw and 22
degrees pitch, and zoom is clamped to 0.84–1.18.

The preview reference composition is 1200×1600 at a 29-degree vertical field
of view. Runtime cameras preserve that horizontal composition and derive their
vertical field of view from the current device aspect ratio, preventing the
case edges from being cropped on tall iPhones.

## Shipping assets and validation

- Runtime prefab: `Assets/Resources/Gacha/PremiumDisplayCase.prefab`
- Blender source: `ArtSource/DisplayCase/PremiumDisplayCase.blend`
- Reproducible Blender build: `ArtSource/DisplayCase/build_premium_display_case.py`
- Unity FBX: `Assets/_DisplayCase/Models/PremiumDisplayCase.fbx`
- Preview scene: `Assets/_DisplayCase/Scenes/PremiumDisplayCase.unity`
- Runtime source: `Assets/_DisplayCase/Runtime/`
- Acrylic shader: `Assets/_DisplayCase/Shaders/PremiumAcrylicLiquidGlass.shader`
- Deterministic EditMode tests: `Assets/_DisplayCase/Tests/Editor/PremiumDisplayCaseTests.cs`
- Shipping-scene previews: `Artifacts/PremiumDisplayCasePreview/`
- Shipping native preview: `Artifacts/PremiumDisplayCaseNativePreview/`

The placeholder coin is for development and fallback only. It is not a prize
catalog item and does not establish any content-specific geometry or material
contract.
