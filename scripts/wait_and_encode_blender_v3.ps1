$ErrorActionPreference = 'Stop'

$frameDir = 'C:\Users\liuzh\Desktop\1\renders\final_v3_full\frames'
$outputDir = 'C:\Users\liuzh\Desktop\1\resource\fromAI\05_blender_generated'
$outputVideo = Join-Path $outputDir 'blender_v3_full_final_1080p60.mp4'
$remotionVideo = 'C:\Users\liuzh\Desktop\1\remotion_project\public\assets\blender_v3_full_final_1080p60.mp4'
$ffmpeg = 'D:\MY_WORLD\Tools\ffmpeg-2026-08-09-git-6bbc22dc09-full_build\bin\ffmpeg.exe'
$ffprobe = 'D:\MY_WORLD\Tools\ffmpeg-2026-08-09-git-6bbc22dc09-full_build\bin\ffprobe.exe'

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

while ($true) {
    $files = Get-ChildItem -LiteralPath $frameDir -Filter 'frame_*.png' -File
    $valid = @($files | Where-Object Length -gt 0).Count
    $zero = @($files | Where-Object Length -eq 0).Count
    Write-Output ("WAIT valid={0}/5400 zero={1} time={2}" -f $valid, $zero, (Get-Date -Format 'HH:mm:ss'))
    if ($valid -eq 5400 -and $zero -eq 0) {
        break
    }
    Start-Sleep -Seconds 30
}

& $ffmpeg -y -framerate 60 -start_number 0 -i (Join-Path $frameDir 'frame_%04d.png') -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -movflags +faststart -an $outputVideo
if ($LASTEXITCODE -ne 0) {
    throw "FFmpeg encode failed with exit code $LASTEXITCODE"
}

$probe = & $ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate,codec_type -of default=noprint_wrappers=1 $outputVideo
Write-Output $probe
if ($probe -notmatch 'duration=90\.000000') {
    throw 'Encoded duration is not exactly 90 seconds.'
}
if ($probe -match 'codec_type=audio') {
    throw 'Unexpected audio stream in Blender output.'
}

Copy-Item -LiteralPath $outputVideo -Destination $remotionVideo -Force
Write-Output "ENCODE_COMPLETE=$outputVideo"
Write-Output "REMOTION_COPY=$remotionVideo"
