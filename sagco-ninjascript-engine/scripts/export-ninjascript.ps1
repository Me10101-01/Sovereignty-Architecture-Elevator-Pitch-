# export-ninjascript.ps1 — Export NinjaScript files from NinjaTrader back to repo
# Reverse of build.ps1 — pulls compiled/edited files back from NT Documents.
# Use when editing inside NinjaTrader IDE and want to sync back to repo.

param(
    [string]$NTDocuments = "$env:USERPROFILE\Documents\NinjaTrader 8",
    [switch]$DryRun
)

$files = @(
    @{ Src = "NinjaScript\Indicators\SagcoDeltaRenkoSignal.cs"; Dst = "NinjaTrader\Indicators\SagcoDeltaRenkoSignal.cs" },
    @{ Src = "NinjaScript\Indicators\SagcoVolumePulse.cs";      Dst = "NinjaTrader\Indicators\SagcoVolumePulse.cs" },
    @{ Src = "NinjaScript\Indicators\SagcoBrushCache.cs";       Dst = "NinjaTrader\Indicators\SagcoBrushCache.cs" },
    @{ Src = "NinjaScript\Strategies\SagcoStrategyCore.cs";     Dst = "NinjaTrader\Strategies\SagcoStrategyCore.cs" },
    @{ Src = "NinjaScript\Strategies\SagcoEntryExitEngine.cs";  Dst = "NinjaTrader\Strategies\SagcoEntryExitEngine.cs" },
    @{ Src = "NinjaScript\Strategies\SagcoResumeStateStrategy.cs"; Dst = "NinjaTrader\Strategies\SagcoResumeStateStrategy.cs" },
    @{ Src = "NinjaScript\AddOns\SagcoControlPanel.cs";         Dst = "NinjaTrader\AddOns\SagcoControlPanel.cs" },
    @{ Src = "NinjaScript\AddOns\SagcoCustomUserControl.cs";    Dst = "NinjaTrader\AddOns\SagcoCustomUserControl.cs" }
)

Write-Host "`n  Exporting from NinjaTrader → repo...`n"
foreach ($f in $files) {
    $src = Join-Path $NTDocuments $f.Src
    $dst = $f.Dst
    if (Test-Path $src) {
        if ($DryRun) { Write-Host "  [DRY_RUN] $src → $dst" }
        else { Copy-Item $src $dst -Force; Write-Host "  [COMPUTED] $($f.Dst)" }
    } else {
        Write-Host "  [SKIP] Not found: $src"
    }
}
Write-Host "`n  Done. Run git diff NinjaTrader/ to review changes.`n"
