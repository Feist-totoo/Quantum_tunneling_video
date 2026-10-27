# DeepSeek V4-Flash 文本工作流

## 只需填写一处

打开 `DEEPSEEK_API_KEY.txt`，把占位文本替换成你的 DeepSeek API Key。不要加引号或额外空格。该文件已写入根目录 `.gitignore`。

## 工作边界

适合交给 DeepSeek：脚本拆段、字幕表草稿、镜头表草稿、素材清单、来源元数据整理、许可证文本摘要、转场文字建议和检查清单。

不交给 DeepSeek：观看素材、判断画面/声音质量、直接下载、操作 Blender/Manim/剪辑软件、批准科学事实、批准版权或决定最终成片。

## 使用

先检查环境：

```powershell
python workflow/deepseek/deepseek_worker.py doctor
```

填写密钥后测试官方接口：

```powershell
python workflow/deepseek/deepseek_worker.py smoke-test
```

执行任务包：

```powershell
python workflow/deepseek/deepseek_worker.py run --task workflow/deepseek/tasks/example_script_analysis.json
```

每次调用都会在 `runs/<时间戳>/` 保存脱敏后的请求、原始响应、解析后的 JSON、模型名和用量。Codex 只把通过复核的内容转移到正式文档。

## 模型

配置锁定 `deepseek-v4-flash`，思考模式开启，推理强度为 `max`。启动时会先调用官方 `/models` 接口核验账号实际可见的模型，避免使用过期别名。
