import { approveStageFromDelegation, loadManifest } from "../pipeline-core.mjs";
const modelId = "model-hhax";
const manifest = loadManifest(modelId);
const next = approveStageFromDelegation(modelId, "04-architecture", {
  expectedRevision: manifest.revision,
  notes: "已在交互爆炸装配中检查正面、顶面和斜视，并核对零件树：下壳固定、上壳直推、背部圆载体旋转；三套图案与透明封晶分区独立，隐藏联动仍保持未知。"
});
console.log(JSON.stringify({ revision: next.revision, gate04: next.stages[3].status, gate05: next.stages[4].status }, null, 2));
