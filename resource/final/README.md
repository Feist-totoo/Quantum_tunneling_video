# Resolve 最终素材库

本目录是当前唯一建议导入 DaVinci Resolve 的素材入口。当前有效画面为 F00000–F10795，60 fps；所有动画均无音轨，不含字幕、旁白或 BGM。

## 当前入口

- `06_resolve_aligned/`：按全局帧命名的 Resolve 正片素材与精确动作表。
- `03_manim/`：Manim 当前版本成片与可编辑源码。
- `02_html/`：核聚变 HTML 当前源文件；已被 Manim 取代的旧公式/图表成片已移入回收站。
- `01_blender/`：Blender 工程、脚本和旧参考视频。完整 V5 最终渲染仍待用户输出。
- `04_source_images/`：人物、诺奖与科学结构参考。
- `05_optional_broll/`：可选公共素材与许可记录。
- `07_endcard/`：片尾参考文献页的可编辑 SVG 与 1920×1080 PNG。
- 临时 QA/接触表已在验收后移入回收站，最终素材库不再携带预览截图。

## Resolve 最快放置

1. 时间线设置为 1920×1080、60 fps。
2. 依次放入 `06_resolve_aligned/01`、`02`、`03`。
3. F05545–F09122 在 V1 留给 1300×1080 Blender V5；同区间 V2 优先放 `04_blender_right_manim_aligned_F05545-F09122_3578f_resolve_cfr_intra.mp4`，Position X = `+630`。只有需要透明通道时才改用 Alpha MOV。
4. F09123 放 `05_nobel_macro_aligned_F09123-F09708_586f.mp4`。
5. F09709 放 `06_applications_aligned_F09709-F10795_1087f.mp4`。
6. NB12 与应用段直接相接，不加淡变。
7. 应用段结束后放入 `06_resolve_aligned/07_references_endcard_1920x1080.png`，建议停留 3–5 秒。

## 当前关键状态

- Blender 右栏已经由 Manim 重构为线性/对数双图，不再使用旧 04a/04b HTML 透明层；Q 比例与 I 只做跳动强调，不变色。
- NB12 主模型为标准 S–I–S 约瑟夫森结；旧 NB13 内容改为右侧依次缩小弹出，不再导入 05a/05b 两段旧文件。
- 应用段 NAND 在片内 00:06 才开始浮现。
- 应用段有效终点为 F10795，旧 F10796–F10813 尾帧已取消。
- `01_blender/blender_final_v5_voice_aligned_1080p60.mp4` 已由完整 PNG 序列重建为 3578 帧，并已重新生成左右合成素材。

详细参数见 `ASSET_MANIFEST.json`；完整操作见 `RESOLVE_IMPORT_AND_SYNC.md`。
