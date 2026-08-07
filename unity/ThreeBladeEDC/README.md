# Three-Blade EDC — Unity iPhone Product Viewer

Interactive Unity presentation of a three-blade EDC spinner reconstructed from reference images.

> **Concept boundary:** This project is a visual and interaction study, not manufacturing-grade CAD. Exact dimensions, material grades, bearing construction, washers, fasteners, clearances, tolerances, load ratings, and the bill of materials were not established from a physical sample. Any internal anatomy shown in the assembled or exploded views is an explicitly inferred concept and must not be used for production.

## Requirements

- Unity Editor `6000.5.6f1`
- Universal Render Pipeline `17.5.0`
- Input System `1.20.0`
- Unity Test Framework `1.7.0`
- Xcode `26.4` for the supplied iOS build pipeline
- iPhone 12 or newer with Developer Mode enabled for direct installation

## Open and run

1. Open `unity/ThreeBladeEDC` with Unity `6000.5.6f1`.
2. Open the delivery scene listed below.
3. Enter Play Mode.

Delivery scene: `Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity`

## iPhone controls

| Input | Action |
| --- | --- |
| Drag or flick on the model | Apply real Rigidbody angular velocity; bearing drag slows it after release |
| Drag on the background | Orbit the product camera |
| Two-finger pinch | Zoom between the protected near/far limits |
| `EXPLODE / ASSEMBLE` | Pause rotor physics and smoothly separate/restore the inferred parts |
| `RESET` | Stop the rotor and motor, assemble all parts, and restore the Hero camera |
| `MOTOR` | Toggle the automatic demonstration spin |
| `VIEW` | Cycle Hero, top, and side views |

Mouse input remains available in the Editor: left drag is classified by hit target, right drag orbits, and the wheel zooms. One `MobileGestureController` owns all pointer streams so spin, orbit, pinch, and UI cannot compete for the same touch.

## Interaction parameters

The Rigidbody interaction components expose these starting values in the Inspector:

| Parameter | Default | Meaning |
| --- | ---: | --- |
| Spin axis | Local `Y` | Physical rotor axis |
| Angular damping | `0.55` | Rigidbody angular damping |
| Maximum rotor speed | `24 rad/s` | Axial angular-speed clamp |
| Flick sensitivity | `0.34` | Multiplier for signed circular pointer motion |
| Maximum flick speed | `24 rad/s` | Pointer-derived speed clamp |
| Flick smoothing | `15 s⁻¹` | Exponential input smoothing rate |
| Motor target speed | `35 rad/s` | Target while the on-screen motor toggle is enabled |
| Motor acceleration | `80 rad/s²` | Maximum motor acceleration |
| Bearing-cage visual ratio | `0.50` | Cage visual angle divided by accumulated rotor angle |

Gravity is disabled, the rotor center is frozen when no hinge is present, and Rigidbody interpolation is enabled. These are presentation defaults, not measurements of a physical product.

The iOS delivery uses product name `Three-Blade EDC`, bundle identifier
`com.jiaweizhou.threebladeedc`, version `0.1.0`, minimum iOS `15.0`, IL2CPP,
ARM64, and Metal. The runtime is locked to landscape left/right, targets 60 FPS,
prevents display sleep, and safely clears touch/motor state when backgrounded.
The overlay is fitted to the device Safe Area.

## Visual calibration

The reference boards provide visual starting points rather than measured material data:

| Zone | Metallic | Roughness | Notes |
| --- | ---: | ---: | --- |
| Three-blade body | `1.00` | `0.28` | Cool silver, fine ground finish |
| Center cap | `1.00` | `0.19` | Radial brushed appearance |
| Highlight bevels | `1.00` | `0.10` | Continuous, controlled edge highlights |
| Dark center ring | Candidate | `0.32` | Material identity is inferred |

The Hero camera uses an `85 mm` physical focal length. Lighting starts from a `5000 K` key, `3200 K` warm rim, and `6500 K` cool fill. The warm orange edge in the reference is treated as rim lighting, not confirmed copper material.

## Model and motion contract

- Exactly three equal blade sectors are arranged at `120°` around one rotor axis.
- The rotor and bearing outer race rotate together.
- The holder, center caps, and bearing inner race remain independent of the rotor.
- Motion is real Transform/Rigidbody rotation; motion blur is presentation-only and is not a substitute for geometry rotation.
- Bearing internals and the exploded view are inferred concept anatomy, not an engineering BOM.

## iOS export and direct installation

The serial pipeline refuses to guess the signing team. It requires exactly one valid `Apple Development` identity and reads the real ten-character Team ID from the certificate `OU` field. Existing exports are moved into `Builds/iOS/Archive` instead of being deleted.

With the iPhone connected by data cable, unlocked, trusted, and in Developer Mode:

```bash
cd "/absolute/path/to/Fidgeting app"
./scripts/ios_build_and_install.sh
```

The command exports Unity to `Builds/iOS/ThreeBladeEDC`, verifies `project.pbxproj` and `Info.plist`, builds a signed Debug device app with `xcodebuild -allowProvisioningUpdates`, discovers the hardware UDID, installs with `devicectl`, and launches the bundle. To reuse an already complete Unity export:

```bash
./scripts/ios_build_and_install.sh --install-existing
```

The script stops before Xcode if the paired phone is offline, locked, or lacks Developer Disk Image services. Reconnect and unlock the device, accept any Trust/Allow Access prompt, and rerun the `--install-existing` form.

## Automated acceptance tests

Edit Mode acceptance covers:

- three-blade count and `120°` radial symmetry;
- finite mesh vertices, normals, and bounds;
- triangle index validity and non-degenerate triangles;
- independent rotor, holder/cap, and bearing-race hierarchy;
- one unified gesture owner, Safe Area UI, and active studio stage;
- mobile PBR mesh channels and a visible triangle budget below `60k`;
- real Play Mode spin hit classification, zoom clamps, exploded-state physics restoration, and background pause safety;
- iOS bundle, version, Metal/URP, orientation, signing, MSAA, and render-scale settings.

Run from Unity Test Runner with **EditMode** selected, or in batch mode:

```bash
"/Applications/Unity/Hub/Editor/6000.5.6f1/Unity.app/Contents/MacOS/Unity" \
  -batchmode \
  -projectPath "/absolute/path/to/Fidgeting app/unity/ThreeBladeEDC" \
  -runTests -testPlatform EditMode \
  -testResults "/tmp/three-blade-editmode.xml" \
  -logFile "/tmp/three-blade-editmode.log"
```

On the current macOS/Unity `6000.5.6f1` installation, `-nographics` caused the IL Post Processor runner to exit before test discovery. Use the command above without `-nographics`, or run the same Edit Mode suite from the Test Runner window. A run that produces no XML result is an environment-blocked run, not a passing or failing test result.

Last verified result (2026-08-02): **12/12 tests passed**. The Edit Mode run includes three coroutine tests that enter Play Mode and exercise the delivered scene.

## Reference limitations

Visually supported by the supplied images:

- three-blade silhouette and low side profile;
- faceted center cap;
- recessed triangular regions and a dark annular separation;
- silver, metal-like finish.

Estimated or inferred:

- exact blade angle, thickness, scale, and surface roughness;
- axis, bearing races, balls, washers, lower cap, and part connections;
- every internal fit, clearance, tolerance, material specification, and manufacturing process.

A physical sample must be measured and disassembled before any CAD, tooling, safety, or production decision.
