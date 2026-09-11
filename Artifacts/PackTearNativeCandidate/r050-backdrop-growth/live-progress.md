# R050 实时进度

当前阶段：全部完成，等待视觉批准

- [已完成] `FidgetGachaPackPresentation.swift`
  - 粒子：首版 `0.11–1.04 pt` 不可见（07:13 退回）；改为 0.8–1.3 pt 细尘 + 少量 2.0–2.6 pt 白芯 bokeh，36–84 粒，档位色向白提 45%，黄金比分层。
  - 删除周期性整屏斜向过光规则。
  - 底部生长：1.3 s 线性时钟 + ease-out³；色相底与弧带延迟 0.55 s、用 0.6 s 跟上。
- [已完成] `FidgetProductUIComponents.swift`
  - 删除整屏斜向光带。
  - 新增 `ProductPackBottomGlowGrowth`；修正渐变中心落在屏外 25% 的定位错误（R049 版 ripple 不可见的原因）。
- [已完成] `FidgetGachaShippingStorefront.swift`
  - 每次切换 Pack 在 `.id(tier)` 上重建底部生长；色相底/弧带改用 `backdropFollowAnimation` 延迟跟随。
- [已完成] Swift 编译：`xcodebuild` `BUILD SUCCEEDED`（`/tmp/pack-tear-redo/r051e-swift-build.log`）。
- [已完成] 规则测试：`PASS 220/220`。
- [已完成] Simulator 录制六档往返：`r050-backdrop-growth-clear.mp4`（26.5 s）。
- [已完成] 抽帧检查：`growth-strip-10fps.png` 0.2–0.6 s 内暖色自底部升起，上方仍为前一档颜色。
- [已完成] 文档：`IMPLEMENTATION_STATUS.md` R049–R050 条目；设计圣经 `FDB-GAC-038`。
- [已完成] Unity EditMode 聚焦测试 `26/26`（修正过期断言 `storefrontPriceLabel` → `GachaPackPaymentRules.priceLine(`）。
- [未做] 真机复现「开包卡住」修复：需装机，待视觉批准。

事故记录：原线程 23:03 启动的 `simctl recordVideo` 客户端随对话中断被杀，`SimRenderingService` 继续向 `raw.mp4.sb-*` 写入 72 分钟至 11.6 GB；已终止并删除，磁盘回收 11 GB。新录制脚本 `/tmp/pack-tear-redo/record-r050.sh` 用 EXIT trap 保证录像器一定被停止。

更新时间：2026-09-08 07:25
