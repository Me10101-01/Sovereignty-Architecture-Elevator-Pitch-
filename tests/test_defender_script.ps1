# Test script for defender-executive-override.ps1
# This validates the script structure and syntax

$ErrorActionPreference = "Stop"

Write-Host "Testing defender-executive-override.ps1..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Script file exists
Write-Host "Test 1: Checking if script file exists..." -ForegroundColor Yellow
$scriptPath = Join-Path $PSScriptRoot ".." "defender-executive-override.ps1"
if (Test-Path $scriptPath) {
    Write-Host "  ✓ Script file exists" -ForegroundColor Green
} else {
    Write-Host "  ✗ Script file not found" -ForegroundColor Red
    exit 1
}

# Test 2: Script has valid PowerShell syntax
Write-Host "Test 2: Validating PowerShell syntax..." -ForegroundColor Yellow
try {
    $tokens = $null
    $errors = $null
    $ast = [System.Management.Automation.Language.Parser]::ParseFile(
        $scriptPath,
        [ref]$tokens,
        [ref]$errors
    )
    
    if ($errors.Count -eq 0) {
        Write-Host "  ✓ No syntax errors found" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Syntax errors found:" -ForegroundColor Red
        foreach ($error in $errors) {
            Write-Host "    - $($error.Message)" -ForegroundColor Red
        }
        exit 1
    }
} catch {
    Write-Host "  ✗ Failed to parse script: $_" -ForegroundColor Red
    exit 1
}

# Test 3: Script contains required functions
Write-Host "Test 3: Checking for required functions..." -ForegroundColor Yellow
$scriptContent = Get-Content $scriptPath -Raw
$requiredFunctions = @(
    "Test-Administrator",
    "Show-Banner",
    "Invoke-DefenderOverride"
)

foreach ($func in $requiredFunctions) {
    if ($scriptContent -match "function\s+$func") {
        Write-Host "  ✓ Function '$func' found" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Function '$func' not found" -ForegroundColor Red
        exit 1
    }
}

# Test 4: Script has proper parameter definitions
Write-Host "Test 4: Checking parameter definitions..." -ForegroundColor Yellow
$expectedParams = @("ProjectPath", "SkipRealtimeMonitoring", "DryRun")
$paramBlock = $ast.ParamBlock

if ($null -ne $paramBlock) {
    Write-Host "  ✓ Parameter block exists" -ForegroundColor Green
    
    $paramNames = $paramBlock.Parameters | ForEach-Object { $_.Name.VariablePath.UserPath }
    
    foreach ($param in $expectedParams) {
        if ($paramNames -contains $param) {
            Write-Host "  ✓ Parameter '$param' defined" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Parameter '$param' not found" -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "  ✗ No parameter block found" -ForegroundColor Red
    exit 1
}

# Test 5: Script has help documentation
Write-Host "Test 5: Checking help documentation..." -ForegroundColor Yellow
$helpSections = @(".SYNOPSIS", ".DESCRIPTION", ".NOTES", ".EXAMPLE")

foreach ($section in $helpSections) {
    if ($scriptContent -match [regex]::Escape($section)) {
        Write-Host "  ✓ Help section '$section' found" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Help section '$section' not found" -ForegroundColor Red
        exit 1
    }
}

# Test 6: Script contains security warnings
Write-Host "Test 6: Checking for security warnings..." -ForegroundColor Yellow
$securityKeywords = @("SECURITY WARNING", "administrator", "DryRun")

foreach ($keyword in $securityKeywords) {
    if ($scriptContent -match [regex]::Escape($keyword)) {
        Write-Host "  ✓ Security keyword '$keyword' found" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Security keyword '$keyword' not found" -ForegroundColor Red
        exit 1
    }
}

# Test 7: Script has error handling
Write-Host "Test 7: Checking error handling..." -ForegroundColor Yellow
if ($scriptContent -match "try\s*\{" -and $scriptContent -match "catch\s*\{") {
    Write-Host "  ✓ Try-catch blocks found" -ForegroundColor Green
} else {
    Write-Host "  ✗ No try-catch blocks found" -ForegroundColor Red
    exit 1
}

# Test 8: Script validates administrator privileges
Write-Host "Test 8: Checking administrator validation..." -ForegroundColor Yellow
if ($scriptContent -match "Test-Administrator" -and $scriptContent -match "administrator privileges") {
    Write-Host "  ✓ Administrator validation present" -ForegroundColor Green
} else {
    Write-Host "  ✗ Administrator validation missing" -ForegroundColor Red
    exit 1
}

# All tests passed
Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "All tests passed! ✓" -ForegroundColor Green
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

exit 0
