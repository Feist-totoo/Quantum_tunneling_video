# 当前进度

更新时间：2026-08-29（Asia/Shanghai）

当前主方案为 Blender 左侧主体 + 660×1080 Manim 右栏 + Manim/HTML 全屏段，最终在 DaVinci Resolve 中人工剪辑。Remotion 与旧 HTML 概率图不再作为正片主方案。

## 已完成

### F00000–F05544

- 核聚变、不确定性原理、波函数语言三段已经按配音全局帧重新生成。
- 当前交付帧数分别为 2769、1109、1667；均为 1920×1080、60 fps、无音轨。
- 逐动作表：`resource/final/06_resolve_aligned/F00000-F05544_源素材动作对齐表.md`。

### F05545–F09122｜Blender 右栏

- 旧的 HTML 公式层和概率图层已由一个完整 Manim Alpha 轨替代。
- 输出 Alpha 母版及 Resolve 流畅版：`04...alpha.mov`、`04...resolve_cfr_intra.mp4`。
- 规格：660×1080、60 fps、3578 帧、qtrle/argb、无音轨。
- 方势场承接、V(x)/W/V₀、ψ、Re/Im 闪烁、概率密度、B/C/D/F 区域解、精确与近似透射率、概率图、Q 比例和电流 I 均按全局帧编排。
- 概率区现为双图：上方 0–100% 线性图，下方 `log₁₀P` 图；对数图顶部 `1` 代表 `10⁰`，整数刻度到 `-8`。
- 高度比较为橙色，按 0.8V₀→1.3V₀→V₀；厚度比较为紫色，按 0.5W→1.5W→W；图表内不显示 W、V₀。
- Q 比例与 I 的最终强调只做缩放/位移跳动，不再变色。
- CFR MP4 为 H.264 High 4.2、All-Intra、无 B 帧、1/60000 时间基，已完成全片解码校验。
- 右栏接触表已经检查：`resource/final/99_qa/blender_right_manim_voice_v1_contact.png`。

### F09123–F09708｜NB12

- 约瑟夫森结已从错误的 2DEG 平面模型改为两个超导电极夹一层薄绝缘势垒的标准 S–I–S 结构。
- 旧 NB13 的宏观电路、三人照片和能级作为缩小卡片在右侧依次弹出，不再取代主模型。
- 开头使用 `resource/final/04_source_images/science_references/blender_v5_f3578_transition_source.png`，按左侧对齐。
- 透视运动线半透明、快速延伸并顺时针旋转约 5°；约瑟夫森结在运动线出现 3 帧后开始由大而透明收束，旧圆圈已删除。
- 输出：`resource/final/06_resolve_aligned/05_nobel_macro_aligned_F09123-F09708_586f.mp4`。
- 规格：1920×1080、60 fps、586 帧、无音轨。

### F09709–F10795｜应用与结尾

- 应用段前 6 秒保留二维原理图与引导运动，NAND 从片内 00:06（全局 F10069）才开始浮现；随后 STM、CMOS 依次演示。
- NAND 在 F10273 归位，STM 在 F10413 归位，CMOS 在 F10637 准时结束。
- F10638 开始最终重排；量子隧穿居中上移，三项应用在下方横排，三支箭头在最后 120 帧完成。
- 输出：`resource/final/06_resolve_aligned/06_applications_aligned_F09709-F10795_1087f.mp4`。
- 规格：1920×1080、60 fps、1087 帧、无音轨。

### 交付整理

- 精确动作表：`resource/final/06_resolve_aligned/F05545-F10795_素材动作对齐表.md`。
- Manim 可编辑源码：`resource/final/03_manim/editable_source/`。
- 自动重建脚本：`resource/final/06_resolve_aligned/rebuild_F05545-F10795.ps1`。
- Resolve 导入说明：`resource/final/RESOLVE_IMPORT_AND_SYNC.md`。
- 旧 04a/04b、05a/05b、应用 V8 已移出当前交付目录，暂存于 `_archive/superseded_20260829/`，避免 Resolve 误选。

## 尚未完成

- Blender V5 的 V1 完整渲染仍缺失。目标为 1300×1080、60 fps、3578 帧，对应全局 F05545–F09122。
- 当前 `resource/final/01_blender/blender_final_v5_voice_aligned_1080p60.mp4` 只有 3094 帧（51.5667 秒），不能作为最终交付。
- 用户完成 Blender 图像序列/视频渲染后，再将它放入 Resolve V1；本次完成的 Manim Alpha 可直接放 V2。
- 配音与字幕尚未重新导入 Resolve；按用户要求，先完成画面素材，之后再处理音轨和字幕。
- 不包含旁白、BGM，也未启动最终成片渲染。
