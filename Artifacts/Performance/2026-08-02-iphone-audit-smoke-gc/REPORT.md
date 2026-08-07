# iPhone Release GC遥测冒烟 — 2026-08-02

结论：本轮未通过，不能作为60秒或30分钟性能证据。

- 设备：iPhone 15 Pro Max，iOS 26.6。
- 构建：非Development、IL2CPP、Release、arm64，签名安装并由CoreDevice启动。
- 审计启动成功，预热后取得413个Frame Timing样本。
- 应用随后进入后台；汇总为`reason="backgrounded"`、`passed=false`。
- 短样本`phys_footprint`峰值320.1 MiB，可用内存最低3055.9 MiB，thermal始终Nominal。
- `gcCounterAvailable=false`；Unity官方说明`GC Allocated In Frame`在Release Player不可用，
  所以日志中的0平均值不能解释为`0 B/frame`。
- 控制台证据：`device-console.log`。

CPU/GPU和漏帧数只覆盖预热后的数秒，且首末5分钟稳定性不存在，不能用于验收。下一次
正式测试必须保持应用前台完成四个交互阶段；GC另用目标iPhone Development Player连接
Unity Profiler验证。源代码随后已把计数缺失显示为`-1`和`externalGcCheckRequired=true`，
并让Release脚本同时校验`reason="completed"`与`passed=true`。
