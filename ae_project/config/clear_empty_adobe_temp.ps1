$ErrorActionPreference = "Stop"

$targets = @("C:\adobeTemp", "D:\adobeTemp")

$activeInstaller = Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessName -match "Set-up|Setup|HDHelper|CreativeCloudInstaller" }
if ($activeInstaller) {
    throw "Adobe installer process is still running."
}

foreach ($target in $targets) {
    if (-not (Test-Path -LiteralPath $target)) {
        continue
    }

    $resolved = (Resolve-Path -LiteralPath $target).Path
    if ($resolved -ne $target) {
        throw "Refusing unexpected resolved path: $resolved"
    }

    $item = Get-Item -LiteralPath $target -Force
    if (-not $item.PSIsContainer -or $item.LinkType) {
        throw "Refusing non-directory or reparse point: $target"
    }

    $children = @(Get-ChildItem -LiteralPath $target -Force)
    if ($children.Count -ne 0) {
        throw "Refusing non-empty directory: $target"
    }

    $item.Attributes = [IO.FileAttributes]::Directory
    Remove-Item -LiteralPath $target -Force
}

Write-Output "Verified empty Adobe installer temporary directories were removed."
