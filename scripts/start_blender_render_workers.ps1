$ErrorActionPreference = 'Stop'

$blender = 'D:\MY_WORLD\Tools\blender\blender.exe'
$blendFile = 'C:\Users\liuzh\Desktop\1\quantum_tunneling_scientific_v3_fullrender.blend'
$logDir = 'C:\Users\liuzh\Desktop\1\renders\final_v3_full\logs'

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$ranges = @(
    @{ Start = 155; End = 1465; Name = 'worker_1' },
    @{ Start = 1466; End = 2777; Name = 'worker_2' },
    @{ Start = 2778; End = 4088; Name = 'worker_3' },
    @{ Start = 4089; End = 5399; Name = 'worker_4' }
)

foreach ($range in $ranges) {
    $stdout = Join-Path $logDir ($range.Name + '.out.log')
    $stderr = Join-Path $logDir ($range.Name + '.err.log')
    $arguments = @(
        '--background',
        $blendFile,
        '--frame-start',
        [string]$range.Start,
        '--frame-end',
        [string]$range.End,
        '--render-anim'
    )
    $process = Start-Process -FilePath $blender -ArgumentList $arguments -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
    Write-Output ("{0}: PID={1}, frames={2}-{3}" -f $range.Name, $process.Id, $range.Start, $range.End)
}
