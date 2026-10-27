# DaVinci Resolve 导入与同步

## 项目设置

- 时间线：1920×1080，60 fps。
- 当前有效画面：F00000–F10795。
- 素材均无音轨；配音与字幕留在独立音频/字幕轨，画面不烘焙台词或 BGM。
- 工作目录：`C:/Users/liuzh/Desktop/1/resource/final/06_resolve_aligned`。

## V1 顺序

1. F00000：`01_fusion_aligned_F00000-F02768_2769f.mp4`
2. F02769：`02_uncertainty_aligned_F02769-F03877_1109f.mp4`
3. F03878：`03_wavefunction_aligned_F03878-F05544_1667f.mp4`
4. F05545–F09122：留给 Blender V5 的 1300×1080 最终渲染；左侧对齐。
5. F09123：`05_nobel_macro_aligned_F09123-F09708_586f.mp4`
6. F09709：`06_applications_aligned_F09709-F10795_1087f.mp4`

NB12 的最后一帧与应用段第一帧使用同一二维隧穿构图，直接相接，不加交叉溶解。旧 NB13、旧 05a/05b 和旧应用 V8 不再使用。

## V2：Blender 右侧 Manim

优先直接导入已经锁定左右边缘的单文件：

`04_blender_manim_composite_aligned_F05545-F09122_3578f.mp4`

放置在 V1 的 F05545，Position X/Y 均为 `0`，Zoom X/Y 均为 `1`。该文件
已经是 1920×1080，不再需要 Resolve 自动缩放或手动平移。

以下分轨方式仅作为可编辑备用方案：

在 F05545 放入以下二选一文件：

`04_blender_right_manim_aligned_F05545-F09122_3578f_alpha.mov`

`04_blender_right_manim_aligned_F05545-F09122_3578f_resolve_cfr_intra.mp4`

设置：

- 保持原始 660×1080 尺寸，不缩放。
- Position X = `+630`，使素材右边缘与 1920 px 画面右边缘重合。
- Position Y = `0`。
- Alpha MOV：合成模式保持 Normal，保留透明通道。
- CFR MP4：不透明黑底，但只占右侧 660 px；H.264 All-Intra、无 B 帧，Resolve 播放更轻。右栏本身为黑色时优先使用它。
- 最后一帧必须落在 F09122。

## Blender 时间映射

- 工程：`C:/Users/liuzh/Desktop/1/quantum_tunneling_scientific_v5_voice_aligned.blend`
- Blender 本地 F00001 = 全局 F05545。
- Blender 本地 F03578 = 全局 F09122。
- 全局帧 = Blender 本地帧 + 5544。
- 输出建议为 PNG 图像序列；确认后再编码，避免长片渲染中断导致整段损坏。

## 精确动作参考

- F00000–F05544：`06_resolve_aligned/F00000-F05544_源素材动作对齐表.md`
- F05545–F10795：`06_resolve_aligned/F05545-F10795_素材动作对齐表.md`
- 非 Blender 画面批注：`C:/Users/liuzh/Desktop/1/voice/非Blender素材时间轴标注.txt`
- 临时接触表已完成验收并移入回收站；当前交付只保留正式素材、可编辑源文件与说明文档。

## 已验证规格

|文件|尺寸|fps|帧数|音轨|
|---|---:|---:|---:|---|
|04 Alpha|660×1080|60|3578|无|
|04 CFR MP4|660×1080|60|3578|无|
|05 NB12|1920×1080|60|586|无|
|06 应用|1920×1080|60|1087|无|
