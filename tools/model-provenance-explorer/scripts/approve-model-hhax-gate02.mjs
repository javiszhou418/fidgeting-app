import { approveStageFromDelegation, loadManifest, updateModelMechanism } from "../pipeline-core.mjs";
const modelId = "model-hhax";
let manifest = loadManifest(modelId);
manifest = approveStageFromDelegation(modelId, "02-analysis", {
  expectedRevision: manifest.revision,
  notes: "已在真实交互 CAD 中旋转并切换正面、顶面和斜视检查；两个主壳、直轨、圆轨、中央调节区与未知边界符合当前来源，磁吸驱动旧判断已排除。"
});
manifest = updateModelMechanism(modelId, {
  expectedRevision: manifest.revision,
  mechanism: "linear-magnetic-slider",
  note: "兼容工作台分类；真实驱动为机械直推与旋转联动轨道，磁性仅用于可换贴片。"
});
console.log(JSON.stringify({ revision: manifest.revision, mechanism: manifest.model.mechanism, gate02: manifest.stages[1].status }, null, 2));
