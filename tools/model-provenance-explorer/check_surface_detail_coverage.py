"""Gate 05/06 gate-keeper: every `mustBeGeometry` detail in the Gate 02 surface
detail spec must be implemented and tagged in the Blender builder.

Usage:
    python3 check_surface_detail_coverage.py <builder.py> [--spec <spec.json>] [--json]

The builder tags the code that produces a detail with a comment `# detail: UTS-D05`
(several ids may share one line). Exit code 1 when any required id is missing,
so registration scripts for Gate 05/06 can refuse to proceed.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path("/Users/jiawei.zhou/Documents/Fidgeting app")
DEFAULT_SPEC = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/metal-three-blade/evidence/02-analysis/rev-006/surface-detail-spec.json"
TAG = re.compile(r"#\s*detail:\s*([A-Z]+-D\d+(?:\s*,\s*[A-Z]+-D\d+)*)")


def coverage(builder: Path, spec_path: Path) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    required = [d["id"] for d in spec["details"] if d.get("mustBeGeometry")]
    text = builder.read_text(encoding="utf-8") if builder.exists() else ""
    tagged = set()
    for match in TAG.finditer(text):
        for token in match.group(1).split(","):
            tagged.add(token.strip())
    missing = [d for d in required if d not in tagged]
    return {
        "builder": str(builder), "spec": str(spec_path), "specRevision": spec.get("revision"),
        "required": required, "tagged": sorted(tagged & set(required)), "missing": missing,
        "coverage": f"{len(required) - len(missing)}/{len(required)}", "pass": not missing,
    }


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    builder = Path(args[0])
    spec = Path(args[args.index("--spec") + 1]) if "--spec" in args else DEFAULT_SPEC
    report = coverage(builder, spec)
    if "--json" in args:
        print(json.dumps(report, indent=2))
    else:
        print(f"surface detail coverage {report['coverage']} for {builder.name} (spec rev {report['specRevision']})")
        for d in report["missing"]:
            print(f"  MISSING {d}")
    sys.exit(0 if report["pass"] else 1)


if __name__ == "__main__":
    main()
