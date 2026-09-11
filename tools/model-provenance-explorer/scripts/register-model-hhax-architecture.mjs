import { loadManifest, saveArchitecturePlan } from "../pipeline-core.mjs";
const modelId = "model-hhax";
const base = "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax/evidence/04-architecture/rev-001";
const manifest = loadManifest(modelId);
const next = saveArchitecturePlan(modelId, {
  expectedRevision: manifest.revision,
  partTreePath: `${base}/part-tree.svg`,
  explodedPlanPath: `${base}/exploded-plan.svg`,
  recipe: "Gate 04 source-linked two-shell, mechanical-track and three-art-surface architecture",
  validations: [
    { id: "two-shell-ownership", status: "pass", evidence: "下壳固定，上壳沿 +Y 位移；外观不再拆成圆牌式第三主壳。" },
    { id: "mechanical-drive-owned", status: "pass", evidence: "直线轨、圆形载体和中央调节区属于机械手感总成；磁性只属于可换后贴。" },
    { id: "three-art-surfaces-separated", status: "pass", evidence: "上壳正面、露出下壳正面、背面三套图案和日夜掩膜各自独立。" },
    { id: "hidden-boundary-preserved", status: "pass", evidence: "隐藏联动曲线、内部数量、孔深和公差未被固化为生产结构。" }
  ]
});
console.log(JSON.stringify({ revision: next.revision, status: next.stages[3].status, artifactIds: next.stages[3].artifactIds }, null, 2));
