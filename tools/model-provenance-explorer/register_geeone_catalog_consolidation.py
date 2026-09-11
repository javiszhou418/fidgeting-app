#!/usr/bin/env python3
"""Record the 2026-09-09 catalog consolidation and the lighting-preset proposal
on the metal-three-blade manifest (rev 66 → 67).

Gate 12 rev-007 stays approved + device accepted: geometry, materials, export,
parity and the shipping lighting recipe are unchanged. Two notes only:

1. FDB-PREF-032 catalog consolidation done on the user's instruction
   “前两张图的陀螺去掉”: pointed-three-blade and gold-four-wing retired,
   migration v2 merges their progress into metal-three-blade.
2. FDB-PREF-036 lighting presets A/B/C/D proposed after “第三张的陀螺是不是
   光照太强了”; shipping stays A until the user picks.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import register_geeone_video_intake_rev6 as base

CONSOLIDATION_TEXT = "前两张图的陀螺去掉"
LIGHTING_TEXT = "第三张的陀螺是不是光照太强了，有没有柔和的一点的灯光设置，你发给我几个灯光设置，以及会对物体造成什么样的影响"
NOW = datetime.now(timezone.utc).isoformat()
SHEET = "Artifacts/GeeoneLighting/r001/r001-geeone-lighting-options-sheet.png"
SIM_SHEET = "Artifacts/LibraryDetailConsistency/r002/r002-library-detail-sheet.png"


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    s12 = {s["id"]: s for s in manifest["stages"]}["12-shipping"]
    assert s12["revision"] == 7 and s12["status"] == "approved", "expected Gate 12 rev-007 approved (manifest rev 66)"

    cs = manifest["currentState"]
    cs["catalogConsolidation"] = {
        "status": "done",
        "decidedBy": "user",
        "channel": "chat",
        "exactWording": CONSOLIDATION_TEXT,
        "decidedAt": "2026-09-09T00:31:00+00:00",
        "retiredModelIds": ["pointed-three-blade", "gold-four-wing"],
        "migration": "ProductCatalogMigration v2 (max-merge into metal-three-blade)",
        "evidence": SIM_SHEET,
    }
    cs["lightingPresetProposal"] = {
        "status": "awaiting-user-choice",
        "exactWording": LIGHTING_TEXT,
        "options": ["A studio-bright (shipping)", "B soft-studio", "C overcast-diffuse", "D low-key-metal"],
        "shipping": "A",
        "evidence": SHEET,
        "note": "Gate 12 rev-007 unchanged; choosing B/C/D will open a Gate 12 rev-008 lighting-only revision",
    }
    cs["diagnosis"] = (
        cs["diagnosis"].split("下一步：FDB-PREF-032 catalog 收敛")[0]
        + f"09-09 08:31 consolidation: 用户“{CONSOLIDATION_TEXT}”→ FDB-PREF-032 catalog 收敛完成（pointed-three-blade / gold-four-wing 退出 catalog，migration v2 取最大值迁入 GEEONE）；模拟器录屏 {SIM_SHEET}。"
        + f" | 09-09 lighting-presets: 用户“{LIGHTING_TEXT}”→ GeeoneLightingPresetCatalog A/B/C/D 对比表 {SHEET}；出货仍为 A，等用户选择。视觉批准待确认，未推送手机。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    events = [
        ("stage-note", f"FDB-PREF-032 catalog consolidation done on the user's explicit chat instruction 2026-09-09 08:31 (exact wording: {CONSOLIDATION_TEXT}); pointed-three-blade + gold-four-wing retired, ProductCatalogMigration v2 max-merges their state into metal-three-blade; simulator evidence {SIM_SHEET}; Gate 12 rev-007 unchanged"),
        ("stage-note", f"GEEONE lighting presets A/B/C/D proposed after the user's 2026-09-09 08:31 question (exact wording: {LIGHTING_TEXT}); comparison sheet {SHEET}; shipping stays A (rev-007 recipe) until the user chooses; visual approval pending, not pushed to phone"),
    ]
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for kind, note in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, "type": kind, "stageId": "12-shipping", "notes": note}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "catalogConsolidation": cs["catalogConsolidation"]["status"], "lightingPresetProposal": cs["lightingPresetProposal"]["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
