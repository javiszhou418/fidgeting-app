#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import {
  digestValues,
  loadManifest,
  resolveRepoPath,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "premium-display-case";
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/08-lighting/rev-001";
const manifest = loadManifest(modelId);
const materialStage = manifest.stages[6];
const stage = manifest.stages[7];
const environmentStage = manifest.stages[8];

if (
  manifest.revision !== 34
  || materialStage.status !== "approved"
  || materialStage.decision?.notes !== "挺好的"
  || stage.status !== "blocked"
  || stage.artifactIds.length !== 0
) {
  throw new Error("Expected Gate 07 rev 1 approval at manifest revision 34 and an empty blocked Gate 08.");
}

const definitions = [
  ["lighting-registrar", "registration-source", "register_lighting_review.mjs"],
  ["lighting-builder", "lighting-source", "build_lighting_lookdev.py"],
  ["lighting-composer-validator", "validation-source", "compose_and_validate_lighting.py"],
  ["lighting-auditor", "validation-source", "audit_lighting_lookdev.py"],
  ["lighting-blend", "lighting-blend", "premium-display-case-lighting-r001.blend"],
  ["lighting-build-report", "validation-report", "lighting-build-report.json"],
  ["lighting-image-validation", "validation-report", "lighting-image-validation.json"],
  ["lighting-blender-audit", "validation-report", "blender-lighting-audit.json"],
  ["lighting-qa-verdict", "validation-report", "qa-verdict.json"],
  ["lighting-raw-hero", "hero", "raw/hero.png"],
  ["lighting-raw-left-oblique", "left-oblique", "raw/left-oblique.png"],
  ["lighting-raw-right-oblique", "right-oblique", "raw/right-oblique.png"],
  ["lighting-raw-low", "low-angle", "raw/low.png"],
  ["lighting-raw-beauty", "pass-beauty", "raw/pass-beauty.png"],
  ["lighting-raw-clay", "pass-clay", "raw/pass-clay.png"],
  ["lighting-raw-normal", "pass-normal", "raw/pass-normal.png"],
  ["lighting-raw-depth", "pass-depth", "raw/pass-depth.png"],
  ["lighting-raw-roughness", "pass-roughness", "raw/pass-roughness.png"],
  ["lighting-raw-label-closeup", "lighting-detail", "raw/label-closeup.png"],
  ["lighting-raw-tube-corner", "lighting-detail", "raw/tube-corner.png"],
  ["lighting-raw-black-panel", "lighting-detail", "raw/black-panel.png"],
  ["lighting-review", "lighting-review-board", "lighting-review.png"],
  ["lighting-details", "lighting-review-board", "lighting-details-contact-sheet.png"],
  ["lighting-passes", "lighting-review-board", "lighting-passes-contact-sheet.png"],
  ["lighting-parameters", "lighting-review-board", "lighting-parameters-board.png"],
];
const sourceAssetIds = [
  "premium-display-case-material-blend-r001",
  "premium-display-case-material-build-report-r001",
  "premium-display-case-material-blender-audit-r001",
  "premium-display-case-material-image-validation-r001",
  "premium-display-case-material-board-r001",
  "premium-display-case-material-closeup-r001",
  "premium-display-case-material-grain-stability-r001",
  "premium-display-case-geometry-blend-r002",
];
const approvalClaimId = "display-case-gate07-r001-user-approval-r001";
const lightingClaimId = "display-case-gate08-neutral-lighting-r001";
const sourceClaimIds = [
  "display-case-analysis-closed-loop-r002",
  "display-case-analysis-manifold-r002",
  "display-case-analysis-background-r002",
  "display-case-analysis-label-r002",
  "display-case-analysis-portrait-r002",
  "display-case-analysis-flow-r002",
  "display-case-analysis-environment-r002",
  approvalClaimId,
];
const build = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/lighting-build-report.json`), "utf8"));
const image = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/lighting-image-validation.json`), "utf8"));
const audit = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/blender-lighting-audit.json`), "utf8"));
const qa = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/qa-verdict.json`), "utf8"));
if (
  ![build, image, audit, qa].every((report) => report.status === "pass")
  || build.sourceGate07.approvalQuote !== "挺好的"
  || !build.geometry.unchanged
  || !build.materials.unchanged
  || qa.result !== "READY_FOR_LIGHTING_REVIEW_NOT_SHIPPING"
) {
  throw new Error("Gate 08 rev 1 evidence did not pass.");
}

const viewMetadata = {
  "lighting-raw-hero": ["hero", "M08_HeroCamera", "perspective"],
  "lighting-raw-left-oblique": ["left-oblique", "M08_Left_ObliqueCamera", "perspective"],
  "lighting-raw-right-oblique": ["right-oblique", "M08_Right_ObliqueCamera", "perspective"],
  "lighting-raw-low": ["low", "M08_LowCamera", "perspective"],
  "lighting-raw-beauty": ["hero", "M08_HeroCamera", "beauty-pass"],
  "lighting-raw-clay": ["hero", "M08_HeroCamera", "clay-pass"],
  "lighting-raw-normal": ["hero", "M08_HeroCamera", "normal-pass"],
  "lighting-raw-depth": ["hero", "M08_HeroCamera", "depth-pass"],
  "lighting-raw-roughness": ["hero", "M08_HeroCamera", "roughness-pass"],
  "lighting-raw-label-closeup": ["label-closeup", "M08_Label_CloseupCamera", "detail"],
  "lighting-raw-tube-corner": ["tube-corner", "M08_Tube_CornerCamera", "detail"],
  "lighting-raw-black-panel": ["black-panel", "M08_Black_PanelCamera", "detail"],
};
const records = definitions.map(([suffix, slot, file]) => {
  const relativePath = `${root}/${file}`;
  const absolutePath = resolveRepoPath(relativePath);
  if (!fs.existsSync(absolutePath)) throw new Error(`Missing ${relativePath}`);
  const isSource = /\.(py|mjs)$/.test(file);
  const isBlend = file.endsWith(".blend");
  const isImage = file.endsWith(".png");
  const record = {
    id: `${modelId}-${suffix}-r001`,
    stageId: "08-lighting",
    slot,
    path: relativePath,
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role: isBlend ? "source-model" : isImage ? "blender-render" : isSource ? "process" : "validation",
    producer: {
      name: isImage
        ? (file.startsWith("raw/") ? "Blender" : "Pillow review compositor")
        : isBlend
          ? "Blender"
          : isSource
            ? "Python/Node.js"
            : "deterministic evidence pipeline",
      version: isBlend || file.startsWith("raw/") ? build.blender : "Python 3 / Node.js",
      recipe: `${root}/${isSource ? file : file.startsWith("raw/") || isBlend ? "build_lighting_lookdev.py" : "compose_and_validate_lighting.py"}`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: suffix,
      assertedBy: "assistant",
      note: "Gate 08 rev 1 uses the user-approved Gate 07 rev 1 materials and unchanged Gate 06 rev 2 geometry. It is whole-case-only Blender lighting evidence; Gate 09, shipping Unity, build, install, and phone work remain untouched.",
      approvedGate07Decision: "挺好的",
      sourceGeometryDigest: build.geometry.digestAfter,
      sourceMaterialDigest: build.materials.digestAfter,
    },
    sourceAssetIds,
    sourceClaimIds,
    wholeCaseOnly: true,
    explodeEligible: false,
  };
  if (viewMetadata[suffix]) {
    const [id, camera, kind] = viewMetadata[suffix];
    record.view = {
      id,
      kind,
      camera,
      assemblyState: "assembled",
      renderEngine: file.includes("pass-") && !file.includes("beauty") ? "BLENDER_EEVEE" : "CYCLES",
      axisContract: "X-width/Y-height/Z-front",
    };
  }
  return record;
});
manifest.assets.push(...records);

manifest.claims.push({
  id: approvalClaimId,
  stageId: "07-material",
  topic: "gate07-rev1-material-approval",
  statement: "用户查看 Gate 07 rev 1 material-board.png 后以原文“挺好的”批准当前材质响应和分区。",
  confidence: "high",
  state: "active",
  assertedBy: "user",
  sourceAssetIds: [
    "premium-display-case-material-board-r001",
    "premium-display-case-material-closeup-r001",
  ],
  sourceRegions: [],
  sourceTask: "current Cursor thread",
  decisionState: "locked",
  deliveryState: "gate07-approved-gate08-lighting-review-pending",
});
manifest.claims.push({
  id: lightingClaimId,
  stageId: "08-lighting",
  topic: "controlled-neutral-product-lighting",
  statement: "Gate 08 rev 1 使用 key/fill/rim=1.00/0.30/0.40 的中性产品灯光、60 mm / 29.862834° vFOV Portrait 相机、AgX Medium High Contrast 与 +0.55 EV。该配方只属于 Blender lighting review，不是当前 Unity runtime 参数。",
  confidence: "high",
  state: "active",
  assertedBy: "assistant",
  sourceAssetIds: [
    `${modelId}-lighting-build-report-r001`,
    `${modelId}-lighting-review-r001`,
    `${modelId}-lighting-parameters-r001`,
  ],
  sourceRegions: [],
  sourceTask: "current Cursor thread",
  decisionState: "pending-user-approval",
  deliveryState: "gate08-ready-for-review-not-shipping",
});

materialStage.materialSpec = {
  ...materialStage.materialSpec,
  gate07Approved: true,
  gate08Entered: true,
  finalLightingApproved: false,
  approval: {
    approvedRevision: 1,
    userApprovalQuote: "挺好的",
    approvalEffect: "locks-current-material-response-and-boundaries",
    gate08Status: "eligible",
  },
};

stage.revision += 1;
stage.status = "ready_for_review";
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  `${modelId}-lighting-review-r001`,
  `${modelId}-lighting-details-r001`,
  `${modelId}-lighting-passes-r001`,
  `${modelId}-lighting-parameters-r001`,
];
stage.lightingSpec = {
  revision: 1,
  sourceMaterialRevision: 1,
  sourceMaterialApprovalQuote: "挺好的",
  sourceGeometryRevision: 2,
  sourceGeometryDigest: build.geometry.digestAfter,
  sourceMaterialDigest: build.materials.digestAfter,
  geometryUnchanged: build.geometry.unchanged,
  materialUnchanged: build.materials.unchanged,
  wholeCaseOnly: true,
  explode: false,
  controlledRig: build.lighting,
  cameras: build.cameras,
  render: build.render,
  outputs: build.outputs,
  imageMetrics: image,
  grainStability: build.grainStability,
  transparentOrderingPreflight: build.materials.transparentOrderingPreflight,
  qaResult: qa.result,
  shippingUnityChanged: false,
  buildInstallPhonePush: false,
  gate08Approved: false,
  gate09Entered: false,
};
stage.validations = [
  {
    id: "gate07-material-approval-exact",
    status: "pass",
    evidence: "Gate 07 rev 1 is approved through the pipeline API with exact user wording “挺好的”.",
  },
  {
    id: "geometry-digest-preserved",
    status: "pass",
    evidence: `Gate 06 rev 2 geometry digest remains ${build.geometry.digestAfter}.`,
  },
  {
    id: "material-digest-preserved",
    status: "pass",
    evidence: `Approved Gate 07 material digest remains ${build.materials.digestAfter} before and after all renders.`,
  },
  {
    id: "controlled-neutral-rig",
    status: "pass",
    evidence: "Key/fill/rim ratios are 1.00/0.30/0.40; 5000/6200/5600 K low-chroma sources contain no rarity or fixed green light.",
  },
  {
    id: "camera-and-exposure-recorded",
    status: "pass",
    evidence: `Hero uses 60 mm, ${build.cameras.hero.verticalFovDegrees}° vFOV, AgX Medium High Contrast, and ${build.render.exposureEv} EV. Shutter/ISO are unset and no Unity runtime mapping is claimed.`,
  },
  {
    id: "required-whole-case-views",
    status: "pass",
    evidence: "Hero, left/right oblique, and low-angle Blender renders are assembled whole-case views with comfortable uncropped margins.",
  },
  {
    id: "required-render-passes",
    status: "pass",
    evidence: "Beauty, Clay, Normal, Depth, and Roughness passes are present, distinct, and validated.",
  },
  {
    id: "highlight-clipping-controlled",
    status: "pass",
    evidence: `Maximum >=250 channel clipping fraction is ${Math.max(...Object.values(image.rawMetrics).map((item) => item.highlightClipFraction))}, below 0.5%.`,
  },
  {
    id: "label-and-dark-panel-readable",
    status: "pass",
    evidence: `Label/background mean contrast is ${image.labelMetrics.labelBackgroundMeanContrast}; black-panel median is ${image.blackPanelMetrics.medianLuma} with ${image.blackPanelMetrics.crushedBelow4Fraction} crushed fraction.`,
  },
  {
    id: "tube-highlight-continuous",
    status: "pass",
    evidence: `Largest bright component spans ${image.tubeHighlightContinuity.largestBrightComponent.widthFraction} × ${image.tubeHighlightContinuity.largestBrightComponent.heightFraction} of the tube detail frame.`,
  },
  {
    id: "green-bias-controlled",
    status: "pass",
    evidence: `Hero neutral-sample mean green excess is ${image.greenBiasMetrics.hero.meanGreenExcess}; >8 excess fraction is ${image.greenBiasMetrics.hero.greenExcessAbove8Fraction}.`,
  },
  {
    id: "grain-and-transparency-preflight",
    status: "pass",
    evidence: "Object-local grain is stable at 0/90/180/270/360; transparent label/foil/print/cover ordering preflight passes.",
  },
  {
    id: "whole-case-only-no-explode",
    status: "pass",
    evidence: "All review artifacts show the assembled case. No exploded, assembly, reassembly, or layer-separation evidence is user-facing.",
  },
  {
    id: "gate08-only",
    status: "pass",
    evidence: "Gate 09 remains blocked. Shipping Unity, build, install, and phone state are unchanged.",
  },
];
stage.decision = null;
delete stage.staleReason;
if (environmentStage.status === "blocked") {
  environmentStage.staleReason = "Gate 08 lighting rev 1 is ready_for_review and awaits explicit user approval. Gate 09 must not start.";
}

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const current = manifest.stages[index];
  const hashes = current.artifactIds.map((assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claimRecords = manifest.claims
    .filter((claim) => claim.stageId === current.id)
    .map(stableJson);
  current.inputDigest = index === 0
    ? digestValues([...hashes, ...claimRecords])
    : manifest.stages[index - 1].outputDigest;
  current.outputDigest = digestValues([...hashes, ...claimRecords]);
}
manifest.currentState.visualApproval = "gate08-lighting-pending";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis = "Gate 07 rev 1 已通过 pipeline API 以用户原文“挺好的”批准。Gate 08 rev 1 使用未变 Gate 06 geometry 与 Gate 07 materials，生成 whole-case-only Hero／左右斜视／低角、Beauty／Clay／Normal／Depth／Roughness、标签／闭环管角／黑内板特写及大字评审板。当前 Gate 08 ready_for_review，Gate 09 blocked；shipping Unity 未修改，未构建、未安装、未推送手机。";

const event = {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "08-lighting",
  lightingRevision: 1,
  sourceMaterialRevision: 1,
  sourceMaterialApprovalQuote: "挺好的",
  geometryDigest: build.geometry.digestAfter,
  materialDigest: build.materials.digestAfter,
  keyFillRimRatios: build.lighting.ratios,
  heroCamera: build.cameras.hero,
  exposure: build.render.exposureEv,
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
  lightingReviewPath: `${root}/lighting-review.png`,
  gate09Status: "blocked",
  autoApproved: false,
  shippingAssetUnchanged: true,
  buildInstallPhonePush: false,
};
const saved = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: saved.revision,
  approvedCount: saved.stages.filter((item) => item.status === "approved").length,
  gate07: saved.stages[6].status,
  gate08: saved.stages[7].status,
  gate09: saved.stages[8].status,
  artifacts: saved.stages[7].artifactIds.length,
  reviewArtifacts: saved.stages[7].reviewArtifactIds,
  lightingReviewPath: `${root}/lighting-review.png`,
  geometryDigest: build.geometry.digestAfter,
  materialDigest: build.materials.digestAfter,
  approvalClaimId,
  lightingClaimId,
}, null, 2));
