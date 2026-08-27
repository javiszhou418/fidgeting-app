# Claude Code shipping handoff

Use `badge-asset-manifest.json` as the only mapping authority. Do not infer Badge IDs from visible text or reorder assets alphabetically.

## Required implementation order

1. Import the 40 files from `png-1024/unlocked/` without resizing, recoloring, or adding text.
2. Bind each file to its existing `badge_id` from the manifest. Do not create a second Badge catalog or change thresholds, XP, fragments, migration, UTC cycles, or reward idempotency.
3. Keep milestone token and short name outside the hexagon, at most two lines. Keep the progress bar below those two lines.
4. Render the catalog as three columns with 1:1 artwork and equal optical padding. Preserve existing VoiceOver labels and Dynamic Type behavior.
5. Prefer one runtime locked-state treatment derived from the unlocked asset. The files in `png-1024/locked/` are the approved tonal reference and may be used directly only if the current renderer cannot reproduce it consistently.
6. Generate real shipping SwiftUI previews for catalog, detail, Locked, In Progress, Hidden, Unlocked, and 1080 × 1080 share card states.
7. Verify small-screen three-column legibility, Reduce Motion, Reduce Transparency, memory/cache limits, and that every one of the 40 stable IDs resolves exactly once.
8. Update `Docs/IMPLEMENTATION_STATUS.md` with code, test, and preview evidence.

## Release gate

The concept direction is approved, but these extracted files have not yet been approved inside the real shipping UI. Do not build or install to the user's iPhone until the user explicitly approves previews captured from the shipping native implementation. Building a local Simulator preview for review is allowed and required.

Relevant requirements: `FDB-BDG-006`, `FDB-BDG-007`, and `FDB-BDG-010` in `Docs/FidgetingAppProductDesignBible.md`.

