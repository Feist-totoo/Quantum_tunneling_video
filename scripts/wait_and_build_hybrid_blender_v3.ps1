$ErrorActionPreference = 'Stop'

$projectRoot = 'C:\Users\liuzh\Desktop\1'
$frameDir = Join-Path $projectRoot 'renders\final_v3_full\frames'
$logDir = Join-Path $projectRoot 'renders\final_v3_full\logs'
$blender = 'D:\MY_WORLD\Tools\blender\blender.exe'
$blendFile = Join-Path $projectRoot 'quantum_tunneling_scientific_v3_fullrender.blend'
$ffmpeg = 'D:\MY_WORLD\Tools\ffmpeg-2026-08-09-git-6bbc22dc09-full_build\bin\ffmpeg.exe'
$ffprobe = 'D:\MY_WORLD\Tools\ffmpeg-2026-08-09-git-6bbc22dc09-full_build\bin\ffprobe.exe'
$selectedVideo = Join-Path $projectRoot 'remotion_project\public\assets\blender_v3_selected_animatic_1080p60.mp4'
$outputDir = Join-Path $projectRoot 'resource\fromAI\05_blender_generated'
$outputVideo = Join-Path $outputDir 'blender_v3_full_final_1080p60.mp4'
$remotionVideo = Join-Path $projectRoot 'remotion_project\public\assets\blender_v3_full_final_1080p60.mp4'
$finalDir = Join-Path $projectRoot 'resource\final\01_blender'
$resolveVideo = Join-Path $finalDir 'blender_quantum_tunnelling_v3_90s_1080p60_h264.mp4'

New-Item -ItemType Directory -Force -Path $logDir, $outputDir, $finalDir | Out-Null

function Test-RangeComplete([int]$start, [int]$end) {
    for ($frame = $start; $frame -le $end; $frame++) {
        $path = Join-Path $frameDir ('frame_{0:D4}.png' -f $frame)
        if (-not (Test-Path -LiteralPath $path)) { return $false }
        if ((Get-Item -LiteralPath $path).Length -eq 0) { return $false }
    }
    return $true
}

function Get-FirstIncompleteFrame([int]$start, [int]$end) {
    for ($frame = $start; $frame -le $end; $frame++) {
        $path = Join-Path $frameDir ('frame_{0:D4}.png' -f $frame)
        if (-not (Test-Path -LiteralPath $path)) { return $frame }
        if ((Get-Item -LiteralPath $path).Length -eq 0) {
            Remove-Item -LiteralPath $path -Force
            return $frame
        }
    }
    return $null
}

while (-not (Test-RangeComplete 4089 5399)) {
    $count = @(Get-ChildItem -LiteralPath $frameDir -Filter 'frame_*.png' -File | Where-Object Length -gt 0).Count
    Write-Output ("WAIT_TAIL valid_total={0} time={1}" -f $count, (Get-Date -Format 'HH:mm:ss'))
    Start-Sleep -Seconds 30
}

if (-not (Test-RangeComplete 3865 4088)) {
    $gapStart = Get-FirstIncompleteFrame 3865 4088
    Write-Output ("RENDER_GAP frames={0}-4088" -f $gapStart)
    & $blender --background $blendFile --frame-start $gapStart --frame-end 4088 --render-anim
    if ($LASTEXITCODE -ne 0) { throw "Gap render failed: $LASTEXITCODE" }
} else {
    Write-Output 'SKIP_GAP already_complete=3865-4088'
}

$highlightStart = Get-FirstIncompleteFrame 1740 2039
if ($null -ne $highlightStart) {
    Write-Output ("RENDER_HIGHLIGHT frames={0}-2039" -f $highlightStart)
    & $blender --background $blendFile --frame-start $highlightStart --frame-end 2039 --render-anim
    if ($LASTEXITCODE -ne 0) { throw "Highlight render failed: $LASTEXITCODE" }
} else {
    Write-Output 'SKIP_HIGHLIGHT already_complete=1740-2039'
}

if (-not (Test-RangeComplete 1740 2039)) { throw 'Highlight range is incomplete.' }
if (-not (Test-RangeComplete 3865 5399)) { throw 'Tail range is incomplete.' }

$earlyClean = "drawbox=x=140:y=110:w=1280:h=75:color=black:t=fill:enable='between(n\,900\,1739)',drawbox=x=0:y=745:w=1280:h=80:color=black:t=fill:enable='between(n\,500\,1600)'"
$lateClean = "drawbox=x=140:y=110:w=1280:h=75:color=black:t=fill"
$filter = "[0:v]trim=start_frame=0:end_frame=1740,setpts=PTS-STARTPTS,$earlyClean[a];[1:v]trim=end_frame=300,setpts=PTS-STARTPTS[b];[0:v]trim=start_frame=2040:end_frame=3865,setpts=PTS-STARTPTS,$lateClean[c];[2:v]trim=end_frame=1535,setpts=PTS-STARTPTS[d];[a][b][c][d]concat=n=4:v=1:a=0,format=yuv420p[outv]"

& $ffmpeg -y `
    -i $selectedVideo `
    -framerate 60 -start_number 1740 -i (Join-Path $frameDir 'frame_%04d.png') `
    -framerate 60 -start_number 3865 -i (Join-Path $frameDir 'frame_%04d.png') `
    -filter_complex $filter -map '[outv]' -frames:v 5400 `
    -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -movflags +faststart -an $outputVideo
if ($LASTEXITCODE -ne 0) { throw "FFmpeg hybrid encode failed: $LASTEXITCODE" }

$probe = & $ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate,codec_type -of default=noprint_wrappers=1 $outputVideo
Write-Output $probe
$probeText = $probe -join "`n"
if ($probeText -notmatch 'duration=90\.000000') { throw 'Encoded duration is not exactly 90 seconds.' }
if ($probeText -match 'codec_type=audio') { throw 'Unexpected audio stream in Blender output.' }

Copy-Item -LiteralPath $outputVideo -Destination $remotionVideo -Force
Copy-Item -LiteralPath $outputVideo -Destination $resolveVideo -Force
Write-Output "HYBRID_COMPLETE=$outputVideo"
Write-Output "REMOTION_COPY=$remotionVideo"
Write-Output "RESOLVE_COPY=$resolveVideo"
