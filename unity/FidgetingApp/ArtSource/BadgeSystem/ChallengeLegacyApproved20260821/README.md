# Challenge + Legacy Badge Asset Handoff

Status: visual direction approved by the user on 2026-08-21; shipping integration and device acceptance are still pending.

This package is the implementation handoff for all 40 existing Badge IDs. It keeps the approved visual language consistent across Toy, Collector, Challenge, Cycle, and Legacy achievements:

- upright rounded hexagon with top and bottom points;
- broad cold pearl-silver satin frame and continuous bevel;
- graphite transition lip, deep sloped recess, and dark fine-grain leather well;
- thick pearl-silver icon with a dark physical sidewall and upper-left softbox reflection;
- runtime token and name outside the badge;
- bright polished unlocked state and graphite locked state.

## Package layout

- `contact-sheets/`: five approved 1:1 visual references, eight badges per sheet.
- `png-1024/unlocked/`: 40 transparent sRGB PNG files for the unlocked state.
- `png-1024/locked/`: 40 transparent sRGB PNG files for the locked-state reference.
- `badge-asset-manifest.json`: stable Badge ID, token, short name, scope, category, grade, contact-sheet cell, and asset path.
- `validation-report.json`: count, size, color-profile, alpha-connectivity, stable-ID, and duplicate-hash checks.
- `CLAUDE_CODE_HANDOFF.md`: shipping integration sequence and visual gates.

The generated PNGs contain the badge shell and icon only. Do not bake the milestone token, achievement name, progress bar, acquired date, or user data into the image.

Regenerate the package from the approved Cowart source sheets with:

```sh
python3 unity/FidgetingApp/Tools/BadgeAssetGenerator/package_approved_badge_concepts.py \
  --repo-root "/Users/jiawei.zhou/Documents/Fidgeting app"
```
