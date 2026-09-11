# R051 实时进度

当前阶段：全部完成，等待视觉批准 + 图案版本选择

- [已完成] 拖影根因：`ProductMatchedGeometry` / 镭射 overlay 按选中切换 `if/else` 分支 → 视图身份改变 → SwiftUI 淡入淡出两份 Pack。改为单分支常驻。
- [已完成] 镭射视差：`carouselOffset` = −0.45 × 连续档位，clamp ±0.90；`ProductPackIdleFloat` 改 `Animatable`，与 snap 弹簧同步。
- [已完成] 漂浮 6 pt/4° → 3 pt/2°。
- [已完成] 粒子：径向软发光 + 四角星芒，删光晕圆盘；上升速度 1× → 2.8×，切档行程连续。
- [已完成] 六档配色：accent 与 arc 色系对齐，harness 断言色相差 ≥ 40°。
- [已完成] 包装光栅：`Tools/GachaPackArtwork/build_pack_artwork.py`；中性源 `ArtSource/GachaPacks/Neutral/`；slab 徽记 188:240；三版候选 `../r051-pack-artwork/pack-artwork-variants-sheet.png`，shipping 用 `plate`。
- [已完成] Swift harness `PASS 238/238`；`xcodebuild` BUILD SUCCEEDED（`/tmp/r051/swift-build.log`）。
- [已完成] 录屏 `r051-foil-sync-clear.mp4`（24.9 s）；`snap-frames-30fps.png` 无重影；`motes-one-of-one-closeup.png` 星芒。
- [已完成] 文档：`IMPLEMENTATION_STATUS.md` R051；设计圣经 `FDB-GAC-039`（FDB-GAC-038 粒子形态条目标注被修订）。
- [未做] 图案版本由用户选定；真机装机待视觉批准；Unity EditMode 本轮无 C# 改动未重跑。

更新时间：2026-09-08 12:50

## R051b（12:55 用户：outline 版「这版好一点，但是饱和度可以降低一点」）
- [x] `build_pack_artwork.py` 默认 `--variant outline`；DESATURATE 0.55/0.46/0.44/0.60，1 OF 1 iridescence 0.30
- [x] 六张 body/flap/foil 重生成到 `Assets/Plugins/iOS/GachaPacks/`
- [x] Swift 预览 BUILD SUCCEEDED（`/tmp/r051/swift-build2.log`）
- [x] Simulator 录屏 `../r051b-outline-desat/r051b-outline-desat.mp4` + `strip.png`
- [x] IMPLEMENTATION_STATUS / 设计圣经 FDB-GAC-039 同步
- [ ] 视觉批准待确认，未推送手机

## R051c（13:20 用户：贵金属色 + 「中间这个黑块是什么」）
- [x] 黑块根因：inpaint 归一化高斯 1e-4 截断 → 改 distance_transform_edt 最近像素回填
- [x] METALS 贵金属箔（银/玫瑰金/黄金/黄金配紫晶/铂金）用于徽记描边 + 印字；STROKE_SCALE 递增
- [x] 重生成 18 张、Swift 预览 BUILD SUCCEEDED、录屏 `../r051c-metal-foil/r051c-metal-foil.mp4`
- [x] 文档同步
- [ ] 视觉批准待确认，未推送手机

## R051d（13:28 用户：比例再加大）
- [x] SLAB_HEIGHT 170 → 184，重生成、BUILD SUCCEEDED、录屏 `../r051d-slab-184/r051d-slab-184.mp4`
- [ ] 视觉批准待确认，未推送手机

## R051e（13:33 用户：特别糊）
- [x] 光栅 384×512 → 768×1024（S=2），旧徽记残影改平铺颗粒回填
- [x] 重生成、BUILD SUCCEEDED、全分辨率录屏 `../r051e-hires/r051e-hires-clear.mp4`
- [ ] 视觉批准待确认，未推送手机

## R051f（13:51 用户：字和图案看不清要重做；pack 再扁平贴合 slab）
- [x] 纯程序化袋体 280×375、DIN Condensed 文字、4× 超采样徽记、精确 foil 掩膜
- [x] Swift inset/fin span/interior width 同步，harness PASS 239/239
- [x] BUILD SUCCEEDED、六档 + 撕包录屏 `../r051f-flat-pouch/r051f-flat-pouch-clear.mp4`
- [ ] 视觉批准待确认，未推送手机

## R051g（14:55 用户：没厚度；上下加锯齿）
- [x] 枕形鼓度 / 内容物凸起 / 封口褶皱；fin 顶与袋底锯齿 8×4.5 px
- [x] BUILD SUCCEEDED、六档 + 撕包录屏 `../r051g-volume-serration/r051g-volume-serration-clear.mp4`
- [ ] 视觉批准待确认，未推送手机

## R051h（15:03 用户：越改越土，没有铝箔高级感）
- [x] 铝箔回到照片源（2×、回填旧徽记+文字、压窄 336→280）；程序化只做起伏/锯齿/徽记/文字
- [x] BUILD SUCCEEDED、六档 + 撕包录屏 `../r051h-foil-hybrid/r051h-foil-hybrid-clear.mp4`
- [ ] 视觉批准待确认，未推送手机
