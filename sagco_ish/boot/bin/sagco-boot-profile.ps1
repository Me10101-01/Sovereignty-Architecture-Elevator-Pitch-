# SAGCO Boot Profile Hook — Brick 071
# Add this to your PowerShell $PROFILE to make sagco-boot fire on every login.
#
# To install:
#   notepad $PROFILE
#   Paste the block below, save, restart PowerShell.
#
# Or run once from an elevated prompt:
#   Add-Content $PROFILE (Get-Content C:\sagco\sagco_ish\boot\bin\sagco-boot-profile.ps1)
#
# What this does:
#   Windows boots → PowerShell opens → Import-Module SAGCO runs →
#   sagco-boot fires → SAGCO claims PRIMARY governance →
#   Windows is now Department=INFRASTRUCTURE
#
# From this point forward: Windows is the plumbing. SAGCO is the interface.

# ── SAGCO Boot Hook ───────────────────────────────────────────────────────────

$SAGCO_ROOT = "C:\sagco"   # adjust if your repo lives elsewhere
$SAGCO_BOOT = "$SAGCO_ROOT\sagco_ish\boot\bin\sagco-boot"
$SAGCO_CASE = "C1602_CASE_001"

# Detect which shell is available (WSL preferred, Git Bash fallback)
function Invoke-SAGCOBoot {
    if (Get-Command wsl.exe -ErrorAction SilentlyContinue) {
        $wslPath = wsl.exe wslpath -u $SAGCO_BOOT.Replace('\', '/')
        $wslCase = $SAGCO_CASE
        wsl.exe sh $wslPath $wslCase
    } elseif (Get-Command bash.exe -ErrorAction SilentlyContinue) {
        $bashPath = $SAGCO_BOOT.Replace('\', '/')
        bash.exe -c "sh '$bashPath' '$SAGCO_CASE'"
    } else {
        Write-Host "SAGCO: no sh runtime found (WSL or Git Bash required)" -ForegroundColor Yellow
    }
}

# Run boot sequence
if (Test-Path $SAGCO_BOOT) {
    Invoke-SAGCOBoot
} else {
    Write-Host "SAGCO: boot script not found at $SAGCO_BOOT" -ForegroundColor Yellow
    Write-Host "       Clone the repo to C:\sagco or update SAGCO_ROOT above" -ForegroundColor Yellow
}

# ── End SAGCO Boot Hook ───────────────────────────────────────────────────────
