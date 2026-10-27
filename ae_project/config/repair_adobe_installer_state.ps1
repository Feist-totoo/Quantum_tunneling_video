$ErrorActionPreference = "Stop"

$stamp = "20260826-2108"
$moves = @(
    @{ Source = "C:\adobeTemp"; Destination = "C:\adobeTemp.codex-failed-$stamp" },
    @{ Source = "D:\adobeTemp"; Destination = "D:\adobeTemp.codex-failed-$stamp" }
)

$activeInstaller = Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessName -match "Set-up|Setup|HDHelper|CreativeCloudInstaller" }
if ($activeInstaller) {
    throw "Adobe installer process is still running."
}

foreach ($move in $moves) {
    $source = $move.Source
    $destination = $move.Destination
    $resolved = (Resolve-Path -LiteralPath $source).Path
    if ($resolved -ne $source) {
        throw "Refusing unexpected resolved path: $resolved"
    }

    $item = Get-Item -LiteralPath $source -Force
    if (-not $item.PSIsContainer -or $item.LinkType) {
        throw "Refusing non-directory or reparse point: $source"
    }
    if (Test-Path -LiteralPath $destination) {
        throw "Backup destination already exists: $destination"
    }

    $item.Attributes = $item.Attributes -band (-bnot [IO.FileAttributes]::Hidden)
    $item.Attributes = $item.Attributes -band (-bnot [IO.FileAttributes]::System)
    $item.Attributes = $item.Attributes -band (-bnot [IO.FileAttributes]::ReadOnly)
    Rename-Item -LiteralPath $source -NewName (Split-Path -Leaf $destination)
}

Write-Output "Adobe installer temporary directories were preserved as timestamped backups."
