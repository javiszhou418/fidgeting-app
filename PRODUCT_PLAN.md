# Fidget Spinner 产品计划（兼容入口）

> 本文件保留给旧任务、脚本和专项规范作为稳定入口，不再维护第二套产品设计正文。

## 权威文档

- 产品定义、设计偏好、当前视觉／交互／模型／成长／收藏规格、批准证据与否决历史：
  [FidgetingAppProductDesignBible.md](unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md)
- 交互、机械、Core Motion 与语义 Haptic 目标架构：
  [FidgetingInteractionHapticsSystem.md](unity/FidgetingApp/Docs/FidgetingInteractionHapticsSystem.md)
- 产品手感语言与调参范围：
  [FidgetingProductFeelGuideline.md](unity/FidgetingApp/Docs/FidgetingProductFeelGuideline.md)；
  [InteractionTuningParameters.md](unity/FidgetingApp/Docs/InteractionTuningParameters.md)
- 原生 UI 与媒体规则：
  [LiquidGlassDesignGuideline.md](unity/FidgetingApp/Docs/LiquidGlassDesignGuideline.md)
- Badge 与 Fan Card 专项合同：
  [BadgeSystemSpecification.md](unity/FidgetingApp/Docs/BadgeSystemSpecification.md)；
  [FanCardModelingGuardrails.md](unity/FidgetingApp/Docs/FanCardModelingGuardrails.md)
- 实际 runtime、场景、测试、构建、安装和真机状态：
  [IMPLEMENTATION_STATUS.md](unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md)

## 新方案评审入口

所有新 feature、重设计和视觉候选在排期前，先通过设计圣经的
[“设计偏好、产品定义与拒绝准则”](unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md#2-设计偏好产品定义与拒绝准则)：

1. 说明它如何加强“真实可感的数字玩具”核心，而不是只增加功能或装饰。
2. 对照可接受特征和明确拒绝的反模式；冲突项先停止，不直接进入实现。
3. 标明结论来自锁定偏好还是推断；推断不得冒充用户批准。
4. 命中视觉／手感／经济灰区时，把 shipping 预览、产品决定或 iPhone 验收列为独立门禁。
5. 涉及触摸、力度、陀螺仪或加速度时，必须写明“真实输入 → 可解释物理参数／状态 → 语义事件 → Haptic／音效／视觉”的完整映射和调校边界；原始传感器值不得直触发反馈。

## 产品身份速查

- 唯一 Unity 产品：`unity/FidgetingApp`
- iOS 产品名：`Fidget Spinner`
- Bundle ID：`com.jiaweizhou.fidgetspinner.codex`
- 当前目录：`blue-classic`、`metal-three-blade`、`gold-four-wing`、`graphite-two-lobe`、`magnetic-slide-tile`、`magnetic-fan-card`

## 维护规则

1. 新的产品决定、视觉批准、否决和替代只写入设计圣经，并使用稳定 `FDB-*` ID。
2. 本文件只更新链接或产品身份，不复制参数、状态矩阵或历史方案。
3. 设计完成不等于集成；实现证据只写入 `IMPLEMENTATION_STATUS.md`。
4. shipping 预览批准、代码集成、手机安装和用户真机接受始终是四个独立门禁。
