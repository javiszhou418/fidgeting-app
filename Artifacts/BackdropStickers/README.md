# 灰色背板白色贴纸素材

本批次从 `IMG_5837.PNG` 的原始 1290 × 2796 像素截图中提取了 24 枚完整可见的白色图形贴纸。

## 交付位置

- Unity PNG：`unity/FidgetingApp/Assets/Resources/ProductStickers/BackdropWhite/`
- 矢量 SVG：`Artifacts/BackdropStickers/SVG/`
- 总览图：`Artifacts/BackdropStickers/backdrop-stickers-contact-sheet.png`
- 原图与 AI 清理参考：`Artifacts/BackdropStickers/Reference/`
- 裁切坐标、文件映射和未提取清单：`Artifacts/BackdropStickers/manifest.json`

## 规格

- 每枚 PNG 均为 1024 × 1024、RGBA、透明背景、白色图形。
- 图形在方形画布内居中，保留原图中的旋转角度，并预留约 9% 安全边距。
- SVG 由清理后的轮廓通过 Potrace 追踪生成，是可编辑路径，不是嵌入的位图。
- PNG 使用白色 RGB + Alpha，可在 Unity 材质中通过 Tint 改色。
- Unity 贴图导入保持 Mipmap，并使用 Clamp，以减少 3D 模型贴花边缘串色。

## 准确性边界

生产素材只使用了原照片中完整可见的轮廓。AI 清理图仅用于判断遮挡关系，没有用于 24 枚正式 PNG/SVG，因为它会改变或臆造被遮挡的标志。

被人物、App 界面、画面边缘或前景展台挡住的 12 枚图形没有伪造补全，详见 `manifest.json` 的 `not_exported_because_occluded_or_cropped`。如需完整还原这些图形，需要无遮挡正面照片或原始 Logo 文件。

## 重新生成

```bash
python3 scripts/extract_backdrop_stickers.py \
  --source /path/to/IMG_5837.PNG \
  --png-dir unity/FidgetingApp/Assets/Resources/ProductStickers/BackdropWhite \
  --svg-dir Artifacts/BackdropStickers/SVG \
  --artifact-dir Artifacts/BackdropStickers
```

这些文件已通过 `ProductStickerCatalog` 绑定到外观编辑器；同一批 PNG 同时作为
Unity 贴花纹理和 iOS Grid thumbnail 的唯一视觉源。
