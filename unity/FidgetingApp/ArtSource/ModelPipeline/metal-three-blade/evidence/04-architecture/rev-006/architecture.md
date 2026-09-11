# Gate 04 · 交互形态 / 零件架构 rev-006（运动学拆分）

触发：用户 2026-09-08 07:13 “OK 还有一点就是这个陀螺的三个页面是可以转的，你确保在结构上是正确的，没问题的话你可以推进下一步”，
13:21 看转台低角度帧后：“这个不是一体的，叶片是分开转的”。

rev-005 的毂座（`Hub_Seat_Top/Bottom`）坐在实心转子上，盖、毂、叶片在渲染里读成一整块。rev-006 把它改成真正的两件式结构：

| 零件（Blender 对象） | 动 / 静 | 枢轴 | 说明 |
|---|---|---|---|
| `Rotor_Body` | **旋转** | 世界原点，绕 +Z | 转子一件：三叶 + 盖下连接环；**中心通孔 R0.425 R**；顶面 T/F/C 硬切 + A 层 + 鸢形/Λ 过渡到中面；六个漏斗坑（上下镜像）；盖下顶面切平到 ±t/2 |
| `Cap_Top` / `Cap_Bottom` | 静止（手指夹持） | 同轴 | 14 扇凹盘（8° provisional）+ 14 楔冠环 + 14×2 裙；盖缘 R0.485 |
| `Hub_Core` | 静止（轴心承托 / 轴承壳，与两盖一体夹持） | 同轴 | **一根 R0.41 R 圆柱，从下盖唇穿过转子通孔到上盖唇**（两端埋入盖体 0.002 R）；暗材质 |
| `Cut_*` | — | — | 布尔刀体（不渲染、不导出） |

间隙（全部按 2R = 85 mm provisional 换算）：

- 径向：转子孔 0.425 R − 毂 0.41 R = **0.015 R ≈ 0.64 mm**（转子面处围绕毂的暗环）。
- 竖向：盖唇 z = t/2 + 0.0457 R；盖足迹内转子最高点 z = 0.1185 R → **≈0.52 mm**。
- 盖下连接环最窄处（缺口角平分线，射线实测）**0.070 R ≈ 2.97 mm**（要求 ≥ 0.05 R）。
- 盖缘外悬毂 0.075 R ≈ 3.2 mm（v18/v20 的 0.03 R 因连接环宽度约束放大；用户 18:33 只说“稍微盖住”，量为占位）。

转子质量特性（均匀密度，rev-008 评估网格）：质心离轴 7e-5 R；|Ixz|,|Iyz| / Izz < 1e-6（Z 为主轴）；Izz / Ixx = 1.98（绕 Z 稳定）。

Unity 挂点：`Fixed_Root`（Cap_Top、Cap_Bottom、Hub_Core，不旋转） / `Rotor_Root`（Rotor_Body，`RotorRigidbodyController` 驱动，局部 +Y = Blender +Z，零初速）。
运动学：仅绕 Z 自由旋转；无滑动、无棘轮。手感 / 阻尼 / Haptics 不在本 Gate。

## 证据

- `06-geometry/rev-008/gate06-checks.json` → `kinematics`（8 项全过）。
- `06-geometry/rev-008/checks/kinematic-section.png`、`kinematic-section-macro.png`（半剖：静止件蓝、转子灰）、`kinematic-junction-macro.png`。
- lookdev rev-005 `renders/kinematic-*.png`（Cycles 同视角）。

## 决定

待用户确认（ready_for_review）。rev-005 的批准（18:52）保留为历史。
