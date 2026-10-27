# 项目级 FFmpeg

本项目使用 `D:\MY_WORLD\Tools\ffmpeg-2026-08-09-git-6bbc22dc09-full_build` 中的完整 Windows 构建，不修改系统 PATH，也不复制约 600 MB 的可执行文件。

## 固定入口

- `ffmpeg.ps1`：视频、音频编码和合成。
- `ffprobe.ps1`：读取媒体时长、分辨率、编码和音轨信息。
- `verify.ps1`：生成 1 秒测试片并检查 H.264、AAC 和媒体探测链路。
- `config.json`：保存绝对路径、版本、哈希和已验证能力。

示例：

```powershell
& .\tools\ffmpeg\ffmpeg.ps1 -version
& .\tools\ffmpeg\ffprobe.ps1 -v error -show_format -show_streams input.mp4
& .\tools\ffmpeg\verify.ps1
```

已验证 `libx264`、`libx265`、`prores_ks`、VP9、AAC、Opus，以及字幕、文字、叠加、交叉转场和响度标准化滤镜，可满足 Blender、Manim、Remotion 和后期剪辑衔接。

如果以后移动 D 盘工具目录，只需修改 `config.json` 中的三个可执行文件路径并重新运行 `verify.ps1`。
