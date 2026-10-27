$ErrorActionPreference = 'Stop'

$blender = 'D:\MY_WORLD\Tools\blender\blender.exe'
$blendFile = 'C:\Users\liuzh\Desktop\1\quantum_tunneling_scientific_v3_fullrender.blend'
$logDir = 'C:\Users\liuzh\Desktop\1\renders\final_v3_full\logs'

$ranges = @(
    @{ Start = 810; End = 1465; Name = 'worker_5_tail' },
    @{ Start = 2122; End = 2777; Name = 'worker_6_tail' },
    @{ Start = 3434; End = 4088; Name = 'worker_7_tail' },
    @{ Start = 4744; End = 5399; Name = 'worker_8_tail' }
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
