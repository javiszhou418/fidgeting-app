#!/usr/bin/env python3
"""Record the specified-only Unity reflection plan without changing Unity."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[7]
MANIFEST = REPO / "unity/FidgetingApp/Packages/manifest.json"
PACKAGE_LOCK = REPO / "unity/FidgetingApp/Packages/packages-lock.json"
MOBILE_PIPELINE = REPO / "unity/FidgetingApp/Assets/Settings/Mobile_RPAsset.asset"
OUTPUT = ROOT / "unity-reflection-plan.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    package_manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    package_lock = json.loads(PACKAGE_LOCK.read_text(encoding="utf-8"))
    mobile = MOBILE_PIPELINE.read_text(encoding="utf-8")
    urp_manifest = package_manifest["dependencies"]["com.unity.render-pipelines.universal"]
    urp_lock = package_lock["dependencies"]["com.unity.render-pipelines.universal"]["version"]
    capabilities = {
        "reflectionProbeBlending": "m_ReflectionProbeBlending: 1" in mobile,
        "reflectionProbeBoxProjection": "m_ReflectionProbeBoxProjection: 1" in mobile,
        "reflectionProbeAtlas": "m_ReflectionProbeAtlas: 1" in mobile,
    }
    checks = {
        "urp175Confirmed": urp_manifest == urp_lock == "17.5.0",
        "mobileReflectionProbeFeaturesEnabled": all(capabilities.values()),
        "noUnityFilesModified": True,
        "deliveryStateSpecifiedOnly": True,
        "verificationDeferredToGate09And11": True,
        "deviceAcceptancePending": True,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "08-lighting",
        "question": "Can the silver mirror body reflect the Unity scene?",
        "answer": "Yes, approximately. URP reflection probes and the skybox/HDRI provide cubemap-based environment reflections. This is not ray-traced or per-pixel true mirror reflection.",
        "decisionState": "specified",
        "deliveryState": "specified-only-not-integrated",
        "canonicalUnityProject": "unity/FidgetingApp",
        "renderPipeline": {
            "name": "Universal Render Pipeline",
            "version": "17.5.0",
            "manifestPath": str(MANIFEST.relative_to(REPO)),
            "manifestSha256": sha256(MANIFEST),
            "packageLockPath": str(PACKAGE_LOCK.relative_to(REPO)),
            "packageLockSha256": sha256(PACKAGE_LOCK),
        },
        "mobilePipelineAsset": {
            "path": str(MOBILE_PIPELINE.relative_to(REPO)),
            "sha256": sha256(MOBILE_PIPELINE),
            "capabilities": capabilities,
        },
        "laterUnityStrategy": {
            "silverBody": [
                "Use local reflection probes for nearby scene response.",
                "Blend with the scene skybox or HDRI cubemap.",
                "Use box projection for bounded interiors where appropriate.",
                "Update realtime probes only when scene changes require it, not every frame.",
            ],
            "reflectionType": "approximate-cubemap-reflection",
            "notSupportedClaim": "not-ray-traced-and-not-per-pixel-true-mirror",
            "crystal": "Transmission and iridescence require a URP Shader Graph or custom approximation.",
        },
        "verification": {
            "Gate09": "Verify neutral and shipping environment contribution with matching cameras.",
            "Gate11": "Verify Blender-versus-Unity material and reflection parity.",
            "deviceAcceptance": "pending",
        },
        "scope": {
            "unityFilesChanged": False,
            "runtimeImplemented": False,
            "reflectionProbesCreated": False,
            "shaderGraphImplemented": False,
            "hapticsChanged": False,
            "buildOrInstallPerformed": False,
        },
        "checks": checks,
        "pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Unity reflection plan validation failed.")


if __name__ == "__main__":
    main()
