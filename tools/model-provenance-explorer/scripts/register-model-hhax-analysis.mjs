import { loadManifest, saveAnalysisResearchRevision } from "../pipeline-core.mjs";

const modelId = "model-hhax";
const base = "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax/evidence/02-analysis/rev-002";
const user = {
  note: "model-hhax-intake-r1-a8301672",
  dayFront: "model-hhax-intake-r1-f2576ce0",
  dayBackA: "model-hhax-intake-r1-fa5bb900",
  dayBackB: "model-hhax-intake-r1-8838e089",
  darkFront: "model-hhax-intake-r1-da708586",
  darkFrontB: "model-hhax-intake-r1-4b59c226",
  darkBack: "model-hhax-intake-r1-2ed6d6a0",
  darkBackB: "model-hhax-intake-r1-f0aebe7c"
};
const publicSource = {
  video: "hhax-intake-nxedc-video-r002",
  sheet: "hhax-intake-nxedc-teardown-sheet-r002",
  open: "hhax-intake-nxedc-open-front-r002",
  track: "hhax-intake-nxedc-open-track-r002",
  rear: "hhax-intake-nxedc-rear-patch-r002",
  overview: "hhax-intake-nxedc-open-overview-r002",
  notes: "hhax-intake-nxedc-source-notes-r002",
  metadata: "hhax-intake-nxedc-source-metadata-r002",
  mechanism: "hhax-intake-mechanical-drive-classification-r002"
};
const allSources = [...Object.values(user), ...Object.values(publicSource)];
const manifest = loadManifest(modelId);
const next = saveAnalysisResearchRevision(modelId, {
  expectedRevision: manifest.revision,
  recipe: "Exact-product public mechanism research cross-checked against the user's custom day/night appearance references",
  assets: [
    { id: "hhax-analysis-discovery-log-r002", slot: "discovery-log", path: `${base}/discovery-log.json`, sourceAssetIds: allSources, contentClass: "source-linked-analysis-log", description: "同款身份、公开标称、机械动作、定制材质与未知边界。" },
    { id: "hhax-analysis-board-r002", slot: "analysis-board", path: `${base}/analysis-board.svg`, sourceAssetIds: allSources, contentClass: "annotated-structure-and-material-board", description: "结构与定制日夜材质判断板。" },
    { id: "hhax-analysis-parameter-snapshot-r002", slot: "parameter-snapshot", path: `${base}/parameter-snapshot.json`, sourceAssetIds: allSources, contentClass: "analysis-parameter-snapshot", description: "第 2 关动作、公开外廓和不确定性边界快照。" },
    { id: "hhax-analysis-interactive-cad-r002", slot: "interactive-cad", path: `${base}/interactive-cad.glb`, sourceAssetIds: allSources, contentClass: "interactive-structural-cad", description: "可旋转检查的结构 CAD：两个胶囊主壳、直线轨、圆轨、调节区与半透明未知联动包络。" }
  ],
  claims: [
    { id: "hhax-claim-product-envelope-r002", category: "dimension", statement: "同款公开标称闭合外形为 50.5 × 30.9 × 13.6 mm、88 g；它是数字复原外廓依据，不是本定制封晶件的独立实测或制造公差。", confidence: "high", sourceAssetIds: [publicSource.metadata, publicSource.notes] },
    { id: "hhax-claim-mechanical-linkage-r002", category: "mechanism", statement: "工作台兼容分类为线性磁吸推牌（linear-magnetic-slider），但产品真实动作驱动是长轴直推与旋转联动机械轨道；磁性只固定可换贴片，不驱动动作。", confidence: "high", sourceAssetIds: [publicSource.video, publicSource.sheet, publicSource.mechanism, publicSource.notes] },
    { id: "hhax-claim-shell-topology-r002", category: "structure", statement: "外观由两个胶囊主壳叠合；推开后露出的是下壳胶囊尾部及其独立图案，不是单独圆牌。", confidence: "high", sourceAssetIds: [user.dayFront, publicSource.open, publicSource.overview] },
    { id: "hhax-claim-service-topology-r002", category: "structure", statement: "后部圆贴可拆，中央螺钉调节直推/旋转阻尼；公开拆解还显示长直轨、圆形旋转载体、可换弹簧/珠与隐藏挂绳孔。", confidence: "high", sourceAssetIds: [publicSource.video, publicSource.sheet, publicSource.track, publicSource.rear] },
    { id: "hhax-claim-custom-day-material-r002", category: "material", statement: "定制外观以用户原图为最高依据：近黑紫灰高抛金属、窄幅局部虹彩边、贝母棋格、珊瑚红骑士及透明封晶；公共普通版本的颜色和图案不得替换它。", confidence: "high", sourceAssetIds: [user.dayFront, user.dayBackA, user.dayBackB, user.note] },
    { id: "hhax-claim-three-art-surfaces-r002", category: "artwork", statement: "图案分为正面上壳、推开露出的下壳正面、背面三套独立表面；字样为 MORE THAN CLASSIC、KNIGHT IN CHESS、MOT STUDIO。", confidence: "high", sourceAssetIds: [user.dayFront, user.dayBackA, user.dayBackB] },
    { id: "hhax-claim-dark-emission-r002", category: "material", statement: "暗处仅棋格发青蓝光、骑士发橙光；金属壳、铭牌和文字保持不发光。", confidence: "high", sourceAssetIds: [user.darkFront, user.darkFrontB, user.darkBack, user.darkBackB] },
    { id: "hhax-claim-hidden-boundary-r002", category: "unknown", statement: "隐藏联动曲线、弹簧/珠精确数量、孔深、公差和本定制封晶件真实厚度仍未知；后续内部数值只能作为绑定同款公开拆解的可回退数字复原目标，不得称实测或生产尺寸。", confidence: "high", sourceAssetIds: [publicSource.video, publicSource.sheet, publicSource.notes, user.dayFront] }
  ],
  validations: [
    { id: "exact-product-source-linked", status: "pass", evidence: "每条当前判断都绑定用户原图或同款公开素材；公共版本只决定外廓/机构，用户原图决定定制外观。" },
    { id: "mechanical-drive-corrected", status: "pass", evidence: "已移除磁吸驱动误判；直推与旋转按机械联动轨道处理，磁铁仅用于可换贴片。" },
    { id: "custom-day-night-separated", status: "pass", evidence: "日光贝母/珊瑚红与暗处青蓝/橙发光被拆成独立、非全局发光的材质状态。" },
    { id: "unknowns-preserved", status: "pass", evidence: "隐藏曲线、数量、公差、孔深与定制封晶真实厚度未冒充实测；只允许可逆数字校准。" },
    { id: "interactive-cad-present", status: "pass", evidence: "真实 GLB CAD 可旋转查看可见模块与半透明未知包络；未启动 Blender。" }
  ],
  diagnosis: "同款公开资料和用户定制图片已统一到机械直推/旋转结构与日夜材质合同；进入交互 CAD 自审。",
  staleReason: "第 2 关已按同款公开机构证据和用户定制日夜外观重建；旧的磁吸驱动与圆牌推断作废。"
});
console.log(JSON.stringify({ revision: next.revision, status: next.stages[1].status, claims: next.claims.filter((claim) => claim.stageId === "02-analysis" && claim.state === "active").length }, null, 2));
