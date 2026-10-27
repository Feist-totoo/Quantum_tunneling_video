$ErrorActionPreference = 'Stop'
$configPath = Join-Path $PSScriptRoot 'config.json'
$config = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
$ffmpeg = [string]$config.ffmpeg_path
$ffprobe = [string]$config.ffprobe_path

foreach ($binary in @($ffmpeg, $ffprobe)) {
    if (-not (Test-Path -LiteralPath $binary -PathType Leaf)) {
        throw "缺少已配置的工具：$binary"
    }
}

$selftestDir = Join-Path $PSScriptRoot 'selftest'
New-Item -ItemType Directory -Path $selftestDir -Force | Out-Null
$output = Join-Path $selftestDir 'ffmpeg_selftest.mp4'

& $ffmpeg -hide_banner -loglevel error -y `
    -f lavfi -i 'testsrc2=size=320x180:rate=30:duration=1' `
    -f lavfi -i 'sine=frequency=440:sample_rate=48000:duration=1' `
    -c:v libx264 -pix_fmt yuv420p -c:a aac -movflags +faststart $output

if ($LASTEXITCODE -ne 0) {
    throw "FFmpeg 编码自检失败，退出码：$LASTEXITCODE"
}

$probeJson = & $ffprobe -v error -show_entries 'format=duration,size:stream=codec_type,codec_name,width,height,sample_rate' -of json $output
if ($LASTEXITCODE -ne 0) {
    throw "FFprobe 自检失败，退出码：$LASTEXITCODE"
}

$probe = $probeJson | ConvertFrom-Json
[pscustomobject]@{
    status = 'PASS'
    output = $output
    duration_seconds = [math]::Round([double]$probe.format.duration, 3)
    size_bytes = [int64]$probe.format.size
    streams = $probe.streams
} | ConvertTo-Json -Depth 5
