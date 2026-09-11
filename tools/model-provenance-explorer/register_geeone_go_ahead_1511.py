"""User 2026-09-08 15:11 "继续吧" after the un-stretched Gate 12 shipping previews (14:56 stretch report fixed and re-captured).

Persists the exact wording as the chat approval of Gate 10 rev-002 (export; real GLB + orbit recording), Gate 11 rev-002
(Unity parity; contact sheet + report) and Gate 12 rev-006 (shipping previews). Approval of the previews authorises the
device build / install that follows; device acceptance stays pending until the user validates on the iPhone.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import register_geeone_video_intake_rev6 as base

NOW = datetime.now(timezone.utc).isoformat()
USER_TEXT = "继续吧"
EVIDENCE = {
    "10-export": "chat approval; evidence: export-validation.json (GLB/FBX round-trip 9/9), review/glb-orbit-review.mp4 of the real exported GLB, glb-hero/low/top renders; no interactive viewer",
    "11-unity-parity": "chat approval; evidence: unity-parity-contact-sheet.png (silhouette IoU top 0.998 / hero 0.995), parity-report.json PASS, unity-import-parity-report.json",
    "12-shipping": "chat approval after the re-captured (un-stretched) shipping-review-contact-sheet.png: phone / hero / top / left / right / low / library from ThreeBladeMetalOriginal.unity",
}


def approve(stage, notes, evidence):
    stage["status"] = "approved"
    stage["decision"] = {"action": "approve", "notes": notes, "decidedBy": "user", "decidedAt": NOW, "channel": "chat", "exactWording": USER_TEXT, "evidenceMode": evidence}
    stage.setdefault("historicalDecisions", []).append({"revision": stage["revision"], "decision": "approved", "decidedAt": NOW, "decidedBy": "user", "channel": "chat", "exactWording": USER_TEXT, "evidenceMode": evidence, "notes": notes})
    stage["validations"] = [v for v in stage.get("validations", []) if v["id"] not in ("user-glb-review", "user-review", "visual-approval")] + [{"id": "approval-evidence-mode", "status": "warn", "detail": evidence}]


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    st = {s["id"]: s for s in manifest["stages"]}
    assert st["10-export"]["revision"] == 2 and st["11-unity-parity"]["revision"] == 2 and st["12-shipping"]["revision"] == 6
    approve(st["10-export"], "用户 15:11“继续吧”。批准 rev-002 导出包（FBX/GLB/collision，米制，Rotor_Root / Fixed_Root）。", EVIDENCE["10-export"])
    approve(st["11-unity-parity"], "用户 15:11“继续吧”。批准 rev-002 Unity 对齐（IoU 0.998 / 0.995，转子转 / 盖 + 毂芯静）。", EVIDENCE["11-unity-parity"])
    approve(st["12-shipping"], "用户 15:11“继续吧”（在 14:56 拉伸修复后的出货预览之后）。批准 rev-006 出货预览；随即执行设备 build / 安装。真机验收另计。", EVIDENCE["12-shipping"])
    st["12-shipping"]["validations"] = [v for v in st["12-shipping"]["validations"] if v["id"] != "device-acceptance"] + [{"id": "device-acceptance", "status": "pending", "detail": "build / install running after the 15:11 approval; user validation on the iPhone pending"}]
    manifest["currentState"]["visualApproval"] = "gate12-shipping-preview-approved-2026-09-08-1511"
    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-08 15:11 go-ahead:")[0]
        + " | 09-08 15:11 go-ahead: 用户“继续吧”→ Gate 10 rev-002 / 11 rev-002 / 12 rev-006 approved（chat）→ 12/12。开始设备交付（scripts/device_delivery_geeone_tri_spinner.sh）；真机验收待用户确认。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for sid in ("10-export", "11-unity-parity", "12-shipping"):
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, "type": "stage-approved", "stageId": sid, "notes": f"{sid} rev-{st[sid]['revision']:03d} approved by the user's explicit chat instruction 2026-09-08 15:11 (exact wording: {USER_TEXT}); evidence mode: {EVIDENCE[sid]}"}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "statuses": {s["id"]: s["status"] for s in manifest["stages"]}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
