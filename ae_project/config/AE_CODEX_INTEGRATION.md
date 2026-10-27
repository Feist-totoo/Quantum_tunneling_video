# Codex × After Effects 2025 接入说明

## 已完成配置

- Codex 全局 MCP 配置已指向 `D:\MY_WORLD\Tools\After Effects MCP\build\index.js`。
- `AE_AERENDER_PATH` 已切换到 AE 2025 的 `aerender.exe`。
- AE 25.0 用户脚本目录已安装 `mcp-bridge-auto.jsx`。
- AE 首选项“允许脚本写入文件和访问网络”已开启。
- 桥接共享目录为 `C:\Users\liuzh\AppData\Local\ae-mcp-bridge`。
- 项目内保留 `bootstrap_ae_mcp.jsx`，可在面板未启动时从 AE 的“文件 → 脚本 → 运行脚本文件”手动加载桥接。

## 联调结果

2026-08-27 完成以下验证：

1. MCP 健康检查返回 `bridgeResponding: true`。
2. AE 返回版本 `25.0x53`。
3. 桥接版本与服务端均为 `1.13.0-mcp-enhanced`。
4. Codex 成功创建 640×360、60 fps 的临时合成及文字图层。
5. Codex 成功保存临时 AEP，并从 AE 回读 640×360 渲染帧。
6. 临时项目和预览图已移入 Windows 回收站，AE 已恢复为空白项目。

## 故障排查

- 连接超时：确认 AE 正在运行，并打开 `窗口 → mcp-bridge-auto.jsx`。
- 面板不在菜单中：重启 AE，再检查窗口菜单。
- 面板提示文件权限错误：重新确认“编辑 → 首选项 → 脚本和表达式 → 允许脚本写入文件和访问网络”。
- 切换 AE 安装位置后：同步更新 `C:\Users\liuzh\.codex\config.toml` 中的 `AE_AERENDER_PATH`。
