$ErrorActionPreference = 'Stop'

$root = 'C:\Users\liuzh\Desktop\1'
$node = (Get-Command node).Source
$ffmpeg = 'D:\MY_WORLD\Tools\ffmpeg-2026-08-09-git-6bbc22dc09-full_build\bin\ffmpeg.exe'
$ffprobe = 'D:\MY_WORLD\Tools\ffmpeg-2026-08-09-git-6bbc22dc09-full_build\bin\ffprobe.exe'
$fusionCapture = Join-Path $root 'tools\html\capture_fusion_html_frames.mjs'
$seekCapture = Join-Path $root 'tools\html\capture_seekable_html_frames.mjs'
$fusionHtml = Join-Path $root 'resource\fromAI\05_html_generated\fusion_quantum_bridge_project_v9.html'
$overlayHtml = Join-Path $root 'resource\fromAI\11_html_generated\probability_overlay_v4\index.html'
$oldFusion = Join-Path $root 'resource\fromAI\10_review_proxies\fusion_quantum_bridge_v8_1080p60.mp4'
$renderRoot = Join-Path $root 'renders\html_resolve_final'
$fusionFrames = Join-Path $renderRoot 'fusion_v9_head_frames'
$formulaFrames = Join-Path $renderRoot 'formula_v4_frames'
$chartFrames = Join-Path $renderRoot 'chart_v4_frames'
$finalDir = Join-Path $root 'resource\final\02_html'
$sourceDir = Join-Path $finalDir 'editable_source'

New-Item -ItemType Directory -Force -Path $renderRoot, $fusionFrames, $formulaFrames, $chartFrames, $finalDir, $sourceDir | Out-Null

function Assert-Frames([string]$directory, [string]$filter, [int]$expected) {
    $count = @(Get-ChildItem -LiteralPath $directory -Filter $filter -File | Where-Object Length -gt 0).Count
    if ($count -ne $expected) { throw "Frame count mismatch in ${directory}: ${count}/${expected}" }
}

Write-Output 'CAPTURE_FUSION_HEAD frames=0-569'
& $node $fusionCapture --html $fusionHtml --out $fusionFrames --fps 60 --duration 49 --from 0 --to 9.5
if ($LASTEXITCODE -ne 0) { throw "Fusion capture failed: $LASTEXITCODE" }
Assert-Frames $fusionFrames 'fusion_*.png' 570

$fusionOut = Join-Path $finalDir 'fusion_quantum_bridge_v9_49s_1080p60_h264.mp4'
$fusionFilter = '[0:v]trim=end_frame=570,setpts=PTS-STARTPTS[a];[1:v]trim=start_frame=570:end_frame=2940,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0,format=yuv420p[outv]'
& $ffmpeg -y -framerate 60 -start_number 0 -i (Join-Path $fusionFrames 'fusion_%05d.png') -i $oldFusion -filter_complex $fusionFilter -map '[outv]' -frames:v 2940 -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -movflags +faststart -an $fusionOut
if ($LASTEXITCODE -ne 0) { throw "Fusion encode failed: $LASTEXITCODE" }

Write-Output 'CAPTURE_FORMULA global=29-34s'
& $node $seekCapture --html $overlayHtml --out $formulaFrames --duration 5 --offset 29 --fps 60 --width 640 --height 1080 --prefix formula
if ($LASTEXITCODE -ne 0) { throw "Formula capture failed: $LASTEXITCODE" }
Assert-Frames $formulaFrames 'formula_*.png' 300

Write-Output 'CAPTURE_CHART global=34-69s'
& $node $seekCapture --html $overlayHtml --out $chartFrames --duration 35 --offset 34 --fps 60 --width 640 --height 1080 --prefix chart
if ($LASTEXITCODE -ne 0) { throw "Chart capture failed: $LASTEXITCODE" }
Assert-Frames $chartFrames 'chart_*.png' 2100

$formulaAlpha = Join-Path $finalDir 'formula_highlight_v4_START_00m29s_5s_640x1080_alpha.mov'
$formulaPreview = Join-Path $finalDir 'formula_highlight_v4_START_00m29s_5s_640x1080_preview.mp4'
$chartAlpha = Join-Path $finalDir 'probability_chart_v4_START_00m34s_35s_640x1080_alpha.mov'
$chartPreview = Join-Path $finalDir 'probability_chart_v4_START_00m34s_35s_640x1080_preview.mp4'

& $ffmpeg -y -framerate 60 -start_number 0 -i (Join-Path $formulaFrames 'formula_%05d.png') -frames:v 300 -c:v prores_ks -profile:v 4 -pix_fmt yuva444p10le -an $formulaAlpha
if ($LASTEXITCODE -ne 0) { throw "Formula alpha encode failed: $LASTEXITCODE" }
& $ffmpeg -y -framerate 60 -start_number 0 -i (Join-Path $formulaFrames 'formula_%05d.png') -frames:v 300 -vf format=yuv420p -c:v libx264 -preset slow -crf 16 -movflags +faststart -an $formulaPreview
if ($LASTEXITCODE -ne 0) { throw "Formula preview encode failed: $LASTEXITCODE" }
& $ffmpeg -y -framerate 60 -start_number 0 -i (Join-Path $chartFrames 'chart_%05d.png') -frames:v 2100 -c:v prores_ks -profile:v 4 -pix_fmt yuva444p10le -an $chartAlpha
if ($LASTEXITCODE -ne 0) { throw "Chart alpha encode failed: $LASTEXITCODE" }
& $ffmpeg -y -framerate 60 -start_number 0 -i (Join-Path $chartFrames 'chart_%05d.png') -frames:v 2100 -vf format=yuv420p -c:v libx264 -preset slow -crf 16 -movflags +faststart -an $chartPreview
if ($LASTEXITCODE -ne 0) { throw "Chart preview encode failed: $LASTEXITCODE" }

Copy-Item -LiteralPath $fusionHtml -Destination $sourceDir -Force
Copy-Item -LiteralPath (Join-Path $root 'resource\fromAI\05_html_generated\fusion_quantum_bridge_project_v9_override.js') -Destination $sourceDir -Force
Copy-Item -LiteralPath $overlayHtml -Destination (Join-Path $sourceDir 'probability_overlay_v4.html') -Force
Copy-Item -LiteralPath (Join-Path $root 'resource\fromAI\11_html_generated\probability_overlay_v4\data.js') -Destination $sourceDir -Force

foreach ($asset in @($fusionOut, $formulaAlpha, $formulaPreview, $chartAlpha, $chartPreview)) {
    & $ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt -of default=noprint_wrappers=1 $asset
    if ($LASTEXITCODE -ne 0) { throw "Probe failed: $asset" }
}
Write-Output "HTML_RESOLVE_COMPLETE=$finalDir"
