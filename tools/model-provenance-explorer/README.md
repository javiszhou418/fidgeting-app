# Fidgeting Model Provenance Explorer

本地 12 关模型溯源工作台，把用户原始参考、结构判断、Blender revision、导出包和 Unity shipping 输出一对一对应。它使用仓库内的 manifest 与追加式历史，而不是把浏览器 localStorage 当成批准来源。

## 打开

在仓库根目录运行：

```sh
npm --prefix tools/model-provenance-explorer install
npm --prefix tools/model-provenance-explorer start
```

然后访问：

`http://127.0.0.1:8891/tools/model-provenance-explorer/`

页面需要本地 API，不能再直接双击 `index.html` 或使用普通静态服务器。

## 权威数据

- 每款模型：`unity/FidgetingApp/ArtSource/ModelPipeline/<model-id>/pipeline.json`
- 追加式历史：同目录 `history.ndjson`
- JSON Schema：`model-pipeline.schema.json`
- 固定数据接口：`pipeline-types.d.ts`（`PipelineManifest`、`AssetRecord`、`Claim`、`StageRun`、`Issue`、`DecisionEvent`）
- 12 关合同：`pipeline-contract.mjs`
- Codex Skill：`skills/fidgeting-model-pipeline/`

素材变化后可在页面点击“刷新哈希”，或运行：

```sh
node tools/model-provenance-explorer/validate-pipelines.mjs --refresh
```

旧 `pipeline-config.mjs` 与 `inventory.generated.js` 只保留为 V1 历史兼容，不再决定审批状态。

## 功能

- 12 关时间线、最早问题定位和下游 `stale` 状态。
- 参考图、Claim、Blender、FBX/GLB 与 Unity 输出的来源链。
- 图片并排/透明叠加、归一化框选问题、关联 Claim 和责任关卡。
- GLB 本地旋转、缩放、线框与固定相机检查。
- 乐观 revision 冲突、原子 manifest 写入、路径白名单与 SHA-256 刷新。
- 每关批准/拒绝、追加式版本历史，以及重建 Brief 导出。

在第 12 关明确批准前，`shippingReady` 永远为 false；工具没有手机安装接口。

## 验证

```sh
npm --prefix tools/model-provenance-explorer test
npm --prefix tools/model-provenance-explorer run validate
```
