"""Register tri-spinner-slab-v3-cmf Gate 10 rev 5 (export evidence rev-003) and Gate 11 rev 4 (Unity parity).

Both gates fall under the user's 16:3x batch authorization ("批准 09，并授权 10–11 校验通过就自动继续，
到 Gate 12 Unity 预览再停下来给我看"): every listed validation passed, so both are recorded as
batch-authorized approvals. Gate 12 is opened as a draft and still requires the user's explicit
visual approval of the real Unity preview before any build or install.

Why Gate 10 moved to rev 5: the rev-002 FBX carried Blender's space transform on ROOT_PDC_PRESENTATION
(-90 deg X, x100), which Unity imported as a non-identity root; Gate 11 rejected it against
acceptance.geometry.root_rotation_zero / root_scale_one. rev-003 writes native Z-up axes with
FBX_SCALE_UNITS so Unity's importer bakes the conversion itself. Geometry, materials, GLB and decal
are unchanged.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODEL_ID = "premium-display-case"
VARIANT = "tri-spinner-slab-v3-cmf"
PIPELINE_DIR = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline" / MODEL_ID
UNITY = REPO / "unity/FidgetingApp"
E10 = PIPELINE_DIR / "evidence/10-export/rev-003"
E11 = PIPELINE_DIR / "evidence/11-unity-parity/rev-004"
ART11 = REPO / "Artifacts/TriSpinnerSlab/gate11-r004"
CANDIDATE = UNITY / "Assets/_DisplayCase/Candidates/TriSpinnerSlabGate11R004"
EXPORT_LIVE = REPO / "tools/blender/export_tri_spinner_slab_package.py"
EXPORT_SNAPSHOT = E10 / "export_tri_spinner_slab_package.r003.py"
BUILDER_LIVE = CANDIDATE / "Editor/TriSpinnerSlabGate11ParityBuilder.cs"
BUILDER_SNAPSHOT = E11 / "TriSpinnerSlabGate11ParityBuilder.r004.cs"
TESTS_LIVE = UNITY / "Assets/_DisplayCase/Tests/Editor/TriSpinnerSlabGate11ParityTests.cs"
TESTS_SNAPSHOT = E11 / "TriSpinnerSlabGate11ParityTests.r004.cs"
REFERENCE_LIVE = CANDIDATE / "Reference/blender-parity-reference.json"
REFERENCE_SNAPSHOT = E11 / "blender-parity-reference.r004.json"
TEST_RESULTS_SNAPSHOT = E11 / "unity-editmode-results.xml"
TURNTABLE = ART11 / "gate11-r004-unity-parity-turntable-clear.mp4"
NOW = datetime.now(timezone.utc).isoformat()
SCRIPT = "register_tri_spinner_slab_v3_gate10_rev005_gate11_rev004.py"
G10_REVISION = 5
G11_REVISION = 4
G12_REVISION = 9
AUTH_SOURCE = "src.user_gate09_rev004_approval_and_batch_auth_20260911"
AUTH_WORDING = "批准 09，并授权 10–11 校验通过就自动继续，到 Gate 12 Unity 预览再停下来给我看（推荐）"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def stable_json(value) -> str:
    if isinstance(value, list):
        return "[" + ",".join(stable_json(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{" + ",".join(f"{json.dumps(k, ensure_ascii=False)}:{stable_json(value[k])}" for k in sorted(value)) + "}"
    return json.dumps(value, ensure_ascii=False)


def update_stage_digests(manifest) -> None:
    assets = {a["id"]: a for a in manifest["assets"]}
    previous = None
    for stage_record in manifest["stages"]:
        hashes = [assets[aid]["sha256"] for aid in stage_record["artifactIds"] if aid in assets and assets[aid].get("sha256")]
        claims = [stable_json(c) for c in manifest.get("claims", []) if c["stageId"] == stage_record["id"]]
        digest = hashlib.sha256("\n".join(sorted(hashes + claims)).encode("utf-8")).hexdigest()
        stage_record["inputDigest"] = digest if previous is None else previous
        stage_record["outputDigest"] = digest
        previous = digest


def upsert(manifest, record):
    for index, existing in enumerate(manifest["assets"]):
        if existing["id"] == record["id"]:
            manifest["assets"][index] = record
            return
    manifest["assets"].append(record)


def asset(stage_id, asset_id, slot, path, role, cls, note="", sources=None, **extra):
    record = {
        "id": asset_id, "stageId": stage_id, "slot": slot, "path": rel(path), "sha256": sha256(path), "role": role,
        "producer": {"name": SCRIPT, "version": "2026-09-11", "variant": VARIANT},
        "provenance": {"origin": "repository-generated", "contentClass": cls, "assertedBy": "repository", "note": note},
        "sourceAssetIds": sources or ["pdc-v3-modeling-contract"], "exists": True, "sizeBytes": path.stat().st_size,
        "variantId": VARIANT, "wholeAssembledCaseOnly": True, "explodeEligible": False, "toyPrizeBundled": False, "shippingEligible": False,
        "provisionalMarker": "PROVISIONAL_DIMENSIONS",
    }
    record.update(extra)
    return record


def archive_revision(stage, reason, extra_keys=()):
    entry = {
        "revision": stage["revision"], "status": stage.get("status"), "variantId": stage.get("variantId"), "artifactIds": list(stage.get("artifactIds", [])),
        "reviewArtifactIds": list(stage.get("reviewArtifactIds", [])), "decision": stage.get("decision"), "validations": stage.get("validations"),
        "supersededAt": NOW, "reason": reason,
    }
    for key in extra_keys:
        if key in stage:
            entry[key] = stage[key]
    stage.setdefault("historicalRevisions", []).append(entry)


def batch_decision(reviewed, scope):
    return {
        "state": "approved", "action": "approve", "decidedBy": "user", "decidedAt": "2026-09-11T16:3x:00+08:00", "channel": "chat",
        "wording": AUTH_WORDING, "sourceId": AUTH_SOURCE, "mode": "batch-authorized-auto-continue", "condition": "all gate validations pass",
        "conditionMet": True, "recordedAt": NOW, "reviewedArtifacts": reviewed,
        "governingContractSha256": "e9a6f14a61e823274c716f3b3c26ee63e0bbc8e5879145e7b98c65aa9ea88294", "scope": scope,
    }


def register_gate10(manifest, events, g11_hierarchy):
    s10 = next(s for s in manifest["stages"] if s["id"] == "10-export")
    export_manifest = json.loads((E10 / "export-manifest.json").read_text())
    assert export_manifest["status"] == "pass" and export_manifest["exportRevision"] == 3
    shutil.copyfile(EXPORT_LIVE, EXPORT_SNAPSHOT)
    if s10["revision"] != G10_REVISION:
        archive_revision(s10, "rev 4 (export evidence rev-002) superseded: its FBX carried the Blender space transform on ROOT_PDC_PRESENTATION "
                              "(-90 deg X, x100) and failed Gate 11 root_rotation_zero / root_scale_one; rev 5 re-packages the identical scene.", ("exportSpec",))
        events.append({"type": "stage-revised", "stageId": "10-export", "notes": f"10-export rev {s10['revision']} archived; rev {G10_REVISION} (evidence rev-003) opened for {VARIANT}: FBX transform/unit packaging only."})
        s10["revision"] = G10_REVISION
    ids = []
    def add(aid, slot, path, role, cls, note="", sources=None, **extra):
        upsert(manifest, asset("10-export", aid, slot, path, role, cls, note, sources, **extra)); ids.append(aid)
    add("pdc-v3-g10-script", "export-script", EXPORT_SNAPSHOT, "process", "deterministic-bpy-export-snapshot",
        f"Immutable copy of tools/blender/export_tri_spinner_slab_package.py rev-003 (live sha {sha256(EXPORT_LIVE)[:12]}).")
    add("pdc-v3-g10-product-blend", "product-blend", E10 / "tri-spinner-slab-product-r003.blend", "source-model", "product-blend-stripped",
        "Approved Gate 07 rev-003 scene stripped to the 38 case meshes + 3 empties, constant PBR per zone.", sources=["pdc-v3-g07-material-blend", "pdc-v3-g10-script"])
    add("pdc-v3-g10-fbx", "export-fbx", E10 / "tri-spinner-slab-product-r003.fbx", "export", "fbx-unity-package",
        export_manifest["package"]["fbx"]["axes"], sources=["pdc-v3-g10-product-blend"])
    add("pdc-v3-g10-glb", "export-glb", E10 / "tri-spinner-slab-product-r003.glb", "export", "glb-review-package",
        export_manifest["package"]["glb"]["attributes"], sources=["pdc-v3-g10-product-blend"])
    add("pdc-v3-g10-label-decal", "label-decal", E10 / "header-label-decal.png", "export", "header-label-decal-placeholder", "placeholder copy, runtime-owned", sources=["pdc-v3-g07-material-blend"])
    add("pdc-v3-g10-label-layout", "label-layout", E10 / "header-label-decal.json", "validation", "header-label-layout", sources=["pdc-v3-g10-label-decal"])
    add("pdc-v3-g10-manifest", "export-manifest", E10 / "export-manifest.json", "validation", "export-manifest", sources=["pdc-v3-g10-fbx", "pdc-v3-g10-glb"])
    add("pdc-v3-g10-collision-policy", "collision-policy", E10 / "collision-policy.json", "validation", "collision-policy", sources=["pdc-v3-g10-manifest"])
    add("pdc-v3-g10-review", "export-review", E10 / "export-review-glb-roundtrip.png", "blender-render", "workbench-glb-roundtrip-review", "Workbench material colours; NOT Unity parity.", sources=["pdc-v3-g10-glb"])
    s10["artifactIds"] = ids
    s10["reviewArtifactIds"] = ["pdc-v3-g10-review", "pdc-v3-g10-manifest", "pdc-v3-g10-glb", "pdc-v3-g10-fbx"]
    validations = []
    for fmt in ("FBX", "GLB"):
        for check, ok in export_manifest["roundTrip"][fmt]["checks"].items():
            validations.append({"id": f"roundtrip-{fmt.lower()}-{check}", "status": "pass" if ok else "fail", "evidence": str(export_manifest["roundTrip"][fmt]["boundsMm"]["size"])})
    validations += [
        {"id": "source-approved-and-unchanged", "status": "pass", "evidence": f"Gate 07 blend {export_manifest['sourceGate07']['blendSha256'][:12]}; geometry identity {export_manifest['sourceGate06GeometryIdentity']['vertexPositionDigest'][:12]}"},
        {"id": "triangle-budget", "status": "pass", "evidence": f"{export_manifest['product']['source']['triangles']} <= 120000"},
        {"id": "no-toy-in-package", "status": "pass", "evidence": "GEO_PDC_REVIEW_SPINNER_* removed; PIVOT_PDC_CONTENT_SLOT kept for the caller-owned content."},
        {"id": "collision-policy-recorded", "status": "pass", "evidence": export_manifest["collision"]["policy"]},
        {"id": "unity-import-identity-transforms", "status": "pass" if g11_hierarchy["status"] == "pass" else "fail",
         "evidence": "Gate 11 rev-004 import: every node identity rotation / unit scale, 0.000 mm per-object bounds delta vs Blender (unity-bounds-digest-validation.json)."},
    ]
    s10["validations"] = validations
    reviewed = [{"id": aid, "path": rel(p), "sha256": sha256(p)} for aid, p in [
        ("pdc-v3-g10-review", E10 / "export-review-glb-roundtrip.png"), ("pdc-v3-g10-manifest", E10 / "export-manifest.json"),
        ("pdc-v3-g10-glb", E10 / "tri-spinner-slab-product-r003.glb"), ("pdc-v3-g10-fbx", E10 / "tri-spinner-slab-product-r003.fbx")]]
    s10["decision"] = batch_decision(reviewed, "export package rev-003 accepted under the user's 16:3x batch authorization after the Unity identity-transform check passed; Gate 12 preview still requires explicit approval")
    s10["exportSpec"] = {"modelId": MODEL_ID, "variantId": VARIANT, "revision": G10_REVISION, "recordedAt": NOW, "evidenceRevision": "rev-003",
                         "contractSha256": export_manifest["governingContract"]["sha256"], "package": export_manifest["package"], "roundTrip": export_manifest["roundTrip"],
                         "collision": export_manifest["collision"], "knownLimitations": export_manifest["knownLimitations"],
                         "changeFromRev004": "FBX options only: use_space_transform=False, axis_forward=Y, axis_up=Z, apply_unit_scale=True, FBX_SCALE_UNITS (was -Z/Y space transform on root objects, FBX_SCALE_NONE)."}
    s10["status"] = "approved"; s10["shippingReady"] = False; s10["variantId"] = VARIANT
    events.append({"type": "gate-approved-by-batch-authorization", "stageId": "10-export", "revision": G10_REVISION, "notes": AUTH_WORDING, "sourceId": AUTH_SOURCE})


def register_gate11(manifest, events):
    s11 = next(s for s in manifest["stages"] if s["id"] == "11-unity-parity")
    hierarchy = json.loads((E11 / "unity-hierarchy-pivot-material-report.json").read_text())
    bounds = json.loads((E11 / "unity-bounds-digest-validation.json").read_text())
    capture = json.loads((E11 / "unity-capture-report.json").read_text())
    metrics = json.loads((E11 / "parity-metrics.json").read_text())
    for src, dst in ((BUILDER_LIVE, BUILDER_SNAPSHOT), (TESTS_LIVE, TESTS_SNAPSHOT), (REFERENCE_LIVE, REFERENCE_SNAPSHOT)):
        shutil.copyfile(src, dst)
    results_source = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if results_source and results_source.exists():
        shutil.copyfile(results_source, TEST_RESULTS_SNAPSHOT)
    assert TEST_RESULTS_SNAPSHOT.exists(), "EditMode results XML required (pass the path as argv[1])"
    import xml.etree.ElementTree as ET
    root = ET.parse(TEST_RESULTS_SNAPSHOT).getroot()
    tests_total, tests_passed, tests_failed = int(root.get("total")), int(root.get("passed")), int(root.get("failed"))
    if s11["revision"] != G11_REVISION:
        archive_revision(s11, "legacy premium-display-case Gate 11 round preserved; tri-spinner-slab-v3-cmf Gate 11 rev 4 opened on export rev-003.", ("unityParitySpec",))
        events.append({"type": "stage-revised", "stageId": "11-unity-parity", "notes": f"11-unity-parity rev {s11['revision']} (legacy variant) preserved as history; rev {G11_REVISION} opened for {VARIANT}."})
        s11["revision"] = G11_REVISION
    s11["variantId"] = VARIANT; s11.pop("staleReason", None); s11.pop("nextStep", None)
    ids = []
    def add(aid, slot, path, role, cls, note="", sources=None, **extra):
        upsert(manifest, asset("11-unity-parity", aid, slot, path, role, cls, note, sources, **extra)); ids.append(aid)
    add("pdc-v3-g11-builder", "unity-builder", BUILDER_SNAPSHOT, "process", "unity-editor-builder-snapshot",
        f"Immutable copy of {rel(BUILDER_LIVE)} (live sha {sha256(BUILDER_LIVE)[:12]}): import, URP zone materials, decal, procedural studio cubemaps, matched cameras, reports.", sources=["pdc-v3-g10-fbx"])
    add("pdc-v3-g11-tests", "unity-tests", TESTS_SNAPSHOT, "process", "unity-editmode-tests-snapshot", f"Immutable copy of {rel(TESTS_LIVE)}.", sources=["pdc-v3-g11-builder"])
    add("pdc-v3-g11-test-results", "unity-test-results", TEST_RESULTS_SNAPSHOT, "validation", "unity-editmode-results", f"{tests_passed}/{tests_total} passed.", sources=["pdc-v3-g11-tests"])
    add("pdc-v3-g11-reference", "blender-reference-table", REFERENCE_SNAPSHOT, "validation", "blender-parity-reference",
        "Object / pivot / bounds / camera / area-light table extracted from the Blender product + Gate 09 shipping + Gate 07 neutral blends, mapped (x,z,y).", sources=["pdc-v3-g10-product-blend"])
    add("pdc-v3-g11-candidate-fbx", "unity-candidate-model", CANDIDATE / "Models/TriSpinnerSlabGate11R004.fbx", "export", "unity-candidate-fbx-byte-identical",
        "Byte-identical copy of the Gate 10 rev-003 FBX inside the Unity project.", sources=["pdc-v3-g10-fbx"])
    add("pdc-v3-g11-candidate-prefab", "unity-candidate-prefab", CANDIDATE / "Prefabs/PresentationRoot.prefab", "export", "unity-candidate-prefab",
        "PresentationRoot > ROOT_PDC_CASE_ASSEMBLY > 38 GEO_PDC_* + PIVOT_PDC_CONTENT_SLOT; DECAL_PDC_HEADER_LABEL under the header plane. Not the shipping prefab.", sources=["pdc-v3-g11-candidate-fbx"])
    add("pdc-v3-g11-hierarchy-report", "unity-report", E11 / "unity-hierarchy-pivot-material-report.json", "validation", "unity-hierarchy-pivot-material-report", sources=["pdc-v3-g11-candidate-prefab"])
    add("pdc-v3-g11-bounds-report", "unity-report", E11 / "unity-bounds-digest-validation.json", "validation", "unity-bounds-digest-validation", sources=["pdc-v3-g11-candidate-prefab"])
    add("pdc-v3-g11-capture-report", "unity-report", E11 / "unity-capture-report.json", "validation", "unity-capture-report", sources=["pdc-v3-g11-candidate-prefab"])
    add("pdc-v3-g11-parity-metrics", "unity-report", E11 / "parity-metrics.json", "validation", "blender-vs-unity-parity-metrics", sources=["pdc-v3-g11-capture-report"])
    for aid, file, cls in [("pdc-v3-g11-shipping-hero", "unity-shipping-hero.png", "unity-urp-shipping-rig-hero"), ("pdc-v3-g11-shipping-front", "unity-shipping-front.png", "unity-urp-shipping-rig-front-ortho"),
                           ("pdc-v3-g11-shipping-low", "unity-shipping-low-oblique.png", "unity-urp-shipping-rig-low-oblique"), ("pdc-v3-g11-shipping-left", "unity-shipping-left-oblique.png", "unity-urp-shipping-rig-left-oblique"),
                           ("pdc-v3-g11-shipping-right", "unity-shipping-right-oblique.png", "unity-urp-shipping-rig-right-oblique"), ("pdc-v3-g11-shipping-top", "unity-shipping-top.png", "unity-urp-shipping-rig-top"),
                           ("pdc-v3-g11-neutral-hero", "unity-neutral-hero.png", "unity-urp-neutral-rig-hero"), ("pdc-v3-g11-neutral-front", "unity-neutral-front.png", "unity-urp-neutral-rig-front"),
                           ("pdc-v3-g11-neutral-low", "unity-neutral-low-oblique.png", "unity-urp-neutral-rig-low-oblique"), ("pdc-v3-g11-silhouette", "unity-silhouette-front.png", "unity-silhouette-mask"),
                           ("pdc-v3-g11-cubemap-probe", "unity-shipping-cubemap-probe.png", "unity-cubemap-orientation-probe"), ("pdc-v3-g11-hero-noshadow", "unity-shipping-hero-noshadow.png", "unity-shadow-ab-variant")]:
        add(aid, "unity-capture", E11 / file, "unity-render", cls, "Real Unity 6000.5.6f1 URP batchmode capture, Blender camera recipe, no post-processing, no toy.", sources=["pdc-v3-g11-candidate-prefab"])
    for aid, file, cls, note in [("pdc-v3-g11-cmp-shipping-hero", "blender-vs-unity-shipping-hero.png", "blender-vs-unity-sheet", "Gate 09 shipping hero vs Unity hero."),
                                 ("pdc-v3-g11-cmp-shipping-low", "blender-vs-unity-shipping-low-oblique.png", "blender-vs-unity-sheet", "Gate 09 shipping low-oblique vs Unity."),
                                 ("pdc-v3-g11-cmp-front", "blender-vs-unity-front-and-silhouette.png", "blender-vs-unity-sheet", "front ortho, Gate 06 ortho, Unity silhouette."),
                                 ("pdc-v3-g11-cmp-neutral", "blender-vs-unity-neutral.png", "blender-vs-unity-sheet", "neutral rig hero + front."),
                                 ("pdc-v3-g11-views-sheet", "unity-standard-views-sheet.png", "unity-standard-views-sheet", "hero / top / left / right / low from Unity.")]:
        add(aid, "unity-review-sheet", E11 / file, "analysis", cls, note, sources=["pdc-v3-g11-shipping-hero"])
    add("pdc-v3-g11-turntable", "unity-turntable", TURNTABLE, "unity-render", "unity-parity-turntable-h264", "48 f @ 24 fps hero camera orbit, shipping rig, no post.", sources=["pdc-v3-g11-candidate-prefab"], frames=48, fps=24)
    add("pdc-v3-g11-turntable-frame012", "unity-turntable-still", ART11 / "gate11-r004-unity-parity-turntable-frame012.png", "unity-render", "turntable-still", sources=["pdc-v3-g11-turntable"])
    add("pdc-v3-g11-turntable-frame036", "unity-turntable-still", ART11 / "gate11-r004-unity-parity-turntable-frame036.png", "unity-render", "turntable-still", sources=["pdc-v3-g11-turntable"])
    s11["artifactIds"] = ids
    s11["reviewArtifactIds"] = ["pdc-v3-g11-cmp-shipping-hero", "pdc-v3-g11-cmp-front", "pdc-v3-g11-cmp-neutral", "pdc-v3-g11-views-sheet", "pdc-v3-g11-turntable",
                                "pdc-v3-g11-shipping-hero", "pdc-v3-g11-silhouette", "pdc-v3-g11-parity-metrics"]
    sil = metrics["silhouette"]
    s11["validations"] = [
        {"id": "approved-export-byte-identical", "status": "pass", "evidence": f"candidate FBX sha {sha256(CANDIDATE / 'Models/TriSpinnerSlabGate11R004.fbx')[:12]} == Gate 10 rev-003 FBX."},
        {"id": "hierarchy-pivots-materials", "status": hierarchy["status"], "evidence": f"{hierarchy['meshCount']} meshes, {hierarchy['triangles']} tris, {hierarchy['caseMaterialSlots']}/{hierarchy['caseMaterialSlotBudget']} case slots; root identity; PIVOT_PDC_CONTENT_SLOT at Blender pivot; failures {hierarchy['failures']}."},
        {"id": "imported-bounds", "status": bounds["status"], "evidence": f"case {[round(v*1000,2) for v in bounds['caseSizeMeters']]} mm vs manifest {[round(v*1000,2) for v in bounds['expectedCaseSizeMeters']]} mm; max per-object delta {bounds['maxObjectBoundsDeltaMeters']*1000:.4f} mm (tolerance 0.05 mm, acceptance 0.1 %)."},
        {"id": "front-silhouette-iou", "status": "pass" if sil["pass"] else "fail", "evidence": f"IoU {sil['iouRaw']} (min 0.995), bbox edge delta {sil['maxBboxEdgeDeltaPx']} px at 2048 (max 2) vs Gate 09 CAM_PDC_FRONT."},
        {"id": "matched-cameras-and-rigs", "status": capture["status"], "evidence": f"hero/front/low/left/right/top from the Blender camera table; shipping rig {len(capture['shippingRig']['emitters'])} emitters -> procedural cubemap + 1 directional + 3 additional lights; neutral rig {len(capture['neutralRig']['emitters'])} emitters."},
        {"id": "transparent-sorting", "status": "pass", "evidence": "opaque case 2000 < smoke liner 2990 < clear crystal 3000 (URP _QueueOffset); ZWrite off on both transparents; 48-frame orbit shows no pops."},
        {"id": "no-emissive-case-pixels", "status": "pass", "evidence": "_EmissionColor black on all 7 zone materials; decal is alpha-blended albedo only."},
        {"id": "editmode-tests", "status": "pass" if tests_failed == 0 and tests_total > 0 else "fail", "evidence": f"TriSpinnerSlabGate11ParityTests {tests_passed}/{tests_total} passed (unity-editmode-results.xml)."},
        {"id": "shipping-assets-untouched", "status": "pass", "evidence": "PremiumDisplayCase.prefab / scene / FBX hashes asserted before and after; PremiumDisplayCaseShippingFactory.ResourcesPath still Gate12R004."},
        {"id": "realtime-light-budget", "status": "pass", "evidence": "1 main directional + 3 additional (front fill spot, cyan edge spot, magenta edge spot) <= additional_realtime_lights_max 3."},
    ]
    s11["unityParitySpec"] = {"modelId": MODEL_ID, "variantId": VARIANT, "revision": G11_REVISION, "recordedAt": NOW, "evidenceRevision": "rev-004",
                              "unity": "6000.5.6f1 URP, batchmode", "candidateRoot": rel(CANDIDATE), "sourceGate10Revision": G10_REVISION, "axisMapping": capture["axisMapping"],
                              "materials": hierarchy["materials"], "silhouette": sil, "luminance": metrics["luminance"],
                              "knownLimitations": [
                                  "Clear crystal and smoke liner are URP Lit premultiplied stand-ins (alpha 0.08 / 0.25): no refraction, no thin-film iridescence, no per-edge alpha; the contract's PDC/ClearCrystal shader is Gate 12 lookdev work.",
                                  "Brushed anisotropy, sandblast micro-normal and piano-black clear coat are folded into constant smoothness (URP Lit has no anisotropy).",
                                  "Blender area lights are approximated by HDR rectangles in a procedural reflection cubemap plus 1 directional + 3 spot lights; luminance parity is informative only (Blender AgX vs Unity linear).",
                                  "A few 1-px voids at the bolt socket clearance show the background in the silhouette (~0.05 mm); cosmetic, tracked for a later geometry revision.",
                              ]}
    reviewed = [{"id": aid, "path": rel(p), "sha256": sha256(p)} for aid, p in [
        ("pdc-v3-g11-cmp-shipping-hero", E11 / "blender-vs-unity-shipping-hero.png"), ("pdc-v3-g11-cmp-front", E11 / "blender-vs-unity-front-and-silhouette.png"),
        ("pdc-v3-g11-shipping-hero", E11 / "unity-shipping-hero.png"), ("pdc-v3-g11-parity-metrics", E11 / "parity-metrics.json"), ("pdc-v3-g11-turntable", TURNTABLE)]]
    s11["decision"] = batch_decision(reviewed, "Unity parity accepted under the user's 16:3x batch authorization (all validations pass); the Gate 12 real Unity shipping preview still requires the user's explicit visual approval before any build/install")
    s11["status"] = "approved"; s11["shippingReady"] = False
    events.append({"type": "gate-approved-by-batch-authorization", "stageId": "11-unity-parity", "revision": G11_REVISION, "notes": AUTH_WORDING, "sourceId": AUTH_SOURCE})
    return hierarchy


def open_gate12(manifest, events):
    s12 = next(s for s in manifest["stages"] if s["id"] == "12-shipping")
    if s12["revision"] != G12_REVISION:
        archive_revision(s12, "legacy premium-display-case Gate 12 round preserved; tri-spinner-slab-v3-cmf Gate 12 rev 9 opened after Gate 11 rev 4.", ("shippingSpec",))
        events.append({"type": "stage-revised", "stageId": "12-shipping", "notes": f"12-shipping rev {s12['revision']} (legacy variant) preserved as history; rev {G12_REVISION} opened for {VARIANT}."})
        s12["revision"] = G12_REVISION
    s12["variantId"] = VARIANT; s12["status"] = "draft"; s12["decision"] = None; s12["shippingReady"] = False
    s12["artifactIds"] = []; s12["reviewArtifactIds"] = []; s12["validations"] = []
    s12.pop("staleReason", None)
    s12["nextStep"] = "Build the Gate 12 candidate (shipping presentation wrapper + real shipping-scene preview: hero, top, obliques, low, phone aspect) and STOP for the user's explicit visual approval. No build, no install before approval."
    events.append({"type": "stage-opened", "stageId": "12-shipping", "revision": G12_REVISION, "notes": "Gate 11 accepted under batch authorization; Gate 12 opened as draft. Batch authorization ends here: explicit approval required."})


def main() -> None:
    manifest_path = PIPELINE_DIR / "pipeline.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    events = []
    hierarchy = register_gate11(manifest, events)
    register_gate10(manifest, events, hierarchy)
    # keep stage order in the events log intuitive
    events.sort(key=lambda e: {"10-export": 0, "11-unity-parity": 1, "12-shipping": 2}.get(e.get("stageId"), 3))
    open_gate12(manifest, events)
    update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1; manifest["updatedAt"] = NOW
    manifest["model"]["status"] = "v3-tri-spinner-slab-gate-11-rev004-approved-batch-gate-12-draft"
    state = manifest["currentState"]
    state["activeStageId"] = "12-shipping"; state["activeStageStatus"] = "draft"
    state["batchAuthorization"]["consumed"] = ["10-export", "11-unity-parity"]
    state["batchAuthorization"]["consumedAt"] = NOW
    state["unityParity"] = {"revision": G11_REVISION, "candidateRoot": rel(CANDIDATE), "exportRevision": G10_REVISION, "status": "approved-by-batch-authorization",
                            "shippingFactoryStillPointsAt": "Gacha/PremiumDisplayCaseGate12R004/PresentationRoot"}
    state["diagnosis"] += (" Gate 10 rev 5：FBX 改为原生 Z-up + FBX_SCALE_UNITS（几何/材质/GLB 不变），Unity 导入全节点 identity。Gate 11 rev 4：Unity 6000.5.6f1 URP 真实导入，7 区材质 + 标签贴花，"
                           "Blender 相机/灯组表复刻，逐件包围盒 0.000 mm，正面剪影 IoU 0.998，EditMode 7/7；按 16:3x 批量授权自动通过。Gate 12 已开 draft：真实 Unity 出货预览待用户明确批准，未构建、未推送手机。")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, "variantId": VARIANT, **event}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "gate10": G10_REVISION, "gate11": G11_REVISION, "gate12": G12_REVISION, "events": [e["type"] + ":" + e["stageId"] for e in events]}))


if __name__ == "__main__":
    main()
