$root = Split-Path -Parent $PSScriptRoot
$csvPath = Join-Path $root "sync\probability_frames_v3.csv"
$outDir = Join-Path $root "resource\fromAI\11_html_generated\probability_overlay_v3"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$rows = Import-Csv $csvPath
$compact = foreach ($r in $rows) {
    [ordered]@{
        f  = [int]$r.manim_frame
        s  = $r.segment
        b  = [double]$r.p_before
        a  = [double]$r.p_after
        lb = [double]$r.log10_before
        la = [double]$r.log10_after
        w  = [double]$r.width_factor
        h  = [double]$r.height_factor
        g  = $r.comparison_group
        cb = [double]$r.comparison_before
        ca = [double]$r.comparison_after
    }
}
$json = $compact | ConvertTo-Json -Compress -Depth 3
[System.IO.File]::WriteAllText((Join-Path $outDir "data.js"), "window.PROBABILITY_DATA=$json;", [System.Text.UTF8Encoding]::new($false))
