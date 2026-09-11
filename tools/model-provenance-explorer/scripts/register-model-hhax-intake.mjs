import {
  loadManifest,
  registerStageApprovalDelegation,
  saveExternalReferencePack
} from "../pipeline-core.mjs";

const modelId = "model-hhax";
const base = "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax/evidence/01-intake/rev-002";
const nxedcPage = "https://nxedc.com/products/groove-ultra";
const nxedcVideo = "https://nxedc.com/cdn/shop/videos/c/vp/5e07740d4ff24673810186d4e4114541/5e07740d4ff24673810186d4e4114541.HD-1080p-2.5Mbps-88589287.mp4?v=0";

let manifest = loadManifest(modelId);
manifest = saveExternalReferencePack(modelId, {
  expectedRevision: manifest.revision,
  sourceName: "NXEDC / same-product public archive",
  sourceVersion: "2026-09-11",
  assets: [
    { id: "hhax-intake-nxedc-video-r002", path: `${base}/nxedc-groove-ultra-source.mp4`, sourceUrl: nxedcVideo, contentClass: "same-model-public-teardown-video", description: "同款完整演示与公开拆解视频：直推、旋转、调节螺钉、弹簧/珠与可换旋转部分。" },
    { id: "hhax-intake-nxedc-teardown-sheet-r002", path: `${base}/nxedc-teardown-contact-sheet.jpg`, sourceUrl: nxedcPage, contentClass: "same-model-public-teardown-image", description: "同款公开拆解视频逐帧联系表；保留动作与内部结构时间顺序。" },
    { id: "hhax-intake-nxedc-open-front-r002", path: `${base}/nxedc-open-front.jpg`, sourceUrl: nxedcPage, contentClass: "same-model-public-teardown-image", description: "同款直推开启外观；用于校验胶囊主壳与行程比例。" },
    { id: "hhax-intake-nxedc-open-track-r002", path: `${base}/nxedc-open-track.jpg`, sourceUrl: nxedcPage, contentClass: "same-model-public-teardown-image", description: "同款开启轨道；用于校验直线轨与圆形旋转载体的可见拓扑。" },
    { id: "hhax-intake-nxedc-rear-patch-r002", path: `${base}/nxedc-rear-patch.jpg`, sourceUrl: nxedcPage, contentClass: "same-model-public-teardown-image", description: "同款后部可换圆贴与中心区域；磁性只作为可换贴片固定。" },
    { id: "hhax-intake-nxedc-open-overview-r002", path: `${base}/nxedc-open-overview.jpg`, sourceUrl: nxedcPage, contentClass: "same-model-public-teardown-image", description: "同款直推与旋转结构总览。" },
    { id: "hhax-intake-nxedc-source-notes-r002", path: `${base}/source-notes.md`, sourceUrl: nxedcPage, contentClass: "same-model-official-spec", description: "同款官网与经销商交叉核对记录，区分公开标称、拆解观察与未知。" },
    { id: "hhax-intake-nxedc-source-metadata-r002", path: `${base}/source-metadata.json`, sourceUrl: nxedcPage, contentClass: "same-model-official-product-spec", description: "同款公开标称 50.5 × 30.9 × 13.6 mm、88 g 与来源 URL 元数据。" }
  ]
});

manifest = registerStageApprovalDelegation(modelId, {
  expectedRevision: manifest.revision,
  exactUserWording: "目标是完整的把这款材质做出来，通过设计圣经的判断和自我审查，一步步的自我通过，通过CAD/白模/blender/unity的流程，不需要人工approve，自我进行下一步，最终出成品",
  fromStageId: "01-intake",
  toStageId: "12-shipping"
});

console.log(JSON.stringify({ revision: manifest.revision, stage: manifest.currentStageId, delegation: manifest.currentState.approvalDelegation.authorizationId }, null, 2));
