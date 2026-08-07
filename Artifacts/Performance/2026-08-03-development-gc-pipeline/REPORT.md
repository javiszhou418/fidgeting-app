# iPhone Development GC链路复核 — 2026-08-03

结论：构建与安装链路通过，GC运行证据缺失。

## 已证明

- Unity Development + Connect With Profiler工程导出成功，使用独立目录
  `Builds/iOS/FidgetingAppDevelopment`和`DerivedDataDevelopment`，不会覆盖Release导出物。
- IL2CPP、arm64、Xcode Release配置签名构建成功。
- Development包以产品唯一Bundle ID覆盖安装到iPhone成功。
- Development `Data/boot.config`包含`profiler-enable=1`；Release对应文件不包含该项。
- 最新非Development Release随后重新导出、签名、构建，并以`--no-launch`恢复覆盖安装成功。
- 最终EditMode回归：`85/85 passed`，脚本`zsh -n`通过。
- CoreDevice锁屏预检已接入安装与审计脚本；实测锁定状态分别在约1.8秒和0.6秒退出，
  不再进入Unity/Xcode构建或开始计时。
- Release成功后会自动生成`summary.json`与`REPORT.md`，并强制声明环境温度、45%至55%亮度
  及`unplugged`供电状态。
- Release遥测本身还会读取电池状态/电量和`UIScreen.brightness`，交叉验证声明；充电、满电
  接电、未知供电状态或亮度越界都会令`environmentPassed=false`。battery monitoring只在显式
  审计对象存活期间启用并恢复原状态。
- 包含上述原生环境门槛的最新Release已于2026-08-03 00:18 CST完成Unity重新导出、Xcode
  `BUILD SUCCEEDED`和锁屏恢复安装；未启动。iPhoneOS Objective-C++ syntax check与最终
  EditMode `85/85 passed`。

## 未证明

Development包安装后，设备已经锁屏。CoreDevice取得DDI tunnel，但SpringBoard明确以
`Locked`拒绝启动应用，因此没有`FIDGET_PERF_AUDIT_START`、GC progress或summary。不能从
Development工程存在、`profiler-enable=1`或安装成功推断`GC Alloc=0 B/frame`。

正式执行仍需解锁手机、保持应用前台，并在5分钟内持续覆盖自由轮、高速棘轮、模型切换、
拆解/复原和混合操作：

```zsh
./scripts/ios_build_and_install.sh --development
./scripts/ios_performance_soak.sh --development-gc
./scripts/ios_build_and_install.sh
```

只有最终日志同时包含`mode="developmentGc"`、`developmentBuild=true`、
`gcCounterAvailable=true`、`gcPassed=true`、`reason="completed"`和`passed=true`才通过。
