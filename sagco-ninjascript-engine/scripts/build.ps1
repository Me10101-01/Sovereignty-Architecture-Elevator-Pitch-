# build.ps1 — SAGCO NinjaScript build + export pipeline
# Copies NinjaScript files to NinjaTrader 8 Documents folder and triggers compile.
# Run from sagco-ninjascript-engine/ root.

param(
    [string]$NTDocuments = "$env:USERPROFILE\Documents\NinjaTrader 8",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$IndicatorsOut = Join-Path $NTDocuments "NinjaScript\Indicators"
$StrategiesOut = Join-Path $NTDocuments "NinjaScript\Strategies"
$AddOnsOut     = Join-Path $NTDocuments "NinjaScript\AddOns"

Write-Host "`n========================================"
Write-Host "  SAGCO NinjaScript Build"
Write-Host "  BRICK-019 — v0.1.0"
Write-Host "========================================`n"

function Copy-NinjaFile($src, $dst) {
    if ($DryRun) { Write-Host "  [DRY_RUN] Would copy: $src → $dst"; return }
    New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
    Copy-Item -Path $src -Destination $dst -Force
    Write-Host "  [COMPUTED] Copied: $(Split-Path $src -Leaf)"
}

# Indicators
Get-ChildItem "NinjaTrader\Indicators\*.cs" | ForEach-Object {
    Copy-NinjaFile $_.FullName (Join-Path $IndicatorsOut $_.Name)
}

# Strategies
Get-ChildItem "NinjaTrader\Strategies\*.cs" | ForEach-Object {
    Copy-NinjaFile $_.FullName (Join-Path $StrategiesOut $_.Name)
}

# AddOns
Get-ChildItem "NinjaTrader\AddOns\*.cs" | ForEach-Object {
    Copy-NinjaFile $_.FullName (Join-Path $AddOnsOut $_.Name)
}

Write-Host "`n  Files deployed. Open NinjaTrader 8:"
Write-Host "  Tools → NinjaScript Editor → Compile All"
Write-Host "`n  Then run: sagco ninja debug"
Write-Host "========================================`n"
