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

## Shipping UI component-library gate

- This gate applies to every new or modified visible UI in `unity/FidgetingApp`, including SwiftUI, UIKit, Unity UI, Rive-adjacent controls, and shipping preview hosts.
- Read `Docs/FidgetingAppProductDesignBible.md` and `Docs/LiquidGlassDesignGuideline.md` before editing visible UI.
- Native business views may only compose components and tokens from `Assets/Plugins/iOS/FidgetProductUIComponents.swift`.
- Do not hand-write product buttons, glass surfaces, headings, tags, cards, spacing, typography, pressed motion, or action states in business views.
- If a reusable primitive is missing, add and test it in `FidgetProductUIComponents.swift` first, then consume it from the business view.
- Use `ProductPrimaryActionButton` for Primary text actions. Keep one Primary per decision region and use `ProductActionState` for action state.
- Every native root must apply `productDesignSystem()`. Business UI must not use `.font(.system...)`, tracking, kerning, raw glass materials, perimeter strokes, or hard-coded radii.
- Unity and Rive may render product content and motion, but must not introduce a second business-control or CTA system.
- Every visible UI change requires focused tests and a shipping-source preview. Keep “视觉批准待确认，未推送手机” until explicit approval.

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

## Standardized 3D model provenance gate

- Any task that creates, rebuilds, imports, or changes 3D model geometry, proportions, pivot, hierarchy, materials, lighting, cameras, export packages, or Unity model presentation must use the `fidgeting-model-pipeline` skill before editing.
- The repository-authoritative skill is `skills/fidgeting-model-pipeline/`. The per-model authority is `unity/FidgetingApp/ArtSource/ModelPipeline/<model-id>/pipeline.json` plus its append-only `history.ndjson`; do not maintain an untracked parallel checklist.
- Resume work at the earliest non-approved gate in the 12-gate pipeline. Every gate requires an explicit user decision. A rejection creates a new revision, and any changed upstream reference, claim, dimension, structure, or asset hash makes downstream gates stale.
- Blender/CLIAnything is the default deterministic reconstruction route. Hyper3D Rodin may be used only as a separately labeled concept branch and must never be promoted directly into Unity or treated as approved geometry.
- Stage 12 must contain previews from the real shipping Unity scene and receive explicit approval before a model-appearance build can be installed on a phone. Device acceptance remains a separate status after installation.

## Persistent model workbench gate

- Keep one repository workbench with a stable left model selector and stable progress/navigation. Revisions may change content, not the information architecture.
- Always show the current model, current task, `当前 Gate NN/12`, `已批准 X/12`, and the ordered 12-gate roadmap.
- Keep these seven tabs visible in this order: `参考原图`, `分析（截图/视频）`, `尺寸`, `交互 CAD`, `白模`, `贴图与材质`, `Unity 灯光与成品`.
- Show `当前`, `已批准`, `过期`, `被退回`, or `未开始` on each tab. Keep stale and rejected artifacts inspectable as labeled history.
- Persist the selected model, tab, gate, scroll/view state, and opened artifact. Reload, browser history, and direct model/tab/gate URLs must restore context.
- An explicit tab, gate, or artifact route overrides automatic earliest-problem navigation. Keep the `当前正在做什么` banner stable while content versions change.

## Interactive model approval gate

- Text summaries and static screenshots are supplementary evidence only. Neither can be the sole approval artifact for any model gate, and chat text alone never approves a gate.
- Mechanical, contract, architecture, blockout, and geometry gates require an interactive CAD/3D simulator. Use a complete simulator recording only when interaction is unavailable.
- Material, lighting, and environment gates require interactive lookdev or a real render turntable/comparison recording.
- Export approval requires interaction with the real exported GLB. Unity parity and shipping approval require a real Unity simulator/runtime preview or a complete recording.
- Keep approval controls disabled until the gate-specific interaction or viewing checklist is complete.
- Every approval event must record the reviewed artifact SHA-256, governing contract SHA-256, exact parameter snapshot, completed checklist, interaction mode, and browser/device timestamp.
- Interactive evidence remains mandatory before requesting approval, but the final authority is the user's latest explicit instruction in this chat. Approval may be given in the workbench or in chat. The latest explicit chat decision overrides stale or conflicting tool state and must be persisted through workflow history with its exact wording.
- A workbench approval button is optional. Do not block a valid explicit chat approval after the required interactive evidence exists.
- A fallback recording can satisfy viewing milestones only when the user marks interaction unavailable and watches the full recording. Interactive operation remains preferred.
- Keep exactly 12 gates grouped into three user-facing phases: reference + interaction form (Gates 01–04) → Blender modeling + textures (Gates 05–10) → Unity + scene + rendering (Gates 11–12).
- Structural CAD covers parts, ownership, endpoint pivot, bilateral rails, simultaneous kinematics, dimensions, sections, tangencies, gaps, and steps. It must not expose damping, force feel, detent strength, inertia, sound, stop feel, or Simulator recordings.
- Approved interaction-form CAD feeds the later modeling gates after Gate 03–04 contracts and required physical dimensions are complete. A standalone hand-feel Simulator is not a pre-Blender gate.
- Preserve any old Simulator draft as internal/superseded. A simulator may be created later only as a requested Unity interaction-validation tool.
- Magnetic-slide Gate 03 blocks only on nine core measurements: closed L/W/T, top thickness, bottom thickness, max travel, fixed-axis offset from the nearest rounded end, rotating-carrier diameter, and closed seam/gap. Each needs mm, method/source, and uncertainty.
- The user's latest explicit chat instruction may authorize a provisional Gate 03 modeling contract that reuses hash-linked prior dimensions. Mark every value `user-authorized-provisional`, never `measured`; keep unknown engineering dimensions unknown and limit authorization to the stated downstream gate.
- Groove spacing/width/depth, axis diameter, step heights, and visible follower dimensions are optional for initial blockout. Operating clearance, allowance, and tolerance are manufacturing-stage unknowns and never block initial Blender modeling.

## Premium Display Case whole-case gate

- Premium Display Case shipping animation, native UI, Unity presentation, and user approval previews must show the whole assembled case only.
- Never expose explode, assembly, reassembly, layer separation, or assembly scrub in those product paths.
- Pipeline-required exploded geometry may remain as internal technical evidence. Keep it out of `reviewArtifactIds` and every primary user preview.
- Current Premium Display Case work changes the case body and its presentation only. The enclosed toy/prize geometry, materials, artwork, pivot, physics, Haptics, and mechanism are out of scope.
- Treat the toy as caller-owned content attached through `contentSlot`. Do not edit or rebuild it unless the user starts and approves a separate toy feature task.

## Magnetic fan-card modeling gate

- Any task that changes the magnetic fan card's card geometry, pivot, rear track, grille, magnets, bearing follower, face artwork, layer parenting, materials, or imported Blender asset must use both the `fidgeting-model-pipeline` and `fan-card-modeling-guardrails` skills before editing.
- `unity/FidgetingApp/Docs/FanCardModelingGuardrails.md` and `unity/FidgetingApp/ArtSource/FanCard/fan_card_guardrails.json` are the authoritative modeling contract. Do not re-derive their locked dimensions from a screenshot or introduce a duplicate default.
- The complete rear-track outer contour, including the 6.2 mm undercut ribbon and rounded end caps, must keep at least 6.0 mm clearance from the rounded card outline. A centerline-only or endpoint-only check is insufficient.
- Before reporting a fan-card model change complete, rebuild the Blender source, rebuild the shipping Unity scene, run `validate_fan_card_guardrails.py`, pass the Unity geometry validator and fan-card EditMode tests, and regenerate the required shipping-scene previews. A failure blocks device installation.
