# iPhone Release动态遥测冒烟 — 2026-08-02

结论：采样链路通过；发布性能结论数据不足。

- 设备：iPhone 15 Pro Max，iOS 26.6。
- 构建：非Development、IL2CPP、Release、arm64，签名安装并由CoreDevice启动。
- 激活：`FIDGETING_PERFORMANCE_AUDIT=1`与`--fidgeting-performance-audit`。
- 起始thermal：Nominal。
- 稳态冒烟：60秒，3,601帧。
- `phys_footprint`峰值：323.3 MiB。
- thermal最大值：0（Nominal）。
- 控制台证据：`device-console.log`第69行Start、第79行Progress。

本次在首个一分钟Progress后主动中止，目的只是验证Release控制台、Frame Timing循环、
原生内存和thermal采样可以在真实设备运行。没有完整`FIDGET_PERF_SUMMARY`，未记录环境温度、
屏幕亮度、电量/充电状态，也没有执行四个交互阶段，因此不能填写GPU/CPU P95/P99、
available-memory最低值、首末5分钟衰减、Jetsam或Energy结论。

323.3 MiB虽低于内部350 MiB绿色上限，但只剩26.7 MiB余量。正式30分钟测试期间如峰值超过
350 MiB，必须先定位Unity、SwiftUI、纹理、音频或诊断缓存，而不能把本次冒烟当作豁免。
