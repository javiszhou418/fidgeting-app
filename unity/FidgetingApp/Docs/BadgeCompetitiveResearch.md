# Badge 竞品研究与结论

最后更新：2026-08-08

## 目标与方法

本专项研究 Badge 如何同时承担目标提示、掌握证明、收藏物和分享素材，而不是只把现有 SF Symbol 换成彩色图标。样本覆盖健身产品、游戏平台和高频游戏化产品；评价维度固定为视觉语言、状态模型、难度结构、进度、奖励、分享、时间压力和适配 Fidgeting 的风险。

主要公开依据：

- [Apple Game Center / WWDC20](https://developer.apple.com/videos/play/wwdc2020/10145/)：标准、渐进、隐藏成就；独立 artwork；图中避免文字；正方形 512/1024 资源；解锁当下反馈。
- [PlayStation Trophies](https://www.playstation.com/en-au/support/games/how-to-earn-trophies-on-playstation--consoles/)：Bronze/Silver/Gold/Platinum 等级与基于真实获得率的 rarity 是两个不同维度。
- [Steam Achievements](https://partner.steamgames.com/doc/features/achievements?l=schinese)：进度统计、未获得/已获得图、隐藏状态、离线缓存和统计一致性。
- [Duolingo Achievements](https://blog.duolingo.com/achievement-badges/)：入门目标、长期稀有目标、隐藏惊喜、个人纪录、统一陈列和分享。
- [Kyewski & Krämer, 2018](https://www.sciencedirect.com/science/article/pii/S0360131517302506)：Badge 本身不保证长期动机或表现提升，私密可见 Badge 甚至可能比社交可见评价更好。
- [Badge Design Framework](https://games.jmir.org/2019/2/e14342/)：Badge 应表达目标、学习/掌握路径和获得意义，视觉不能脱离行为设计。

## 竞品矩阵

| 样本 | 强项 | 局限 | 对 Fidgeting 的取舍 |
|---|---|---|---|
| Apple Fitness / Activity | 立体、材质统一、收藏感强，重要奖章有仪式感 | 同构圆章较多，技巧差异弱 | 采用材质和展示品质，不复制轮廓与图形 |
| Apple Game Center | 状态和进度模型清晰，独立 artwork，隐藏成就成熟 | 系统容器弱化产品自己的世界观 | 采用四状态和两行内短文案，使用自有视觉 |
| PlayStation | 等级立即可懂，稀有章具有强烈地位感 | 真实 rarity 依赖平台全局数据 | 采用四级难度，不显示伪造全球百分比 |
| Xbox | Gamerscore 把不同成就汇入长期身份 | 分数可能让用户只追效率 | XP 只作小奖励，Badge 仍以掌握和收藏为主 |
| Steam | 锁定/解锁图、隐藏成就和进度统计灵活 | 不同游戏美术品质不一致 | 每枚章独立核心符号，锁定时仍保留目标线索 |
| Duolingo | 简单、稀有、惊喜和个人纪录共同形成旅程 | Streak 容易制造损失焦虑 | 使用高强度挑战，但不扣进度、不永久绝版 |
| Strava | 挑战 Badge 与具体活动/时间段绑定，陈列明确 | 参与型 Badge 容易稀释掌握含义 | 周挑战独立于永久掌握 Badge，并明确到期时间 |
| Nike Run Club | 高对比图形和个人最佳记录识别快 | 同类数字纪录可能重复 | 保留少量关键阈值，减少纯累计档位 |

## 分类与适配结论

适合进入产品：

1. **成长里程碑**：低门槛起步和长期目标，必须显示当前值与目标值。
2. **技巧挑战**：Clean、Power、Speed、Endurance、Perfect，体现动作质量而非单纯次数。
3. **个人纪录**：峰值动力和最高 Combo，强调“超过自己”。
4. **组合挑战**：把真实输入、速度和持续运动组合为高难目标。
5. **收藏与精通**：跨模型使用、等级和外观收藏，支持长期图鉴。
6. **隐藏惊喜**：只用于三个高级技巧章，不能把主成长路径全部藏起来。
7. **周期挑战**：有截止时间但四周后轮回，不形成永久错失。
8. **纪念章**：仅承接无法映射的旧版离线成就，不与技巧难度混在一起。

不适合进入产品：

- 同一个中心图标只换颜色：会让收藏变成表格，无法形成达成记忆。
- 图中直接写 `100K`、`3.5 KM/H`：缩小时不可读，也破坏国际化；数值应放在标题与详情。
- 把离线 XP 作为掌握证明：用户没有即时控制，不能形成能力反馈。
- 连续六七档纯次数累计：鼓励刷量，缺少玩法变化。
- 本机产品展示“全球稀有度”：没有账号和可信聚合数据，属于误导。
- 永久绝版、失败扣 XP、断签清零：与可重复触摸和低风险使用场景冲突。

## 方向结论

主方向是“高能游戏徽记”，但需要在三套子方向中确认正式母版：

- **A · Arc Reactor Core**：识别最稳、最适合小尺寸和常规四级成长。
- **B · Tactical Prism Insignia**：稀有度和 Raid 感最强，适合挑战与 Singularity，但尖角需收敛。
- **C · Forged Relic**：金属触感最贴近实体玩具，暖色较多，若全量使用会弱化当前冷色 UI。

推荐组合为 A 的可读结构、B 的高阶剪影、C 的表面材质；正式批量生产前必须获得视觉确认。
