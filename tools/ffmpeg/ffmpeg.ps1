$ErrorActionPreference = 'Stop'
$configPath = Join-Path $PSScriptRoot 'config.json'
$config = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
$binary = [string]$config.ffmpeg_path

if (-not (Test-Path -LiteralPath $binary -PathType Leaf)) {
    throw "项目配置的 FFmpeg 不存在：$binary"
}

& $binary @args
exit $LASTEXITCODE
