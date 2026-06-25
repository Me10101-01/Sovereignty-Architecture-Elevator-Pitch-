# seal-release.ps1 — SHA-256 seal all report exports
# Computes SHA-256 for every file in reports/ and writes SHA256SUMS.txt.
# Run after every backtest export before archiving.

param(
    [string]$ReportsDir = "reports",
    [switch]$DryRun
)

$SumsFile = Join-Path $ReportsDir "SHA256SUMS.txt"
$timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")

Write-Host "`n========================================"
Write-Host "  SAGCO Seal Release"
Write-Host "  BRICK-019 SHA-256 Seal"
Write-Host "========================================`n"

$files = Get-ChildItem -Path $ReportsDir -Recurse -File | Where-Object { $_.Name -ne "SHA256SUMS.txt" }

if ($files.Count -eq 0) {
    Write-Host "  (no report files to seal)"
    exit 0
}

$entries = @()
foreach ($f in $files) {
    $hash = (Get-FileHash -Path $f.FullName -Algorithm SHA256).Hash.ToLower()
    $rel  = $f.FullName.Replace((Resolve-Path $ReportsDir).Path + "\", "").Replace("\", "/")
    $entry = "$hash  $rel  # sealed $timestamp"
    $entries += $entry
    Write-Host "  [COMPUTED] $($f.Name)  $($hash.Substring(0,16))..."
}

if (-not $DryRun) {
    $entries | Set-Content -Path $SumsFile -Encoding UTF8
    Write-Host "`n  SHA256SUMS.txt written: $SumsFile"
    Write-Host "  $($entries.Count) files sealed."
} else {
    Write-Host "`n  [DRY_RUN] Would write $($entries.Count) entries to $SumsFile"
}

Write-Host "========================================`n"
