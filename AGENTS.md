# Fidgeting App Repository Contract

These instructions apply to every task and conversation working in this repository.

## Canonical product

- The shipping Unity product is `unity/FidgetingApp`.
- `PRODUCT_PLAN.md` defines product scope.
- `unity/FidgetingApp/Docs/FidgetingInteractionHapticsSystem.md` defines the target interaction, mechanics, Core Motion, and Haptic architecture.
- `unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md` records what is actually integrated. A specification or mockup alone is never implementation.

## Required interaction invariants

- The rotor starts and resets at zero angular velocity. No historical motor, idle loop, animation, or fallback may create self-spin.
- Freewheel motion can only receive speed from an explicit user or device input, then decays using frame-rate-independent half-life damping.
- Magnetic detent motion remains captured below breakaway, travels only after breakaway, captures the nearest detent at low speed, and finishes at zero angular velocity.
- Physical and Haptic detent counts must come from the same mechanism setting.
- Haptics must ultimately follow this pipeline: input -> mechanism state -> semantic event -> Haptic recipe -> iOS renderer.
- Do not add new raw-input-to-`IosHaptics` calls. Existing direct calls are migration debt until the semantic event layer replaces them.
- `Tick`, `Detent`, `Snap`, `Pop`, `Burst`, `Breakaway`, and `Capture` are app semantics. Do not present them as Apple Core Haptics event types.
- Shake must use user acceleration plus hysteresis/cooldown. Device Twist must use unwrapped attitude or integrated rotation rate; raw wrapped Euler subtraction is invalid.

## Definition of done

Do not report a feature as integrated merely because documentation, UI controls, constants, or a native stub exist. A feature is integrated only when all applicable items are present:

1. Runtime implementation in the canonical Unity product.
2. Scene/prefab/coordinator wiring reaches that implementation.
3. Automated tests cover its deterministic rules and regressions.
4. Native bridge start/update/stop lifecycle is implemented when iOS APIs are involved.
5. An iPhone validation remains explicitly pending until it is performed on hardware.
6. `Docs/IMPLEMENTATION_STATUS.md` is updated with code and test evidence.

When a task changes a recommended tuning value, update the runtime source of truth, serialized scene/prefab value, native/UI fallback if one exists, and the acceptance test in the same change. Do not allow silent duplicate defaults to drift.

## Device visual push gate

- Before installing any build that changes model appearance, stickers, materials, lighting, camera composition, or native UI, generate previews from the shipping Unity scene or native implementation rather than a conceptual mockup.
- Model-appearance previews must cover top, authored hero, left/right oblique, and low-angle views. Exercise at least one pictogram, one text mark, and one thin-line mark when sticker rendering changes.
- Show the preview to the user and obtain explicit visual approval before building or installing that visual change on their device. Automated tests, compilation, signing, or a successful launch do not replace this approval.
- Record the preview artifact and the approval-pending state in `unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md`.
