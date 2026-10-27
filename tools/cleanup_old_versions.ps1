param(
    [switch]$Apply
)

$ErrorActionPreference = 'Stop'
$projectRoot = [System.IO.Path]::GetFullPath('C:\Users\liuzh\Desktop\1')
$rootPrefix = $projectRoot.TrimEnd('\') + '\'
$targets = [System.Collections.Generic.List[string]]::new()

function Add-CleanupTarget {
    param([Parameter(Mandatory)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    $item = Get-Item -LiteralPath $Path -Force
    $resolved = [System.IO.Path]::GetFullPath($item.FullName)
    if (-not $resolved.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing target outside project: $resolved"
    }
    if ($resolved -eq $projectRoot) {
        throw 'Refusing to target the project root.'
    }
    if (-not $targets.Contains($resolved)) {
        $targets.Add($resolved)
    }
}

function Add-ChildrenExcept {
    param(
        [Parameter(Mandatory)][string]$Directory,
        [Parameter(Mandatory)][string[]]$KeepNames
    )

    Get-ChildItem -LiteralPath $Directory -Force | ForEach-Object {
        if ($_.Name -notin $KeepNames) {
            Add-CleanupTarget -Path $_.FullName
        }
    }
}

$oldRootFiles = @(
    'applications_contact.inspect.jpg',
    'applications_contact.png',
    'applications_round2_final.inspect.jpg',
    'applications_sequence_gate_contact.jpg.small.jpg',
    'applications_v4_contact.jpg',
    'applications_v4_tiny.jpg',
    'apps_gate_tiny.jpg',
    'fusion_contact_small.inspect.jpg',
    'fusion_contact_small.jpg',
    'fusion_contact.png',
    'fusion_round2_final.inspect.jpg',
    'qt.blend',
    'quantum_tunneling_review.blend1',
    'quantum_tunneling_scientific_v2.blend',
    'quantum_tunneling_scientific_v2.blend1',
    'quantum_tunneling_scientific_v3.blend1',
    'unc_gate_tiny.jpg',
    'uncertainty_1d_gate_contact.jpg.small.jpg',
    'uncertainty_contact.inspect.jpg',
    'uncertainty_contact.png',
    'uncertainty_round2_final.inspect.jpg'
)
$oldRootFiles | ForEach-Object { Add-CleanupTarget -Path (Join-Path $projectRoot $_) }

@('source', 'media', '@', '__pycache__') | ForEach-Object {
    Add-CleanupTarget -Path (Join-Path $projectRoot $_)
}

Add-ChildrenExcept -Directory (Join-Path $projectRoot 'renders') -KeepNames @('review_v3_final')

Add-ChildrenExcept -Directory (Join-Path $projectRoot 'docs') -KeepNames @(
    'ACCEPTANCE_V3.md',
    'build_report_v3.json',
    'camera_motion_validation_v3.json',
    'CLEANUP_2026-08-19.md',
    'FIVE_STAGE_WORKFLOW.md',
    'PROGRESS.md',
    'PROJECT_PROCESS_V3.md',
    'review_validation_v3.json',
    'STAGE1_REVIEW.md',
    'STAGE2_TOOLING_REVIEW.md',
    'STAGE3_DELIVERY_2026-08-13.md',
    'v3_contact_sheet_report.json'
)

Add-ChildrenExcept -Directory (Join-Path $projectRoot 'scripts') -KeepNames @(
    'add_v3_parameter_arrows.py',
    'build_probability_html_data.ps1',
    'build_quantum_tunneling_v3.py',
    'extract_reference_contact_sheet.py',
    'manim_sync_adapter_v3.py',
    'render_quantum_tunneling_v3_keyframes.py',
    'validate_camera_motion_v3.py',
    'validate_quantum_tunneling_v3.py'
)

Add-ChildrenExcept -Directory (Join-Path $projectRoot 'tools\manim') -KeepNames @(
    'README.md',
    'render_project_assets_v3.ps1'
)
Add-ChildrenExcept -Directory (Join-Path $projectRoot 'tools\html') -KeepNames @(
    'capture_fusion_html_frames.mjs'
)
Add-CleanupTarget -Path (Join-Path $projectRoot 'tools\video')

$fromAI = Join-Path $projectRoot 'resource\fromAI'
Add-ChildrenExcept -Directory $fromAI -KeepNames @(
    '01_science_references',
    '02_public_visuals',
    '03_open_projects',
    '04_manim_generated',
    '05_blender_generated',
    '05_html_generated',
    '06_voiceover',
    '07_music_sfx',
    '08_transitions_overlays',
    '09_licenses',
    '10_review_proxies',
    '11_html_generated',
    'CURRENT_ASSET_INDEX.md',
    'MASTER_ASSET_TIMELINE_DRAFT.md',
    'README.md',
    'STAGE3_FINAL_ASSET_INDEX.md',
    'visual-style-3b1b.md'
)

$manim = Join-Path $fromAI '04_manim_generated'
Add-ChildrenExcept -Directory $manim -KeepNames @(
    'APPLICATIONS_INTERMEDIATE_LAYOUT_V7.md',
    'README.md',
    'scenes.md',
    'STAGE3_CORE_SCENES.md',
    'stage3_core_scenes.py',
    'tunneling_applications_intermediate_layout_v7.py',
    'UNCERTAINTY_REFERENCE_REBUILD.md',
    'uncertainty_reference_rebuild_v3.py'
)

$fusion = Join-Path $fromAI '05_html_generated'
Add-ChildrenExcept -Directory $fusion -KeepNames @(
    'FUSION_V4.md',
    'fusion_quantum_bridge_project_v4.html',
    'fusion_quantum_bridge_project_v4_override.js',
    'README.md'
)

$html = Join-Path $fromAI '11_html_generated'
Add-ChildrenExcept -Directory $html -KeepNames @('probability_overlay_v3')

$review = Join-Path $fromAI '10_review_proxies'
Add-ChildrenExcept -Directory $review -KeepNames @(
    'blender_bridge_current_480p30.mp4',
    'fusion_quantum_bridge_v4_1080p30.mp4',
    'nasa_sdo_sun_6s_review.mp4',
    'probability_overlay_v3_height.png',
    'probability_overlay_v3_html_640x1080p60.mp4',
    'probability_overlay_v3_live.png',
    'probability_overlay_v3_width.png',
    'qa_apps_intermediate_v7',
    'qa_fusion_v4',
    'qa_uncertainty_v3',
    'README.md',
    'REVIEW_ROUND7_INTERMEDIATE_LAYOUT_CORRECTION.md',
    'tunnelling_applications_intermediate_layout_v7_1080p60.mp4',
    'uncertainty_1d_stochastic_v3_1080p60.mp4',
    'wavefunction_language_current_480p30.mp4'
)

Add-ChildrenExcept -Directory (Join-Path $review 'qa_apps_intermediate_v7') -KeepNames @(
    'contact_sheet.jpg',
    'report.json',
    'report.md'
)
Add-ChildrenExcept -Directory (Join-Path $review 'qa_fusion_v4') -KeepNames @(
    'contact_sheet.png',
    'report.md'
)
Add-ChildrenExcept -Directory (Join-Path $review 'qa_uncertainty_v3') -KeepNames @(
    'contact_sheet.jpg',
    'report.json'
)

$targets = $targets | Sort-Object -Unique
$fileCount = 0
$directoryCount = 0
$totalBytes = 0L
foreach ($target in $targets) {
    if (-not (Test-Path -LiteralPath $target)) {
        continue
    }
    $item = Get-Item -LiteralPath $target -Force
    if ($item.PSIsContainer) {
        $directoryCount++
        $children = Get-ChildItem -LiteralPath $target -File -Recurse -Force -ErrorAction SilentlyContinue
        $fileCount += $children.Count
        $totalBytes += [long](($children | Measure-Object Length -Sum).Sum)
    } else {
        $fileCount++
        $totalBytes += $item.Length
    }
}

$summary = [pscustomobject]@{
    Mode = if ($Apply) { 'RECYCLE' } else { 'DRY-RUN' }
    TargetEntries = $targets.Count
    Files = $fileCount
    Directories = $directoryCount
    SizeMB = [math]::Round($totalBytes / 1MB, 2)
}
$summary | Format-List
$targets | ForEach-Object { "TARGET`t$_" }

if (-not $Apply) {
    return
}

Add-Type -AssemblyName Microsoft.VisualBasic
foreach ($target in $targets) {
    if (-not (Test-Path -LiteralPath $target)) {
        continue
    }
    $item = Get-Item -LiteralPath $target -Force
    if ($item.PSIsContainer) {
        [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory(
            $target,
            [Microsoft.VisualBasic.FileIO.UIOption]::OnlyErrorDialogs,
            [Microsoft.VisualBasic.FileIO.RecycleOption]::SendToRecycleBin
        )
    } else {
        [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile(
            $target,
            [Microsoft.VisualBasic.FileIO.UIOption]::OnlyErrorDialogs,
            [Microsoft.VisualBasic.FileIO.RecycleOption]::SendToRecycleBin
        )
    }
}

'Cleanup complete. All listed targets were sent to the Windows Recycle Bin.'
