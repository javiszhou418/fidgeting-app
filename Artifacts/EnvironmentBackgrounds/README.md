# Rough Cave Background Variants

Four portrait environment plates generated from the supplied visual reference.

- `cave-container-background-01-cool-overhead.png`: cool overhead skylight and a broad empty stone platform.
- `cave-container-background-02-warm-side.png`: warm left-side dawn light and an empty oval basin platform.
- `cave-container-background-03-cool-rear.png`: cool rear-right light and an empty circular recessed platform.
- `cave-container-background-04-diffuse-fissure.png`: diffuse fissure light and an empty rectangular stone container.

These are source-art explorations only and are not integrated into the shipping Unity product.

## V2: semi-abstract night variants

- `cave-container-background-01-cool-overhead-v2.png`: simplified curved rock masses, cool mist, and a restrained starry opening.
- `cave-container-background-02-warm-side-v2.png`: layered rounded silhouettes, muted warm edge light, and a narrow night-sky wedge.
- `cave-container-background-03-cool-rear-v2.png`: minimal vertical slabs, cool sky rim, and a small starry opening.
- `cave-container-background-04-diffuse-fissure-v2.png`: overlapping abstract planes, diffuse night fill, and an empty rectangular container.

The V2 set intentionally reduces geological specificity and photoreal surface detail while preserving an empty staging platform and a small view of the night sky.

## V3: shallow-depth-of-field variants

- `cave-container-background-01-cool-overhead-v3-dof.png`
- `cave-container-background-02-warm-side-v3-dof.png`
- `cave-container-background-03-cool-rear-v3-dof.png`
- `cave-container-background-04-diffuse-fissure-v3-dof.png`

V3 keeps the V2 semi-abstract layouts while moving the focal plane onto the empty platform surface. Background forms, mist, and night sky progressively defocus with distance so a small foreground object can remain the visual focus.

## V4: high-DPI model 2/3/4 variants

- `cave-container-background-02-warm-side-v4-hd.png`
- `cave-container-background-03-cool-rear-v4-hd.png`
- `cave-container-background-04-diffuse-fissure-v4-hd.png`

V4 uses AI reconstruction constrained to the V3 composition, followed by a
non-sharpening 2× resize to 1882 × 3344. The Unity importer retains the native
dimensions (NPOT None / 4096 max) and uses ASTC 8×8 on iOS. Model 1 deliberately
keeps its original V3 resource and presentation.

The shipping Unity product maps these through `SpinnerEnvironmentCatalog`:

- cool overhead → classic blue
- warm side → metal three-blade
- cool rear → mirror-steel four-wing
- diffuse fissure → graphite two-lobe

Unity-rendered 900 × 1600 neutral and maximum-parallax integration previews are
stored in `Artifacts/EnvironmentIntegration`.
