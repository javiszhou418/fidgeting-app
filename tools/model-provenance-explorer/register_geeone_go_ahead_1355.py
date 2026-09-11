"""User 2026-09-08 13:55 "继续吧" after the kinematic-split review (kinematic-review-board.png, rotor-only spin recording,
turntable). Persists the exact wording as the chat approval of Gate 04 rev-006 (kinematic split architecture), Gate 06 rev-008
(rotor bore + static Hub_Core) and Gate 07/08/09 rev-005 (approved materials re-rendered on rev-008). Nothing downstream
is approved; Gate 10 export starts after this.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import register_geeone_video_intake_rev6 as base

NOW = datetime.now(timezone.utc).isoformat()
USER_TEXT = "继续吧"
EVIDENCE = "chat approval after kinematic-review-board.png (Cycles half sections, junction macro, spin frame), rotor-only spin recording (24 frames) and the 36-frame turntable; no interactive 3D viewer"


def approve(stage, notes):
    stage["status"] = "approved"
    stage["decision"] = {"action": "approve", "notes": notes, "decidedBy": "user", "decidedAt": NOW, "channel": "chat", "exactWording": USER_TEXT, "evidenceMode": EVIDENCE}
    stage.setdefault("historicalDecisions", []).append({"revision": stage["revision"], "decision": "approved", "decidedAt": NOW, "decidedBy": "user", "channel": "chat", "exactWording": USER_TEXT, "evidenceMode": EVIDENCE, "notes": notes})
    stage["validations"] = [v for v in stage.get("validations", []) if v["id"] not in ("visual-approval-pending", "user-confirmation-pending")] + [{"id": "approval-evidence-mode", "status": "warn", "detail": EVIDENCE}]


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    st = {s["id"]: s for s in manifest["stages"]}
    assert st["04-architecture"]["revision"] == 6 and st["06-geometry"]["revision"] == 8
    approve(st["04-architecture"], "用户 13:55“继续吧”（在看过运动学拆分评审板 + 转子单独旋转录像后）。批准 rev-006：静止 = Cap_Top + Cap_Bottom + Hub_Core；转动 = Rotor_Body（通孔 R0.425 R，绕 Z）；盖缘外悬毂 0.075 R。")
    approve(st["06-geometry"], "用户 13:55“继续吧”。批准 rev-008 几何：转子通孔 + 静止毂芯，20 项检查全过（含 8 项运动学）。bore / hub / gap / overhang 仍 provisional。")
    for sid in ("07-material", "08-lighting", "09-environment"):
        assert st[sid]["revision"] == 5
        approve(st[sid], "用户 13:55“继续吧”。批准 rev-005（材质 / 灯光 / 环境与 rev-004 一致，几何 rev-008）。")
    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-08 13:55 go-ahead:")[0]
        + " | 09-08 13:55 go-ahead: 用户“继续吧”→ Gate 04 rev-006 / 06 rev-008 / 07/08/09 rev-005 approved（chat；半剖 + spin + 转台录像）。进入 Gate 10 导出。未 build、未安装；视觉批准待确认，未推送手机。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for sid in ("04-architecture", "06-geometry", "07-material", "08-lighting", "09-environment"):
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, "type": "stage-approved", "stageId": sid, "notes": f"{sid} rev-{st[sid]['revision']:03d} approved by the user's explicit chat instruction 2026-09-08 13:55 (exact wording: {USER_TEXT}); evidence mode: {EVIDENCE}"}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "statuses": {s["id"]: s["status"] for s in manifest["stages"]}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
