# DaVinci Resolve MCP 配置说明

> 配置日期：2026-08-25  
> 项目根目录：`C:\Users\liuzh\Desktop\1`

## 当前状态

- DaVinci Resolve：免费版 `20.3.0.10`
- Resolve 程序：`D:\MY_WORLD\Tools\DaVinci Resolve\Resolve.exe`
- Resolve MCP：`D:\MY_WORLD\Tools\DaVinci Resolve MCP`
- MCP 版本：`2.103.1`
- Python：官方 CPython `3.12.10`
- FFmpeg：已加入用户 `PATH`，供素材分析、抽帧与交付检查使用
- Codex 配置：`C:\Users\liuzh\.codex\config.toml`
- 连接测试：已通过，能够读取正在运行的 Resolve 版本和当前项目

Resolve 21.0.4 的升级提示已跳过，本次没有升级软件，避免在项目制作中途引入版本变化。

## 每次使用

1. 打开 DaVinci Resolve，并打开一个已经保存的项目。
2. 选择菜单：`工作区 → 脚本 → resolve_bridge`。
3. 保持 Resolve 运行，再让 Codex 执行剪辑操作。
4. 免费版每次重新启动 Resolve 后都需要重新运行一次 `resolve_bridge`。

若 Codex 中暂时没有出现 Resolve 工具，重新打开 Codex 任务或重启 Codex，使其重新读取 MCP 配置。

## 安全边界

- 桥接仅监听本机地址 `127.0.0.1:49632`，没有向局域网或公网开放。
- 桥接使用随机认证令牌；令牌文件位于 `C:\Users\liuzh\.config\davinci-resolve-mcp\bridge.json`，不要分享或提交到公开仓库。
- 允许读取的媒体范围限定在 `C:\Users\liuzh`，涵盖本项目素材。
- 允许文件输出到 `C:\Users\liuzh\Movies` 和本项目根目录。
- MCP 不应修改、转码或替换源素材，除非用户明确要求该项操作。
- 批量剪辑前应复制时间线；最终渲染必须由用户确认后才能启动。

## 分工建议

- DaVinci Resolve：主时间线、剪辑、转场、Fusion、调色、Fairlight 和人工精修。
- Resolve MCP：让 Codex 进行素材整理、精确对齐、重复剪辑、标记、版本化时间线和渲染队列准备。
- FFmpeg：媒体参数检查、代理转换、抽帧和最终技术验收。
- Blender、Manim、HTML：生成动画源素材，不承担最终剪辑时间线。

## 故障排查

- **连接被拒绝**：确认 Resolve 已打开，并重新运行 `工作区 → 脚本 → resolve_bridge`。
- **脚本菜单为空**：先打开并保存一个项目；项目管理器页面通常不会显示完整脚本菜单。
- **Codex 没有 Resolve 工具**：重新加载 Codex 任务；MCP 配置通常只在任务启动时读取。
- **输出路径被拒绝**：把输出设到项目目录或 `C:\Users\liuzh\Movies`。
- **升级 Studio 版后**：可在 Resolve 偏好设置中把外部脚本设为 `Local`，届时不再需要免费版应用内桥接。
