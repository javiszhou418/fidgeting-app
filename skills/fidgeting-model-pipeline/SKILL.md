---
name: fidgeting-model-pipeline
description: Enforce the Fidgeting App 12-gate reference-to-Blender-to-Unity model workflow with source-linked claims, immutable revisions, visual approvals, standard-view capture, export validation, and downstream invalidation. Use whenever Codex creates, rebuilds, imports, changes, reviews, or approves a Fidgeting 3D model, geometry, proportions, pivot, hierarchy, material, lighting, camera, Blender source, FBX/GLB export, Unity scene representation, or shipping preview.
---

# Fidgeting Model Pipeline

Treat the per-model `pipeline.json` as the authority for modeling progress. Do not infer approval from the existence of files, a successful build, or a historical screenshot.

## Start every model task

1. Read the repository `AGENTS.md` and `unity/FidgetingApp/ArtSource/ModelPipeline/<model-id>/pipeline.json`.
2. Read [references/pipeline-contract.md](references/pipeline-contract.md) completely.
3. Run `node tools/model-provenance-explorer/validate-pipelines.mjs`.
4. Resume at the earliest stage whose status is not `approved`. Do not work around an upstream `missing`, `rejected`, or `stale` stage.
5. For the magnetic fan card, also load `fan-card-modeling-guardrails` and obey its stricter geometry contract.

## Execute the route

- Use Blender/CLIAnything or a deterministic `bpy` builder as the primary route for mechanical models.
- Keep Rodin in an explicit `concept-only` branch. Preserve raw and cleanup artifacts separately. Never promote a Rodin result directly into stage 10 or Unity.
- Record every artifact with a repository-relative path, SHA-256, producer/version, recipe or command, stage slot, source asset IDs, and camera/view metadata where applicable.
- Record every dimensional or visual assertion as a claim linked to source assets and normalized source-image regions. Mark unsupported values `unknown`; never reverse-engineer a locked dimension from a Unity screenshot.

## Stop at every gate

- Generate only the current gate's required artifacts.
- Refresh hashes through the local workflow app or `node tools/model-provenance-explorer/validate-pipelines.mjs --refresh`.
- Run gate-specific validation and show the real artifact to the user.
- Stop and obtain explicit user approval after the required interactive evidence exists. Approval may be given in the workbench or in chat. The user's latest explicit chat instruction is final and overrides stale tool state; persist its exact wording through workflow history.
- Text and static screenshots are supplementary only. Mechanical/geometry approval requires interactive CAD/3D or a complete fallback recording. Material/lighting/environment requires interactive lookdev or a real turntable/comparison recording. Export requires real GLB interaction. Unity/shipping requires a real Unity runtime preview or complete recording.
- Keep tool approval disabled until the required interaction/viewing checklist is complete, but do not require the button after valid evidence exists. Record artifact hash, contract hash, parameter snapshot, completed checklist, interaction mode, exact chat wording when applicable, and timestamp.
- Keep exactly 12 gates grouped into three user-facing phases: reference + interaction form (Gates 01–04) → Blender modeling + textures (Gates 05–10) → Unity + scene + rendering (Gates 11–12).
- Structural CAD is kinematic only. It may show slide and rotation, but it must not expose damping, force, detent strength, inertia, sound, stop feel, or Simulator recordings.
- Approved interaction-form CAD feeds Gate 03–04 contracts. Blender starts only after those gates and required physical dimensions are complete; no standalone Simulator is required first.
- Preserve old Simulator drafts as internal/superseded. A simulator may be created later only as a requested Unity interaction-validation tool.
- For magnetic-slide Gate 03, require exactly nine core measurements: closed L/W/T, top and bottom thickness, max travel, fixed-axis offset from the nearest rounded end, rotating-carrier diameter, and closed seam/gap. Record mm, method/source, and uncertainty.
- The user's latest explicit chat decision may instead authorize a provisional Gate 03 modeling contract from hash-linked prior values. Label every reused value `user-authorized-provisional`, never measured; preserve unknown engineering dimensions and the exact authorized scope.
- Groove details, axis diameter, step heights, and visible follower dimensions are optional. Operating clearance, allowance, and tolerance remain manufacturing-stage unknowns and do not block initial Blender.
- Preserve rejected artifacts and create a new revision. Never overwrite evidence from a rejected or approved round.
- When an upstream source, claim, or artifact changes, mark that stage and all downstream stages `stale` before continuing.

## Keep one stable workbench

- Use one repository workbench. Do not create revision-specific navigation or replace its information architecture.
- Keep the model selector, current-task banner, progress counters, 12-gate roadmap, and seven fixed user tabs visible.
- The tabs stay ordered as references, analysis, dimensions, interactive CAD, white model, materials, then Unity finished work.
- Label current, approved, stale, rejected, and unstarted tabs. Keep rejected and stale artifacts available as labeled history.
- Persist model, tab, gate, scroll/view state, and opened artifact. Support reload, browser Back/Forward, and direct URL restoration.
- Explicit model/tab/gate routes override earliest-problem routing. Content may version; navigation labels and order may not.

## Capture truthful Blender views

Run:

```bash
python3 skills/fidgeting-model-pipeline/scripts/capture_standard_views.py \
  --blend /absolute/path/model.blend \
  --output /absolute/path/to/revision/fixed-views
```

The wrapper probes `cli-anything-blender` but always requires real Blender renders for the fixed camera pack. It falls back to the bundled `bpy` capture script when the installed CLI lacks `preview`. Inspect the returned PNG paths; never infer visual quality from scene JSON.

## Validate before handoff

- Run `npm --prefix tools/model-provenance-explorer test`.
- Run `node skills/fidgeting-model-pipeline/scripts/validate_model_pipeline.mjs <model-id>`.
- Update `Docs/IMPLEMENTATION_STATUS.md` with code, tests, real preview paths, and the approval-pending state.
- Update the design bible in the same task when the user approves, rejects, supersedes, or changes a product decision.
- Do not build or install a visual change on a phone until stage 12 has explicit visual approval. Keep device acceptance separate.
