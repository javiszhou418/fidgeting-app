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

## 布局

三栏 Studio 外壳，信息架构不变：

- 顶栏：品牌、当前模型、`当前 Gate NN/12`／`已批准 X/12`（`#studio-header-meta.canonical-progress`，带 `data-current-gate` / `data-approved-count`）。
- 左栏：模型选择、七个固定工作区 tab（`参考原图`→`Unity 灯光与成品`）；12 个 Gate 作为行嵌在所属 tab 下（`.gate-roadmap-item[data-stage-id]`），只展开激活的 tab。`#stage-rail` 保留但为空、`hidden`。
- 中栏：`当前正在做什么` 一行、画布（`#stage-detail`）。画布默认放大当前 Gate 的一个主产物；GLB 直接内联 three.js 视图（拖动旋转、滚轮缩放，工具条悬停才出现）。
- 右栏：`决策`（批准／退回）、`材质库`、`导出`／`成品预览`。
- 颜色：柠檬绿 `--accent` 实心只用于 `#approve-stage`；绿描边 `.button-accent` 给下载；绿字给激活 tab、正在看的 Gate、`已批准`、当前 Gate 数字；其余选中／hover 用灰阶填充或描边。允许清单在 `tests/studio-shell.test.mjs`，新增绿色用法要先加进去。

## 材质库

- 权威：`unity/FidgetingApp/ArtSource/MaterialLibrary/materials.json`；`materials.md` 由它生成，不手改。
- 校准球：`spheres/<id>.png`，`npm run materials:spheres`（需要 `blender` 在 PATH）。
- 校验：`npm run validate:materials`；`--refresh` 重算缩略图 SHA-256，`--write-md` 重新生成 markdown。
- 接口：`GET /api/material-library`。
- 概念图只用 ChatGPT Image Gen，concept-only，不晋升为几何或材质真值。

## 功能

- 12 关时间线、最早问题定位和下游 `stale` 状态。
- 参考图、Claim、Blender、FBX/GLB 与 Unity 输出的来源链。
- 图片并排/透明叠加、归一化框选问题、关联 Claim 和责任关卡。
- GLB 本地旋转、缩放、线框与固定相机检查。
- 乐观 revision 冲突、原子 manifest 写入、路径白名单与 SHA-256 刷新。
- 每关批准/拒绝、追加式版本历史，以及重建 Brief 导出。
- 左栏「模型」是 3×3 缩略图（每个模型最新的 hero 类渲染图，找不到图时显示首字），名字放在悬停提示里。
- 新建模型对话框首行可粘 Obsidian 链接（`obsidian://open?vault=…&file=…`）：`GET /api/obsidian/preview` 读出标题、来源 URL、机构猜测和笔记里嵌入的本地图/视频；创建时 `POST /api/models/<id>/intake-from-obsidian` 把笔记原文和全部附件归档到 Gate 01，标 `external` / `external-reference-*` 并记录 `sourceLocator`、`sourceUrl`、`vaultPath`。库位置读 `~/Library/Application Support/obsidian/obsidian.json`，也可用 `FIDGET_OBSIDIAN_VAULT` 指定。
- 左栏「步骤」是一条竖线 + 7 个节点：实心灰 = 已完成，绿点 = 当前工作步（只有一个），空心 = 未开始，琥珀环 = 过期，红点 = 被退回；展开的 12 关子行用文字「过期 / 退回」而不是圆点。
- 左栏底部固定的 Primary「＋ 新建模型」：填名称（ID 自动生成，可改）、选机构、拖入照片/视频/PDF，`POST /api/models` 建 `pipeline.json` + `history.ndjson`，文件逐个 `POST /api/models/<id>/intake-file`（原始字节，单个 ≤ 512 MB）落到 `evidence/01-intake/rev-NNN/` 并注册为 `original-reference` / `user-provided`，Gate 01 直接变为可审批。Gate 01 画布底部的「＋ 再加参考」同一接口；已批准的 Gate 01 再加参考会开新 rev 并把下游标 `stale`。命令行 `init_model_pipeline.mjs` 现在只是同一函数 `createModelPipeline` 的封装。

在第 12 关明确批准前，`shippingReady` 永远为 false；工具没有手机安装接口。

## 验证

```sh
npm --prefix tools/model-provenance-explorer test
npm --prefix tools/model-provenance-explorer run validate
npm --prefix tools/model-provenance-explorer run validate:materials
```
