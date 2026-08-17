# Fidgeting App Repository Contract

These instructions apply to every task and conversation working in this repository.

## 总控进度通知

- 每完成一个可验证的 feature 优化节点，负责该优化的 Codex task 必须向现有的“总控”task 发送一次进度同步，由总控向用户推送该 feature 的当前状态。
- 每条同步固定包含：feature 名称、当前阶段、已完成内容、验证证据、下一步，以及是否正在等待视觉批准、真机验收或用户输入。
- “已写代码”本身不算完成节点；必须完成与风险相称的编译、自动化测试或 shipping 实现预览后，才能报告为已完成。失败或阻塞必须如实标记。
- 涉及视觉变化时，在用户明确批准真实 shipping 预览前，状态必须写明“视觉批准待确认，未推送手机”，不得让总控将其误报为已安装或已真机验证。

## Canonical product

- The shipping Unity product is `unity/FidgetingApp`.
- `unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md` is the canonical authority for product definition, design preferences, current experience requirements, approved visual evidence, rejection criteria, and decision history.
- `PRODUCT_PLAN.md` is a short compatibility entry and navigation index. It must not become a second, drifting source of product design truth.
- `unity/FidgetingApp/Docs/FidgetingInteractionHapticsSystem.md` defines the target interaction, mechanics, Core Motion, and Haptic architecture.
- `unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md` records what is actually integrated. A specification or mockup alone is never implementation.

## Design bible synchronization gate

- When the user explicitly approves, rejects, supersedes, or materially changes a product, visual, interaction, growth, collection, economy, or release decision, update `unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md` in the same feature task.
- Every executable design decision must use or update a stable `FDB-*` requirement ID and record `DecisionState`, source task/thread ID, and the applicable date or approval round. Do not cite temporary rollout or `/tmp` paths.
- Keep `DecisionState` separate from `DeliveryState`. A locked design may still be only specified; code, tests, installation, and device acceptance are separate gates.
- Copy only still-valid, explicitly approved shipping previews into `unity/FidgetingApp/Docs/DesignBibleAssets/`. Rejected, superseded, conceptual, or approval-pending previews belong only in the decision history or implementation evidence, not the approved asset set.
- Rejected and superseded directions must be removed from current requirements and preserved in the design bible decision appendix with their replacement. Do not silently restore them in later work.
- Runtime, scene wiring, automated tests, build/install evidence, and iPhone validation continue to be recorded in `unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md`; do not duplicate long build logs in the design bible.
- Build, install, launch, or a request to “push to phone” does not by itself change a design to approved or a delivery state to device accepted.

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

## Magnetic fan-card modeling gate

- Any task that changes the magnetic fan card's card geometry, pivot, rear track, grille, magnets, bearing follower, face artwork, layer parenting, materials, or imported Blender asset must use the `fan-card-modeling-guardrails` skill before editing.
- `unity/FidgetingApp/Docs/FanCardModelingGuardrails.md` and `unity/FidgetingApp/ArtSource/FanCard/fan_card_guardrails.json` are the authoritative modeling contract. Do not re-derive their locked dimensions from a screenshot or introduce a duplicate default.
- The complete rear-track outer contour, including the 6.2 mm undercut ribbon and rounded end caps, must keep at least 6.0 mm clearance from the rounded card outline. A centerline-only or endpoint-only check is insufficient.
- Before reporting a fan-card model change complete, rebuild the Blender source, rebuild the shipping Unity scene, run `validate_fan_card_guardrails.py`, pass the Unity geometry validator and fan-card EditMode tests, and regenerate the required shipping-scene previews. A failure blocks device installation.
