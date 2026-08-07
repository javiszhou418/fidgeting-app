# Combo Reward Motion Research

最后更新：2026-08-07

## 研究结论

Combo 的奖励感不等于增加更多装饰。有效反馈必须让玩家在很短时间内同时读到三件事：数值真的增长、这次增长有多重要、我如何继续获得它。GDC 的奖励系统与游戏体验研究都把反馈视为奖励本身，并强调反馈强度要与事件重要性匹配；DiGRA 的 juicy design 框架同样把清晰、即时和分层的视听响应作为可操作维度。Arkham Shadow 的节奏 Combo UI 进一步强调玩家只有很短的响应时间，组件必须减少认知延迟，不能只用静态截图判断动效。

因此本产品采用以下规则：

1. 数字优先：连击数字必须是第一视觉层级，`COMBO · 超频` 只解释语义，不能与数字等权。
2. 连续增长与里程碑分级：普通 +1 使用短促的压缩、上冲和回弹；5 / 10 / 20 以及 20 后整十才增加数字内扫光、数字残影和短火花。
3. 反馈强度来自已获得的进展：2–4 / 5–9 / 10–19 / 20+ 四档同步提升静态字号、瞬时过冲、辉光与里程碑密度，不用随机爆发。
4. 运动方向表达增长：旧数字向上退出，新数字从下方进入；固定数字区和等宽字体防止 9→10、99→100 抖宽。
5. 动画必须可取消：20 Hz telemetry 更新不能重启动效；快速连续增长直接追最新 count，不能排队播放过期庆祝。
6. 容器不抢奖励：不使用票券描边、胶囊周圈或整个卡片弹跳。扫光只穿过数字字形，残影也复制数字本身。
7. 克制地保持产品感：不做全屏 shake、老虎机式无限循环、随机奖励或惩罚性破连；断连只淡出。
8. 可访问性是同一套反馈的降级：Reduce Motion 使用 0.11 秒数字交叉淡化，关闭位移、缩放、扫光、残影和火花，但保留字号层级与准确数值。
9. 连续奖励必须由真实活动驱动：Combo 激活后，每 120° 旋转或推牌等效机械进度产生一次展示 count，并以 0.16 秒最短间隔限制在 6.25 次/秒；低于 4 rad/s 不累计。它不发 XP、不改变 tier，AUTO 与 Library 不允许刷数。
10. 大反馈只属于明确里程碑：默认跨入 10、20、30…时，从 Unity 实时投影出的模型轴心先释放核心闪光，再在 50 ms / 100 ms 错拍中连续喷出三道 burst ring。每道 ring 都由四段不同亮度的圆弧组成，并使用不同扩散终点和缺口转角，不能退化成完整、同速、等亮的同心圆。中心能量雾不是模糊圆环，而是两层不规则云轮廓、九个局部湍流雾团和七条旋散丝缕，随后慢于脉冲环消失。全部层都按当前模型平面的透视压缩成椭圆，并跟随相机视角改变倾角和短轴比例，不能始终正对屏幕。普通 +1 不触发；不增加彩色、科技刻度或粒子礼花，也不给 Combo 字样加描边或常驻周圈。Reduce Motion 下保持中心柔和闪光，不做大范围位移。

## 本轮落地

- `RewardingComboPill` 替换为无边框的 `RewardingComboLockup`。
- 数字从原来的 22 pt 提升为按等级变化的 38 / 42 / 46 / 50 pt Oxanium Heavy 等宽数字。
- 普通增长使用 45 ms 压缩蓄力、85 ms 数字交接和可取消 spring 落定。
- 5 次：白色扫光只通过数字 mask。
- 10 次：数字扩散残影 + 4 枚短火花。
- 20 次及之后每 10 次：更强数字残影 + 8 枚短火花，峰值瞬时缩放为 1.40。
- 背后只保留无边界的径向暗场确保复杂模型背景上的可读性；不存在 `.stroke` 或 `.productGlass` 胶囊。
- 数字、`×` 与 `COMBO · 档位` 全部改为中性白色；不再读取 `combo.accent`，避免廉价霓虹感。
- `SpinnerComboRuntime.RecordMechanicalActivity` 将真实机械行程转换为更密集、可读的展示计数；快速转子直接追最新 count，不排队补播旧脉冲。
- `FidgetComboHalo.swift` 是生产光晕和设置页工具的共同原生源码。`ComboHaloTuning` 默认 `10 / +10 / 920 ms / 104% / 34%`，以两控制点 cubic Bézier 驱动第一道 burst ring 扩散，独立线性时间轴错开五条包络：核心闪光在 20% 时间前结束；主环在 5.5% 达峰并于 48% 消失；第二道环从 5% 启动、12% 达峰并于 64% 消失；第三道环从 10% 启动、18% 达峰并于 80% 消失；能量雾从 1% 启动、10% 达峰并持续到末尾。环组尺寸改按竖屏短边而非屏幕对角线计算，避免扩散后只剩上下两条巨大弧线。`ComboHaloBrokenRing` 生成四段不等亮圆弧；`ComboHaloMistCloud`、九个湍流雾团与 `ComboHaloMistWisps` 七条旋散丝缕共同生成中心云雾。`ComboCenterHalo` 用 `AnimatablePair` 同时逐帧消费扩散与线性时间进度；设置页 `ComboHaloTuningPanel` 复用完整分层渲染器，可实时修改、持久化、预演并恢复推荐值。
- `ComboHaloProjectionRules` 从模型中心、旋转轴/表面法线和活动 Camera 投影两个平面切向量，按屏幕像素比例求椭圆奇异值、短轴比和角度；`ComboHaloProjectionNativeBridge` 以 HUD 更新率只读发布给 SwiftUI。金属三叶、镜钢四翼、石墨双叶使用机械旋转轴和 authored focus，经典蓝色使用 live bounds 中心和世界旋转轴，磁吸推牌使用 live bounds 中心和产品表面法线。该链路不写 Rigidbody、相机、交互或 Haptic。
- `SpinnerExperienceFeedbackLayer` 只在 `milestoneCrossed(previousCount:newCount:)` 成立时播放 `ComboCenterHalo`；逻辑能识别合并快照跨过门槛的情况，计数归零或倒退不会误触发。

## 验证

- 同一 Swift 源码通过 iPhoneOS 15 `swiftc -typecheck`。
- Combo cadence / 标签 / 原生 UI 聚焦 EditMode `4/4` 通过：`Logs/ComboCadenceLabelsFocusedTests.xml`。
- 完整 EditMode `173/173` 通过：`Logs/ComboCadenceLabelsFullEditModeTests.xml`。
- 中心光晕 Swift 门槛/钳制/投影/五层透明度包络规则测试 `47/47` 通过，shipping iPhoneOS 15 typecheck 与 Simulator DEBUG 编译通过。Unity 投影数学测试覆盖 top-origin 中心、0°/−45° 倾角和 `0.5/0.25` 短轴比，结构断言同时锁定 920 ms 推荐值、`AnimatablePair` 双进度、三道断裂脉冲环、中心不规则云雾/湍流雾团/旋散丝缕及四个模型平面压缩值；`SpinnerProgressionTests` 为 `34/34`，完整 EditMode 为 `180/180`，报告 `Logs/ComboHaloReferenceFocusedTests.xml`、`Logs/ComboHaloReferenceFullEditModeTests.xml`。
- 真实原生实现预览位于 `Artifacts/ComboHaloNativePreview/`：38% 五角度定格、曲线工具截图与 60fps 循环视频均由 shipping SwiftUI 源码编译，并叠加 Unity 正式场景帧；`combo-halo-burst-contact-sheet.png` 以紧凑时间线单独展示核心闪光、延迟回声和末段能量雾。用户已查看细化预览并明确要求推送，Device visual push gate 已满足；最新源码已重新完成 Unity 导出与 Xcode Release 构建，`0.1.0 (20)` 已覆盖安装并启动，设备回读 PID 18462。真机动态观感仍待用户肉眼验收。
- 动态视觉效果仍须在 iPhone 上验收；编译与源级断言不替代真实帧节奏、复杂背景对比和 Reduce Motion 肉眼检查。

## 参考

- [GDC：Reward Psychology Without the Neurotrash](https://www.gdcvault.com/play/1024181/Throwing-Out-the-Dopamine-Shots)
- [GDC：Meta-Game Design — Reward Systems that Drive Engagement](https://www.gdcvault.com/play/1012851/Meta-Game-Design-Reward-Systems)
- [DiGRA：Good Game Feel — An Empirically Grounded Framework for Juicy Design](https://doi.org/10.26503/dl.v2018i1.936)
- [GDC：Punching Across the Room in Batman: Arkham Shadow](https://media.gdcvault.com/gdc2026/Slides/Darcey_Ryan_Punching%2BAcross%2Bthe%2BRoom%2Bin%2BBatman_%2BArkham%2BShadow.pdf)
- [GDC：Don't Juice It or Lose It](https://www.gdcvault.com/play/1020861/don-t-juice-it-or)
- [Real Time VFX：18 层 Overwatch-inspired 爆发拆解](https://realtimevfx.com/t/stylized-frag-launcher-explosion-overwatch-inspiration-breakdown-posted/1894?page=2)
- [Real Time VFX：Pulse Cannon 多重 burst ring 拆解](https://realtimevfx.com/t/step-by-step-vfx-breakdown-pulse-cannon-effect/3161)
