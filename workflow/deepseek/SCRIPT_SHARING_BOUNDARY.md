# DeepSeek 文件共享边界

用户于 2026-08-13 明确授权：根目录 `脚本.md` 可以发送给 DeepSeek 官方接口。

当前规则：

- 允许外发：`脚本.md`。
- 默认不外发：`docs/`、`resource/`、`sync/`、Blender 文件、Manim 源码、过程报告和其他项目文档。
- 永不作为任务正文外发：`DEEPSEEK_API_KEY.txt`、任何凭据、环境变量或日志中的令牌。
- 接口仅使用配置中的官方地址 `https://api.deepseek.com` 与 `deepseek-v4-flash`。
- 每次任务包必须在 `inputs` 中显式列出文件；Codex 在调用前复核。
