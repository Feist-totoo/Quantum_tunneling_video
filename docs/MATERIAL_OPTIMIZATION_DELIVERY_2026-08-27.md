# 素材优化交付记录（更新于 2026-08-28）

## 交付原则

- 统一画面基准为 1920×1080、60 fps。
- 取消 179.5 秒硬上限，优先完整保留和复用素材。
- 当前素材完全静音：不含旧台词、旁白、字幕、音乐或临时音效。
- DaVinci Resolve 是当前主剪辑方案；Blender、HTML、Manim 均以独立素材交付。
- 黑底与青、红、蓝、黄、橙、紫语义色保持 3Blue1Brown 式数学可视化秩序。

## 完整素材建议顺序

| 段落 | 时长 | 内容 |
|---|---:|---|
| 核聚变 V9 | 49.00 s | 微光、太阳拉远、动态温标、经典势垒和硬切问号 |
| 不确定性 V4 | 16.4167 s | 上下同步的一维位置/动量动画与海森堡剪影 |
| 波函数 V2 | 11.45 s | 实部、虚部、模平方、势能语言与薛定谔剪影 |
| Blender V3 | 90.00 s | 完整三维隧穿、参数变化、坍缩和多次试验 |
| 宏观电路转场 V1 | 9.00 s | 约瑟夫森结、三位诺奖得主和二维势垒推入 |
| 应用 V8 | 21.0833 s | NAND、STM、CMOS 中央演示与最终同屏布局 |

完整主动画约 196.95 秒。NASA/NIST B-roll 可按新版旁白继续插入。

## Blender 内部同步

- 00:00–00:29：完整镜头移动、势垒进入和波包继续运动。
- 00:29–00:34：公式三步高亮；Blender 同步强调势垒差、波函数和厚度/透射项。
- 00:34–00:48：概率图显示，数值每三帧更新。
- 00:48–00:57：厚度研究。
- 00:57–01:06：高度研究，范围 0.8V₀ 到 1.3V₀。
- 01:06–01:09：比较停留和图表退场。
- 01:09–01:30：坍缩、粒子系综和多次透射/反射。

## 当前入口

- 最终素材库：`resource/final/`
- 导入与同步：`resource/final/RESOLVE_IMPORT_AND_SYNC.md`
- 机器可读清单：`resource/final/ASSET_MANIFEST.json`
- Blender 最终工程：`resource/final/01_blender/editable_source/quantum_tunneling_scientific_v3_fullrender.blend`
- HTML 可编辑源：`resource/final/02_html/editable_source/`
- Manim 可编辑源：`resource/final/03_manim/editable_source/`

## 验收状态

- Blender 母版：5400 帧、90 秒、1920×1080、60 fps、无音轨，通过。
- Blender 同步参考合成：5400 帧、90 秒、1920×1080、60 fps、无音轨，通过。
- HTML 透明层：ProRes 4444、60 fps、Alpha、无音轨，通过。
- 四段 Manim：恒定 60 fps、1920×1080、无音轨，通过。
- 核聚变、波函数、不确定性、宏观电路、三应用与 Blender 同步接触表：通过。
