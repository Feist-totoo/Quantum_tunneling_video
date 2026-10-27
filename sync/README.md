# Blender / Manim / 剪辑统一同步

## 主键

所有动画以 60 fps 的 `blender_frame` 为唯一主键。时间秒数仅用于显示，不用浮点秒定位关键帧。

- `master_timeline_v4.json`：当前 Blender V4 的镜头切换、粒子/复波函数变化、概率波显隐和外部图层入点。
- `master_timeline_v3.json`：既有段落、画面布局、颜色和 Blender→Manim 偏移的回退基准。
- `probability_frames_v3.csv`：1200–4139 帧期间每三帧一行的概率和参数值。

## 推荐画面布局

母版为 1920×1080。常规核心讲解采用：

- 左侧 1280×1080：Blender 演示。
- 右侧 640×1080：Manim 公式、图表和解释。

4140–5399 帧建议让 Blender 临时回到全屏，突出坍缩和多次试验；也可根据后续剪辑审美继续保持分栏。

## Manim 对齐

Manim 透明图层从 Blender 第 1200 帧开始，其局部帧号为：

`manim_frame = blender_frame - 1200`

图表刷新点直接读取 CSV。每个 CSV 行间隔 3 帧，Manim 在两个刷新点间保持或插值；科学数值不得在 Manim 内重新计算。

V4 没有改变 1740 帧公式入点和 2040 帧图表入点。只在 Blender 内把 1050–1660 帧重构为“平面分量→三维复波函数→概率密度”，因此既有外部公式/图表素材无需重新计时。

## 剪辑对齐

剪辑母版也使用 60 fps。Blender 图层从母版指定的核心段起点开始，Manim 图层在对应的 Blender 1200 帧处对齐其透明序列第 0 帧。禁止先转成非整数帧率视频再对齐。

## 完整性检查

运行：

```powershell
python scripts/manim_sync_adapter_v3.py --check
```

它会验证帧号是否严格每三帧递增、所有概率是否有限且处于 0–1、Manim 偏移是否连续。
