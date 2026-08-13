---
name: fan-card-modeling-guardrails
description: Prevent repeated geometry, layering, artwork, track-clearance, and preview regressions in the Fidgeting App magnetic fan-card model. Use whenever Codex creates or modifies the Fan Card Blender source, FBX, Unity scene builder, card geometry, back track, magnets, face A/Q/K and spade artwork, rank-pattern presentation, materials, camera composition, interaction hierarchy, or model previews, and before reporting or installing any Fan Card visual change.
---

# Fan Card Modeling Guardrails

Treat previously approved constraints as hard tests, not context to remember informally. A new detail must never silently reintroduce an old defect.

## Required workflow

1. Locate the repository root and read completely:
   - `AGENTS.md`
   - `PRODUCT_PLAN.md`
   - `unity/FidgetingApp/Docs/FanCardModelingGuardrails.md`
   - the current Fan Card section of `unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md`
2. State which locked invariants the requested change could affect. Include track clearance, card thickness/gaps, pivot, fixed/moving layers, front/back visibility, and artwork parenting even if the user asked about only one new detail.
3. Run before editing:

   ```bash
   python3 unity/FidgetingApp/ArtSource/FanCard/validate_fan_card_guardrails.py --source-only
   ```

   If the baseline already fails, record the failure and include its repair in scope. Do not build on top of it silently.
4. Author manufactured geometry and font relief in Blender. Use Unity only for import, material assignment, assembly, interaction, and shipping validation.
5. Before adding or changing a coordinate, edit `fan_card_guardrails.json` first, then synchronize C#, Blender, scene generation, tests, and docs. Never introduce an unvalidated duplicate default.
6. Run source-only validation again before exporting Blender assets. A failure blocks export.
7. Rebuild the Blender `.blend`/FBX and shipping Unity scene. Then run the full guardrail validator, Unity `CardGeometryValidator`, and `FanCardAcceptanceTests`.
8. Generate shipping Unity top, hero, left/right oblique, low-angle, back, track-closeup, and changed-detail previews. Compare every old invariant, not only the new detail.
9. Update `IMPLEMENTATION_STATUS.md` with code, scene, test, preview, and approval state.
10. Do not claim completion or install to a device while any guardrail fails or visual approval is pending.

## Non-negotiable checks

- Keep the complete back-track outer contour at least `6.0 mm` from the card outline. “Looks inset” is not evidence.
- Keep the track on the back, internally biased toward the lower-left, and invisible from front/hero interaction views.
- Keep `BottomCard` fixed; rotate `MiddleCard` to `45°q` and `TopCard` to `90°q`.
- Parent every visible mark directly to its own rigid slab. Keep two standard playing-card corner indices per front: an upright Oxanium 700 active rank with a same-facing small spade at upper-left, and the same pair rotated 180 degrees at lower-right. Author A/Q/K as Blender relief meshes and swap only each rank mark's `MeshFilter`; never stack renderers or reparent marks between cards. Keep all corner-index artwork off the back.
- Allow exactly two whole-set face states: `AAA`, or bottom/middle/top `Q/K/A`. Select them 50/50 on each detail-page entry. Never randomize the three layers independently, never mismatch the two corners of one card, and never let a rank switch change transforms, colliders, detent state, audio, or Haptic events.
- Preserve three rigid slabs, real thickness, two air gaps, common through-hole, and no interpenetration.
- Preserve four detents, the 45-degree track, physics/Haptic shared semantics, and user-input authorization unless the user explicitly requests a mechanics change.
- Reject new floating rings, duplicated artwork, procedural fake holes, or geometry made only to pass one camera angle.

## Failure behavior

When a check fails, stop the visual push, report the exact failed invariant and measured value, and repair from the canonical JSON. Never weaken or delete an old test to make a new edit pass. Ask the user only if satisfying the new request requires changing a locked invariant.

The repository document is authoritative for numeric values and preview requirements. Do not copy alternate numbers into this skill.
