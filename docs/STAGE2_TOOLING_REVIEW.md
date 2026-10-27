# 第二阶段：工具、技能与插件审查

更新日期：2026-08-13

## 结论

第二阶段已完成第一轮高信号检索、安装与安全筛选。选型原则为：优先官方来源、活跃高星项目和高安装量技能；拒绝低社区验证、许可不适合、功能重复或需要不必要账户权限的候选。

## 已安装技能

### OpenAI 官方

- `playwright`：浏览器自动化和网页交互测试；用于更高效地检查素材网页、许可证页面和后续本地合成界面。
- `speech`：通过 OpenAI Audio API 生成旁白；当前仅安装，未配置密钥、未进行联网调用。
- `transcribe`：对参考视频或录音做转录和说话人区分；当前仅安装，未配置密钥。

### Remotion 官方技能库

- `remotion-best-practices`：程序化视频的动画、资源、音频、字幕和渲染规范。
- `remotion-create`：创建可维护的 Remotion 工程。
- `remotion-render`：预览、并发渲染和导出规范。
- `remotion-multimedia`：视频、音频、图片与透明图层的正确嵌入方式。
- `remotion-captions`：字幕导入、分段、强调与时间同步。

来源仓库 `remotion-dev/skills`，检索时约 3.3k GitHub stars；本次锁定提交 `2a204c9b71f7a98997128759cbd2ab557b197fd3`。

### OpenMontage 独立技能

- `manim-composer`：在编码前把科普概念整理成 3Blue1Brown 风格的逐场景方案。
- `manimce-best-practices`：Manim Community 的公式、坐标、变换、相机和样式规范。
- `ffmpeg`：转码、缩放、压缩、音频处理与母版兼容性。
- `video-edit`：本地剪切、拼接、叠加、变速与导出。
- `video-understand`：本地抽帧、场景检测与可选 Whisper 转录。
- `visual-style`：生成和复用颜色、字体、版式、动效与情绪规范。
- `playwright-recording`：录制网页操作和软件演示素材。
- `motion-graphics`：制作短时长数据图形、标题、标注和透明叠加层。

来源仓库 `calesthio/OpenMontage`，检索时约 47.7k GitHub stars，AGPL-3.0；本次锁定提交 `4eab34c5cfcccaa4f1970554928feccce73ee930`。仅抽取独立技能，不引入完整服务、外部账户或自动运行脚本。

### 审美增强

- `high-end-visual-design`：反模板化的视觉层级、字体、间距、色彩与动效判断。skills.sh 显示约 266.7k 次安装；安装器安全评估为 Safe、0 Socket alerts、Snyk Low Risk。该技能更偏界面设计，但其层级、密度和动效约束可迁移到图表、字幕和视频图形设计。

来源仓库 `leonxlnx/taste-skill`，MIT；本次锁定提交 `e988add20dab0fa97d7a76781c48961c8184288e`。

## 已有且继续使用

- Codex 内置 Browser 插件：优先使用应用内浏览器；需要网页语义数据时先选择专用连接器或 API，减少低效点击。
- Blender 专项技能：建模、材质、灯光、摄影机、动画、渲染、完整工作流和动画质量门槛。
- `imagegen`、文档、PDF、演示文稿、表格和可视化能力：作为未来通用项目工具保留。

## 本机工具状态

- Blender 5.2.0 LTS：可用。
- Node.js / npm / npx：可用。
- Manim Community：可用。
- MiKTeX（LaTeX、pdfLaTeX、XeLaTeX）：可用。
- FFmpeg：已发现本机随其他软件附带的副本，但尚未写入系统 PATH；第三阶段正式制作前应建立项目级固定入口并验证编码器。
- ImageMagick：未发现；当前不是本项目的阻塞项。

## 安全检查

- 已扫描新安装技能中的凭据、上传、网络请求、外部命令和动态执行模式。
- 没有发现读取 `DEEPSEEK_API_KEY.txt`、自动上传项目内容或安装后自启动行为。
- OpenAI Audio、Google Maps、ElevenLabs、Gemini 等只出现在可选示例中；均保持未配置，不会复用 DeepSeek 密钥。
- DeepSeek 密钥仍仅供 `https://api.deepseek.com` 使用。

## 排除项

- `AKMessi/vex`：约 69 stars，且 PolyForm Noncommercial 许可限制商业用途；不安装。
- `podo/design-agent-skills`：检索时 GitHub stars 为 0；不作为生产依赖。
- 大量浏览器自动化社区技能安装量低于 200；已有 OpenAI 官方 Browser 与 Playwright，因此不重复安装。
- RunComfy 视频技能虽有高安装量，但面向云端 Comfy 服务，涉及额外账户和远程素材处理；本项目优先本地处理，暂不安装。

## 待用户审批的远程插件

以下插件不会在未批准前启用：

- `GitHub`：读取仓库、issue、release 与许可证信息；适合第三阶段持续追踪开源素材来源和版本。
- `Remotion`：把程序化公式、图表、字幕和转场统一到可复现的视频工程；与本项目左 2/3 Blender、右 1/3 图表布局高度匹配。
- `Figma`：用于视觉规范、图表布局和字幕安全区的可视化评审；对未来 UI、海报和品牌项目也通用。
- `Canva`：适合快速生成封面、缩略图和社交媒体派生版，不作为核心科学动画工具。
- `HeyGen`：可用于 AI 配音、口型或数字人；本项目只建议将其作为可选配音方案，不默认上传工程素材。
- `HyperFrames by HeyGen`：适合自动动态图形和合成，但与 Manim/Remotion 有重叠；建议仅在后续需要大量快速 B-roll 时批准。

## 下一步门禁

等待用户审批上述远程插件和第二阶段工具选择。获批后进入第三阶段：网络素材检索、许可证记录、候选素材下载和缺口素材制作。

## FFmpeg 下载补记

已从 FFmpeg 官网列出的 Windows 构建源启动稳定版下载，但网络在 68,247,301 字节处超时，未取得校验文件，因此没有解压、没有执行、没有加入 PATH。该文件仅是未验证的缓存，第三阶段开始前必须续传完成并通过官方 SHA-256 校验后才能使用；在此之前继续标记为‘未完成安装’。
