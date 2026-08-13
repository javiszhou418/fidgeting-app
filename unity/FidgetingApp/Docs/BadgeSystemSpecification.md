# Badge 系统与经济规格

最后更新：2026-08-10

## 体系边界

- 单玩具永久 Badge：21 枚，同一目录由每个模型独立计算。
- 收藏者永久 Badge：13 枚，跨模型计算。
- 周挑战：4 个模板按 UTC 周循环；每四周全清获得周期总章。
- Legacy：最多一枚“创始收藏”，只由旧离线 Badge 迁移产生。
- 所有进度保存在本机；不接 Game Center，不展示全球获得率。
- AUTO、Library 预览、回放或无明确用户输入产生的运动不能推进技巧、Combo、挑战或活跃时长。

## 公共模型

`BadgeDefinition` 必须包含：`id`、`scope`、`category`、`mechanism`、`metric`、`threshold`、`grade`、`visibility`、`title`、`description`、`assetName`、`displayToken`、`displayUnit`、`experienceReward`、`shardReward`、`displayOrder`。`displayToken` 和 `displayUnit` 由原生 UI 使用 Oxanium 排版，不写进底图。

`BadgeProgressSnapshot` 必须包含：`id`、`currentValue`、`targetValue`、`state`、`progress`、`unlockedAtUtc`、`rewardClaimed`。

`BadgeChallengeSnapshot` 必须包含：`templateId`、`cycleIndex`、`startsAtUtc`、`endsAtUtc`、`currentValue`、`targetValue`、`completed`、`rewardClaimed`。

状态固定为 `Locked`、`InProgress`、`Hidden`、`Unlocked`。等级固定为 `Ignition`、`Overdrive`、`Apex`、`Singularity`。

## 全 App 统一规则

- 单玩具、收藏者、挑战和 Legacy 只允许使用 `BadgeDefinition` / `BadgeProgressSnapshot` 这一套领域模型；旧 `ProgressionAchievement`、`CollectorAchievement` 只能作为一次性迁移输入，不能继续生成页面、通知或奖励。
- 图鉴、最近目标、详情、解锁通知和分享卡必须复用 `ProductRarityBadge`，并从同一份 `ProductBadgeDetail` 读取 artwork、Token、短名、等级和状态。不得用通用星标、奖杯或 SF Symbol 代替 Badge 本体。
- 所有永久 Badge 共用一个 `BadgeRewardLedger`。领取键分别为 `toy:<model>:<badgeId>`、`collector:<badgeId>` 和 `special:<templateId>@<cycleIndex>`；同一键只能发放一次 XP 与碎片。
- 解锁通知只由 `rewardClaimed == true` 且尚未展示的 `unlockIdentity` 进入统一队列；单玩具和收藏者不得维护两套通知样式或两套 seen key。
- 解锁触感必须发送 `BadgeUnlocked` 语义事件，禁止 UI 或奖励账本直接调用原始 iOS Haptic API。

## 21 枚单玩具 Badge

| 分类 | 数量 | 阈值 / 条件 | 等级 |
|---|---:|---|---|
| 动力 | 4 | Rotor：1.0 / 2.0 / 3.5 / 4.5 km/h；Slider/Fan：峰值标准化力度 0.35 / 0.55 / 0.75 / 0.90 | I/O/A/S |
| 累计操作 | 4 | 100 / 1,000 / 10,000 / 100,000 次真实手势 | I/O/A/S |
| 技巧 | 5 | 首次 Clean / Power / Speed / Endurance / Perfect；后三项为隐藏 | I/O/A/A/S |
| Combo | 4 | 单次最高 5 / 10 / 20 / 50 | I/O/A/S |
| 实际专注 | 4 | 5 分钟 / 30 分钟 / 2 小时 / 10 小时真实触摸 | I/O/A/S |

Rotor、Slider、Fan 共享五种技巧判定结构，但展示名称按机制适配，例如 `Perfect Spin`、`Perfect Slide`、`Perfect Fan`。ProductCatalog 必须提供稳定的 `ProductMechanismKind`，UI 不根据字符串猜测机制。

## 13 枚收藏者 Badge

| 分类 | 数量 | 阈值 |
|---|---:|---|
| 节奏 | 3 | 完成 1 / 4 / 12 个有效节奏周 |
| 探索 | 3 | 有效使用 2 / 3 / 5 个模型 |
| 精通 | 4 | 1、3 个模型达到 LV.20；1、3 个模型达到 LV.100 |
| 外观收藏 | 3 | 获得 5 / 10 / 25 个外观 |

“有效使用”沿用收藏者规则：当日至少 60 秒真实触摸且至少 3 次真实交互。预览和 AUTO 不计入。

## 周挑战

| 周序号 | 模板 | 完成条件 |
|---:|---|---|
| 0 | REDLINE | 在两个不同 UTC 日累计三次达到当前模型动力 Apex 门槛 |
| 1 | CHAIN REACTOR | 本周两次达到 20 Combo |
| 2 | PERFECT PROTOCOL | 本周完成三次当前机制的 Perfect 动作 |
| 3 | THREE-CORE RAID | 三个不同模型分别达到有效使用条件 |

- `cycleIndex = floor(utcUnixSeconds / 604800)`；展示周期为当前 UTC 周。
- 持久化 `highestObservedCycleIndex`，设备时间回拨时不回到旧周期。
- 每周挑战奖励 15 Collector XP 和 2 碎片。
- 同一四周组完成全部模板，奖励周期总章、40 Collector XP 和 5 碎片。
- 周挑战错过后只需等待四周轮回，不产生永久绝版内容。

## 奖励经济

| 等级 | XP | 碎片 |
|---|---:|---:|
| Ignition | 5 | 1 |
| Overdrive | 10 | 2 |
| Apex | 20 | 3 |
| Singularity | 40 | 5 |

- 单玩具 Badge 奖励对应玩具 XP；收藏者与挑战奖励 Collector XP。
- 碎片为全局累计值，不消耗；20 / 40 / 60 / 80 分别解锁四枚 Badge 专属激光蚀刻贴花。
- 每项奖励必须以 Badge ID 或 `templateId@cycleIndex` 记录已领取，重新启动、重复 Publish 或迁移不能重复发放。
- 迁移一次性继承多个 Badge 时，只显示汇总通知，不排队播放几十次动画。

## 迁移与载荷

- 旧速度、手势和真实交互时长直接重新计算新目录。
- 旧 Collector 指标重新计算新的 13 枚目录。
- 旧离线 XP Badge 若曾达到任一门槛，授予一枚 Legacy“创始收藏”。
- 新增技巧、最高 Combo 和峰值力度没有历史数据时从零开始；不得伪造完成状态。
- 迁移版本独立、幂等；保留旧键至少一个发布周期。
- C# → Swift 目录载荷固定为 JSON v2；现有 native C 函数签名继续保留以兼容已导出的调用方，但 Swift 不再构造旧 Achievement 类型或解析两套视觉模型。旧持久化键的迁移由 C# 运行时幂等完成并至少保留一个发布周期。

## 安全与产品不变量

- Badge 只读取机制结果，不写 Rigidbody、角速度、阻尼、磁吸、相机或输入状态。
- 解锁触觉只能由 `BadgeUnlocked` 语义事件进入 Haptic recipe，再由 iOS renderer 输出。
- 稀有度文案只能写“难度等级”，不能写玩家百分比。
- 分享卡不包含用户名、设备 ID、精确位置或其他个人数据。
