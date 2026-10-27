# 量子隧穿科学可视化视频工程 (Quantum Tunneling Scientific Visualization)

本项目是一套完整的**高精度量子物理科普动画工程与多工具联合生产管线**。项目结合 **Blender 3D 渲染**、**Manim 数学动效引擎**、**HTML5/Canvas 粒子仿真** 与 **DaVinci Resolve 自动化剪辑脚本**，完整重现了粒子穿越势垒的量子隧穿（Quantum Tunneling）现象与宏观物理应用。

---

## 成果预览 (Result Preview)

> 成果视频全片共 10,796 帧（60 fps，约 3 分钟），画质为 1080p 纯净科学母版（无声）。下方为仓库内置的高清压缩演示：

https://github.com/user-attachments/assets/quantum_tunneling_preview.mp4

<div align="center">
  <video src="assets/quantum_tunneling_preview.mp4" controls="controls" width="100%"></video>
  <p><em>如浏览器无法直接播放，可直接查看或下载：<a href="assets/quantum_tunneling_preview.mp4"><code>assets/quantum_tunneling_preview.mp4</code></a></em></p>
</div>

---

## 叙事与科学推导结构

全片严格以 60 fps 绝对帧号精确对齐物理方程与视觉表现：

| 阶段 | 全局帧区间 | 帧数 | 核心内容与科学模型 | 呈现工具 |
|:---|:---:|:---:|:---|:---:|
| **01. 恒星核聚变** | `F00000–F02768` | 2769 | 太阳核心 1500 万 K 质子穿越经典物理无法逾越的库仑势垒 | HTML5 Canvas / Manim |
| **02. 不确定性原理** | `F02769–F03877` | 1109 | 海森堡不确定性关系 $\sigma_x \sigma_p \ge \frac{\hbar}{2}$ 推导与一维随机波包测试 | Manim Community |
| **03. 波函数语言** | `F03878–F05544` | 1667 | 薛定谔波动方程分解：实部、虚部与复波函数空间几何意义 | Manim / Python |
| **04. 势垒穿越与双图** | `F05545–F09122` | 3578 | **主视觉**：三维复波函数螺旋 $r=(x, \text{Re}\psi, \text{Im}\psi)$、指数衰减与线性/对数双图对比 | Blender 5.2 + Manim |
| **05. 宏观量子转场** | `F09123–F09708` | 586 | 2025 年诺贝尔物理学奖宏观量子现象、S-I-S 超导约瑟夫森结模型 | Manim 矢量动画 |
| **06. 技术落地与应用** | `F09709–F10795` | 1087 | 闪存浮栅写入（Fowler-Nordheim 隧穿）、STM 显微镜与超导量子比特 | Manim + 参考文献 Endcard |

---

## 技术架构与工具链

```
┌─────────────────────────────────────────────────────────────────┐
│                    Master Timeline (60 fps)                     │
│                sync/master_timeline_v4.json                     │
└──────────────┬──────────────────────────────┬───────────────────┘
               │                              │
       [左侧 2/3 画面]                [右侧 1/3 画面]
 3D 复波函数螺旋 & 势垒空间         实时能量图表 & 概率密度曲线
  (Blender 5.2 LTS EEVEE)             (Manim Community)
               │                              │
               └──────────────┬───────────────┘
                              ▼
                  离线帧合成与对齐流水线
                (Python / FFmpeg / NodeJS)
                              ▼
                   DaVinci Resolve 工程构建
               (Python API / resolve_edit/)
```

- **Blender 5.2 LTS (EEVEE AgX)**：构建势垒三维空间，粒子沿 $X$ 轴运动，解构为实部与虚部后合成为 $r=(x, \text{Re}\psi, \text{Im}\psi)$ 复螺旋空间轨迹。
- **Manim Community (v0.18+)**：绘制高质量矢量公式、坐标变换、线性与 $\log_{10}P$ 对数概率折线。
- **Web / Playwright 动效引擎**：利用 HTML5 Canvas 批量高帧率捕获核聚变库仑势垒粒子撞击与穿越动态。
- **DaVinci Resolve 脚本自动化**：提供自动化轨道生成、时间线 Marker 对齐与剪辑批处理脚本。
- **IndexTTS 本地配音桥接**：本地离线语音模型接口（免 API 密钥，仅在有音轨需求时调用）。

---

## 仓库目录结构

```
Quantum_tunneling_video/
├── quantum_tunneling_scientific_v5_voice_aligned.blend  # Blender 5.2 主工程（含粒子机位与着色器）
├── _add_v4_rhythm_markers.py                            # Blender 时间线节奏标记脚本
├── 脚本.md                                              # 全片解说词、帧级动作对应与科学注释
├── assets/
│   └── quantum_tunneling_preview.mp4                   # 成果全片压缩无声演示 (1080p->720p H.264)
├── resource/final/
│   ├── 02_html/editable_source/                        # 核聚变 HTML5/Canvas 源码
│   ├── 03_manim/editable_source/                       # Manim 全套动效推导与图表代码
│   ├── 04_source_images/science_references/            # 科学参考图谱
│   ├── 07_endcard/                                     # 参考文献与致谢页矢量/高清素材
│   ├── rebuild_F00000-F05544.ps1                       # 前半段自动化渲染对齐流水线
│   ├── rebuild_F05545-F10795.ps1                       # 后半段自动化渲染对齐流水线
│   └── RESOLVE_IMPORT_AND_SYNC.md                      # DaVinci Resolve 精确时间线导入指南
├── sync/
│   ├── master_timeline_v4.json                         # 全局 60 fps 镜头与公式同步基准
│   └── probability_frames_v3.csv                       # 势垒计算数值表 (每 3 帧一组)
├── scripts/
│   └── manim_sync_adapter_v3.py                        # 帧号映射与时间同步适配器
├── resolve_edit/                                       # Resolve 自动化脚本、字幕 (SRT) 与分镜表
├── ae_project/                                         # After Effects MCP 接入脚本与可编辑工程
├── cloud_render/                                       # 云端并行渲染调度脚本
├── tools/                                              # MCP 工具服务器、FFmpeg 封装与批处理脚本
└── docs/                                               # 制作规范、五阶段工作流与复核记录
```

---

## 快速复现与使用指南

### 1. 运行环境要求
- Python 3.10+
- [FFmpeg](https://ffmpeg.org/)（需配置在系统环境变量 `PATH`）
- [Blender 5.2 LTS](https://www.blender.org/)
- Node.js 18+ (用于 HTML 动画捕获)

### 2. 渲染 Manim 数学动效
```bash
# 安装 Manim
pip install manim

# 渲染不确定性原理段落
python -m manim -qh resource/final/03_manim/editable_source/uncertainty_reference_rebuild_v4.py

# 渲染势垒右侧双图表
python -m manim -qh resource/final/03_manim/editable_source/blender_right_manim_voice_v1.py
```

### 3. 打开 Blender 工程
启动 Blender 5.2，打开根目录下的 `quantum_tunneling_scientific_v5_voice_aligned.blend`。
- 关键帧焦点：`450–520`（势垒建立）、`510–960`（粒子机位切入与跟踪）、`1740–2040`（波函数高亮与复平面展开）。

---

## 科学参考文献

1. Griffiths, D. J., & Schroeter, D. F. *Introduction to Quantum Mechanics* (3rd ed.). Cambridge University Press.
2. Merzbacher, E. *Quantum Mechanics* (3rd ed.). John Wiley & Sons.
3. 2025 Nobel Prize in Physics: *Macroscopic Quantum Phenomena in Superconducting Circuits*.
