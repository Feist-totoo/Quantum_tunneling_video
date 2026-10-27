# AE 系统修复记录

## 2026-08-26

- After Effects：26.2.1（2026）
- 启动错误：Common Extensibility Platform (CEP) suite 无法加载。
- 已确认 AE 自带的 `PlugPlug.dll`、`csxsmanager.dll`、`CEPHtmlEngine.exe` 与 `CEPManager.aex` 均存在；已检查文件均带有效 Adobe 数字签名。
- 发现系统目录 `C:\Program Files (x86)\Common Files\Adobe\CEP` 是失效的目录联接。
- 原联接目标：`D:\MY_WORLD\Tools\Photoshop2023-v24.5.0.500-x64-zh_CN-Portable\Photoshop2023-v24.5.0.500-x64-zh_CN-Portable\Photoshop\App\Program Files (x86)\Common Files\Adobe\CEP`
- 原目标不存在，因此该联接无法提供任何现存 Adobe 组件。由于系统公共目录需要管理员权限，为避免改动联接本身，实际采取了更保守的修复：只在原目标位置补建空的 `CEP` 目录，使现有联接恢复为可枚举目录。
- 若需回退：删除上面原联接目标处新建的空 `CEP` 目录即可；这会使系统联接重新变为失效状态。
