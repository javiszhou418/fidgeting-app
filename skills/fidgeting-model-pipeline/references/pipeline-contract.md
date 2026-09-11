# Fidgeting model pipeline contract

## Contents

1. Invariants
2. Twelve gates
3. Evidence model
4. Approval and invalidation
5. Standard camera IDs

## Invariants

- Use the shipping Unity product at `unity/FidgetingApp`.
- Keep existing shipping models active until their replacements finish all gates.
- Separate user input, external reference, AI target, Blender output, Unity output, and shipping evidence by asset role.
- Use repository-relative paths in manifests. Preserve originals; store annotations as normalized coordinates.
- Use `blender-cli` as the primary route for mechanical models. Use Rodin only as a concept branch.
- Treat material approval separately from geometry approval. Revalidate an approved material language on replacement geometry.
- Name materials by `id` from `unity/FidgetingApp/ArtSource/MaterialLibrary/materials.json`. Blender lookdev, Unity material factories, and concept prompts share that vocabulary; `materials.md` is generated from it. Concept images use ChatGPT Image Gen only and never become geometry or material truth.

## Twelve gates

| Gate | Required evidence | Approval question |
|---|---|---|
| 01 Intake | Original user/external references, source metadata, hashes | Did we preserve and classify the real input correctly? |
| 02 Analysis | Image/video keyword extraction, external discovery log, annotated analysis board, and source-linked claims | Did we find useful outside evidence without confusing it with user input, and understand silhouette, scale, structure, material, and unknowns correctly? |
| 03 Contract | Units, bounds, dimensions, pivot, moving/fixed parts, clearances, budgets, route | Is this the exact contract to build? |
| 04 Architecture | Part tree and exploded plan | Are the parts, hierarchy, movement, and material zones correct? |
| 05 Blockout | Deterministic source plus white-model Hero | Are silhouette, proportion, thickness, and center structure correct before detail? |
| 06 Geometry | Six orthographic views, Workbench, dimension/pivot overlays, exploded geometry | Does the same geometry pass every structural view? |
| 07 Material | Neutral PBR board and closeup | Are surface response and material boundaries correct? |
| 08 Lighting | Hero, left/right oblique, low, Beauty, Clay, Normal, Depth, Roughness | Does lighting reveal rather than hide geometry? |
| 09 Environment | Neutral and shipping environment with matching camera | Is any mismatch caused by the environment rather than the model? |
| 10 Export | Blend, FBX, GLB, collision, export manifest and hashes | Are scale, hierarchy, normals, pivot, slots, and collision preserved? |
| 11 Unity parity | Blender neutral, Unity neutral, parity report | Did Unity import alter geometry, scale, pivot, or material response? |
| 12 Shipping | Library, Hero, Top, left/right oblique, Low, Phone | Is the real shipping scene visually approved? |

## Evidence model

- `AssetRecord`: immutable file evidence with stage, slot, role, path, hash, producer, recipe, source asset/claim IDs, and optional view metadata.
- `Claim`: a measured, inferred, or unknown statement linked to source assets and optional normalized source regions.
- `StageRun`: revisioned status, artifacts, validation results, input/output digests, stale reason, and user decision.
- `Issue`: stage, asset, severity, note, optional claim IDs, and optional normalized rectangle.
- `DecisionEvent`: append-only timestamped record in `history.ndjson`.
- `ReferenceDiscovery`: extracted Chinese/English keywords, search queries, candidate references, match/conflict rationale, and a clear boundary between user input and outside exploration. A candidate is not a modeling claim until Stage 2 is approved.

Do not use an output asset as its own source. A downstream asset must reference upstream assets or claims.

Gate 03's modeling-contract asset must declare `sourceClaimIds` that consume every approved Gate 02 claim. Unknowns must be carried forward as explicit contract decisions or blockers, not silently dropped. This is an internal production constraint: the main review UI should foreground actual assets and visible problems instead of displaying the claim ledger as proof.

The twelve gates remain fixed quality boundaries, but the user-facing tool groups them into three production phases: Reference + Interaction Form (Gates 01–04), Blender Modeling + Textures (Gates 05–10), and Unity + Scene + Rendering (Gates 11–12). Foreground the current model, phase, and decision while keeping the full stable roadmap visible. Stage 02 covers interaction-form evidence and CAD; physical dimensions and hidden part counts belong to Stage 03.

The repository uses one persistent workbench. Its left model selector, current-task banner, `当前 Gate NN/12`, `已批准 X/12`, full roadmap, and seven tabs never change order by revision. The tabs are `参考原图`, `分析（截图/视频）`, `尺寸`, `交互 CAD`, `白模`, `贴图与材质`, and `Unity 灯光与成品`. Each shows current, approved, stale, rejected, or unstarted state. Rejected and stale assets remain inspectable as labeled history. Persist model, tab, gate, scroll/view state, and opened artifact across reload and browser history. Direct model/tab/gate routes override earliest-problem routing.

Mechanical Gate 02 reviews use two layers:

1. Keep complete frame manifests, crops, tracking, audio impulses, calculations, source links, and validation in internal artifacts or a collapsed `技术证据` section.
2. Make interactive CAD the default user review. Keep at most seven concrete conclusions collapsed as supplementary context.
3. Do not show a screenshot wall by default. Source thumbnails and annotated crops remain available inside the collapsed evidence layer.
4. Use measured values, inferred ranges, and unknowns as distinct labels. Use perspective-corrected normalized `L/W` and travel-over-`L` until the user supplies physical measurements. Rejected provisional millimetres must not remain current facts.
5. Gate 02 mechanical work uses reference research → structural interactive CAD → user approval. Gate 03 then locks physical dimensions and the modeling contract. A standalone hand-feel Simulator is not a Blender prerequisite.
6. Structural CAD is direct kinematics only. It covers ownership, endpoint pivot, bilateral rails, simultaneous slide/rotation, sections, tangencies, gaps, steps, and dimension sources. It must not contain damping, force feel, detent strength, inertia, sound, stop feel, or Simulator recordings.
7. Encode transform ownership explicitly. Keep fixed bodies unchanged and apply each moving body's contract transform without inventing a moving pivot. For the current slider rev 12, `BottomExterior` and `FixedAxis` are fixed; `RotatingCarrier` applies `R_fixedAxis(θ)`; `TopPlate` and its underside grooves apply `R_fixedAxis(θ)·T_local(s)`. The carrier followers share `θ`, while both bottom exterior skins remain smooth and rail-free.
8. Use an interactive vector engineering drawing for mechanical review. Synchronize top, side and relevant section views; expose a large rotation-ring hit area, zoom/pan and keyboard controls; show tangent geometry and every dimension's `实测 / 视频比例 / 用户输入 / 未知` status.
9. Keep physical fields blank until measured. Calculate a derived value only when all required inputs exist; render missing dimensions as `? / 待实测` and list the caliper, orthogonal-photo or teardown evidence needed.
   - Magnetic-slide Gate 03 requires exactly nine core values: closed overall L/W/T, top thickness, bottom thickness, maximum slide travel, fixed-axis center distance from the nearest rounded end, rotating-carrier diameter, and closed seam/gap. Every value records mm, method/source, uncertainty, and optional photo references.
   - Bilateral groove spacing/width/depth, fixed-axis diameter, upper/lower step heights, and visible follower/contact dimensions are optional for initial Blender blockout.
   - Operating clearance, manufacturing allowance, and manufacturing tolerance are manufacturing-stage unknowns. They never block initial Blender visual/mechanical modeling.
   - Check the thickness stack within combined uncertainty; fit axis/carrier inside the bottom footprint; check travel against finite grooves and MinimumOverlapDisk; show L/W outside 1.52–1.62 as a warning without overriding measurement.
10. A carrier-owned point axis must have one invariant local coordinate. Its world coordinate follows only its evidenced owner transform. When the owner is fixed, both local and world coordinates stay fixed and no axis path may be drawn. Never imply an independent axis-sliding degree of freedom without direct evidence.
11. Direct manipulation must preserve the grabbed top-local point and solve both `θ` and local `s` from the pointer. The grabbed point must move in the same screen direction as the pointer at every carrier angle, including after zoom and pan.
12. For the current slider rev 15, model `MinimumOverlapDisk` as a first-class, user-authoritative `BottomBase` child centered on `FixedAxis`. The disk is distinct from the pivot point and bottom outline. Enforce `MinimumOverlapDisk ⊆ TopPlateFootprint(s,θ)` at every valid pose. Boundary contact is legal; any exposure is invalid.
13. Keep the finite groove endpoint as one candidate bound. Derive `sMax(θ)=min(grooveEndpointLimit, overlapContainmentLimit(θ))`. For an axis-centered circular disk and `TopPlate=R_fixedAxis(θ)·T_local(s)`, inverse rotation leaves the disk unchanged, so the current capsule containment limit is angle-invariant. Recompute both bounds whenever disk radius, groove endpoint, or top proportions change. Physical disk radius and clearance remain unknown.
14. Use analytic capsule-versus-disk containment as the motion gate. Supplement it with a dense full-360 sweep at 1° or finer and continuous boundary checks. Clamp slide before negative margin; rotation at the constrained limit remains available only while containment stays valid. Render the red disk truthfully without clipping or z-order concealment, and flash exposed red only for internal forced-invalid diagnostics.
15. Keep original mechanism references one click from the default review. Provide a top-level `原图与拆解参考` view beside conclusions and interactive CAD, with user videos, official same-model images, external candidates, original URLs, repository paths and full-source actions. Keep tracking math collapsed separately.
16. Gate 02 must emit one schema-backed `mechanism-evidence-contract.json`. Every constraint records its value/range, normalized units, evidence state, confidence, source asset IDs, frame/PTS regions, decision note, and downstream consumers. The default review shows how each conclusion was applied and a compact source→constraint coverage matrix.
17. CAD, Blender, Unity, Haptics, tests, and shipping-review artifacts must record the approved evidence-contract SHA-256. They must load values from that contract; copied mechanism defaults are forbidden and drift validation must fail closed.

## Approval and invalidation

- Text summaries and static screenshots are supplementary only. Required interactive evidence must exist before approval is requested.
- Final approval authority is the user's latest explicit instruction in chat. Approval may be given in the workbench or in chat; the latest explicit chat decision overrides stale or conflicting tool state and must be persisted with its exact wording.
- Gates 02–06 require interactive CAD/3D; a complete interaction recording is the fallback only when interaction is unavailable.
- Gates 07–09 require interactive lookdev or a real render turntable/comparison recording. Gate 10 requires real GLB interaction. Gates 11–12 require real Unity simulator/runtime preview or a complete recording.
- Disable tool approval controls until required interaction/viewing milestones complete. The button is optional after valid evidence exists. Approval events record artifact SHA-256, contract SHA-256, parameter snapshot, completed checklist, interaction mode, exact chat wording when applicable, and browser/device timestamp.
- Gate 02 CAD approval closes the interaction-form decision. Gates 03–04 and required physical dimensions must complete before Blender. Old standalone Simulator drafts remain internal/superseded; a simulator may be requested later for Unity interaction validation.
- Approve only when the previous gate is approved, every required slot exists and is hashed, every validation passes, and the stage is not stale.
- Gate 03 is not ready until its contract assets consume every Gate 02 claim through `sourceClaimIds` and the required physical dimensions are supplied.
- The user's latest explicit chat decision may authorize a separate provisional Gate 03 contract from hash-linked prior dimensions. Every reused value stays `user-authorized-provisional`, never measured; unknown engineering values remain unknown, and the authorization cannot exceed its stated gate scope.
- Rejecting a gate preserves its artifacts and marks downstream non-empty stages stale.
- Changing a known asset hash invalidates its stage and every downstream stage.
- A legacy artifact is visible evidence, not an approval.
- Stage 12 approval is a visual shipping gate, not device acceptance. Installation and iPhone acceptance remain separate.

## Standard camera IDs

- Orthographic: `front`, `back`, `top`, `bottom`, `left`, `right`.
- Perspective: `hero`, `left-oblique`, `right-oblique`, `low`.
- Shipping: `library`, `hero`, `top`, `left-oblique`, `right-oblique`, `low`, `phone`.
- Compare Blender and Unity only when `view.id` and the camera recipe match. Otherwise show side by side without claiming a geometric image diff.
