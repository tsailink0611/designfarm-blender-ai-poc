# ===================================================
# designfarm-blender-ai-poc 実行スクリプト (PowerShell)
# ===================================================

param(
    [string]$Command = "from-json",
    [string]$Input = ""
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = $ProjectRoot

# Blenderのパスが未設定の場合はデフォルトを設定
if (-not $env:BLENDER_PATH) {
    $env:BLENDER_PATH = "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
}

if ($Command -eq "generate") {
    if (-not $Input) {
        $Input = "6m×8mの展示ブース。受付カウンター1つ。壁面パネル3面。モニター2台。右回り導線。白基調で木目アクセント。"
    }
    python "$ProjectRoot\src\app.py" generate $Input --output "$ProjectRoot\output"

} elseif ($Command -eq "from-json") {
    $JsonPath = if ($Input) { $Input } else { "$ProjectRoot\samples\sample_layout_spec.json" }
    python "$ProjectRoot\src\app.py" from-json $JsonPath

} else {
    Write-Host "使用方法:"
    Write-Host "  .\run_local.ps1 generate '6m×8mの展示ブース...' "
    Write-Host "  .\run_local.ps1 from-json 'path\to\layout.json'"
    Write-Host "  .\run_local.ps1              # デフォルト: サンプルJSONで実行"
}
