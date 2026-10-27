# After Effects 重构工程

本目录用于把量子隧穿科普动画重构为可人工继续调整的 After Effects 2025 工程。DaVinci Resolve 现有时间线和素材保留为剪辑基准，不覆盖、不删除。

## 当前接入状态

- AE 主程序：`D:\MY_WORLD\Tools\Adobe After Effects 2025\Support Files\AfterFX.exe`
- AE 版本：25.0.0.53
- Codex 桥接：After Effects MCP 1.13.0
- 后台渲染：`D:\MY_WORLD\Tools\Adobe After Effects 2025\Support Files\aerender.exe`
- 媒体处理：`D:\MY_WORLD\Tools\ffmpeg-2026-08-09-git-6bbc22dc09-full_build\bin\ffmpeg.exe`
- 项目制式：1920×1080、60 fps、总时长不超过 179.5 秒

连接、实际写入、AEP 保存和预览帧回读均已通过。联调产生的临时合成、AEP 和图片已经清理，AE 当前回到空白项目。

## 使用方式

1. 从项目根目录的 `Adobe After Effects 2025.lnk` 启动 AE。
2. 打开 `窗口 → mcp-bridge-auto.jsx`，保持 Auto-run 开启。
3. 保持 AE 运行，Codex 即可读取和修改当前 AEP。
4. 人工调整时直接在 AE 时间线、图层、效果控件和图形编辑器内编辑；所有自动生成内容均使用原生 AE 对象。

详细连接记录见 `config/AE_CODEX_INTEGRATION.md`。
