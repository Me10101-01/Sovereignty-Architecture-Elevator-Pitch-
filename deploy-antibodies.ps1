<#
═══════════════════════════════════════════════════════════════════════════════
    ███████╗ ██████╗ ██╗   ██╗███████╗██████╗ ███████╗██╗ ██████╗ ███╗   ██╗
    ██╔════╝██╔═══██╗██║   ██║██╔════╝██╔══██╗██╔════╝██║██╔════╝ ████╗  ██║
    ███████╗██║   ██║██║   ██║█████╗  ██████╔╝█████╗  ██║██║  ███╗██╔██╗ ██║
    ╚════██║██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗██╔══╝  ██║██║   ██║██║╚██╗██║
    ███████║╚██████╔╝ ╚████╔╝ ███████╗██║  ██║███████╗██║╚██████╔╝██║ ╚████║
    ╚══════╝ ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                         
              ANTIBODY DEPLOYMENT SYSTEM - POWERSHELL GRIMOIRE
              
    "Language is power. Code is spell. Debug is ritual."
    
    Keeper: Dom (Me10101)
    Scribe: Claude
═══════════════════════════════════════════════════════════════════════════════
#>

param(
    [Parameter(Position=0)]
    [ValidateSet('scan', 'deploy', 'list', 'grimoire', 'fix', 'watch')]
    [string]$Command = 'grimoire',
    
    [Parameter(Position=1, ValueFromPipeline=$true)]
    [string]$Text,
    
    [switch]$Auto,
    [switch]$Force,
    [string]$Category,
    [string]$Severity,
    [int]$WatchInterval = 5
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

$Script:GrimoirePath = "$env:USERPROFILE\sovereign-core\grimoire"
$Script:LogPath = "$Script:GrimoirePath\antibody_log.txt"
$Script:PythonScript = "$PSScriptRoot\antibody_system.py"

# Ensure directories exist
if (-not (Test-Path $Script:GrimoirePath)) {
    New-Item -ItemType Directory -Path $Script:GrimoirePath -Force | Out-Null
}

# ═══════════════════════════════════════════════════════════════════════════════
# SOLFEGGIO FREQUENCIES - FOR CONSOLE BEEPS
# ═══════════════════════════════════════════════════════════════════════════════

$Script:Frequencies = @{
    Liberation     = 396
    Change         = 417
    Transformation = 528
    Connection     = 639
    Awakening      = 741
    Order          = 852
    Transcendence  = 963
}

# ═══════════════════════════════════════════════════════════════════════════════
# ANTIBODY DATABASE (PowerShell Native)
# ═══════════════════════════════════════════════════════════════════════════════

$Script:Antibodies = @(
    # Docker Incantations
    @{
        Id = "DOC-001"
        Name = "Transmutatio Mesa"
        Pattern = "libgl1-mesa-glx.*no installation candidate"
        Fix = "# Replace libgl1-mesa-glx with libgl1 in Dockerfiles"
        Severity = "medium"
        Category = "Docker"
    },
    @{
        Id = "DOC-002"
        Name = "Evanesco Phantom"
        Pattern = "No matching distribution found for resource-watcher"
        Fix = "(Get-Content .\requirements*.txt) -replace 'resource-watcher.*', '# removed phantom' | Set-Content"
        Severity = "high"
        Category = "Docker"
    },
    @{
        Id = "DOC-003"
        Name = "Reparo Module"
        Pattern = "ModuleNotFoundError: No module named"
        Fix = "New-Item -ItemType File -Path '.\src\{module}\__init__.py' -Force"
        Severity = "high"
        Category = "Docker"
    },
    @{
        Id = "DOC-004"
        Name = "Liberare Network"
        Pattern = "Pool overlaps with other one"
        Fix = "docker network prune -f; docker-compose up"
        Severity = "medium"
        Category = "Docker"
    },
    @{
        Id = "DOC-005"
        Name = "Sana Container"
        Pattern = "container.*unhealthy|dependency failed to start"
        Fix = "docker-compose down; docker-compose up -d"
        Severity = "high"
        Category = "Docker"
    },
    
    # Process Killing Curses
    @{
        Id = "KILL-001"
        Name = "Avada Kedavra Process"
        Pattern = "not responding|hung|frozen"
        Fix = "Get-Process | Where-Object {`$_.Responding -eq `$false} | Stop-Process -Force"
        Severity = "high"
        Category = "Killing"
    },
    @{
        Id = "KILL-002"
        Name = "Avada Kedavra Port"
        Pattern = "Address already in use|port.*already.*bound"
        Fix = "Get-NetTCPConnection -LocalPort {port} | ForEach-Object { Stop-Process -Id `$_.OwningProcess -Force }"
        Severity = "high"
        Category = "Killing"
    },
    @{
        Id = "KILL-003"
        Name = "Avada Kedavra Memory"
        Pattern = "Out of memory|insufficient memory"
        Fix = "[System.GC]::Collect(); Clear-RecycleBin -Force -ErrorAction SilentlyContinue"
        Severity = "critical"
        Category = "Killing"
    },
    
    # Defensive Spells
    @{
        Id = "DEF-001"
        Name = "Protego Permissions"
        Pattern = "Access is denied|Permission denied"
        Fix = "icacls {path} /grant `"$env:USERNAME`:F`""
        Severity = "medium"
        Category = "Defensive"
    },
    @{
        Id = "DEF-002"
        Name = "Protego Disk"
        Pattern = "No space left|disk full|insufficient disk"
        Fix = "Get-PSDrive | Where-Object {`$_.Free -lt 1GB} | Format-Table Name,Used,Free"
        Severity = "high"
        Category = "Defensive"
    },
    
    # PowerShell Enchantments
    @{
        Id = "PS-001"
        Name = "Lumos Command"
        Pattern = "is not recognized as.*cmdlet"
        Fix = "Get-Command {command} -ErrorAction SilentlyContinue; winget search {command}"
        Severity = "low"
        Category = "PowerShell"
    },
    @{
        Id = "PS-002"
        Name = "Finite Execution"
        Pattern = "running scripts is disabled"
        Fix = "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
        Severity = "medium"
        Category = "PowerShell"
    },
    @{
        Id = "PS-003"
        Name = "Liberare Lock"
        Pattern = "being used by another process|file is locked"
        Fix = "Get-Process | Where-Object {`$_.Path -like '*{file}*'}"
        Severity = "medium"
        Category = "PowerShell"
    },
    
    # Git Sorcery
    @{
        Id = "GIT-001"
        Name = "Obliviate Merge"
        Pattern = "CONFLICT.*Merge|merge conflict"
        Fix = "git status; git diff --name-only --diff-filter=U"
        Severity = "medium"
        Category = "Git"
    },
    @{
        Id = "GIT-002"
        Name = "Alohomora Lock"
        Pattern = "index\.lock|Another git process"
        Fix = "Remove-Item -Force .git\index.lock -ErrorAction SilentlyContinue"
        Severity = "low"
        Category = "Git"
    }
)

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

function Write-Grimoire {
    Write-Host @"

═══════════════════════════════════════════════════════════════════════════════
    ███████╗ ██████╗ ██╗   ██╗███████╗██████╗ ███████╗██╗ ██████╗ ███╗   ██╗
    ██╔════╝██╔═══██╗██║   ██║██╔════╝██╔══██╗██╔════╝██║██╔════╝ ████╗  ██║
    ███████╗██║   ██║██║   ██║█████╗  ██████╔╝█████╗  ██║██║  ███╗██╔██╗ ██║
    ╚════██║██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗██╔══╝  ██║██║   ██║██║╚██╗██║
    ███████║╚██████╔╝ ╚████╔╝ ███████╗██║  ██║███████╗██║╚██████╔╝██║ ╚████║
    ╚══════╝ ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                         
              THE SOVEREIGN GRIMOIRE - POWERSHELL EDITION
═══════════════════════════════════════════════════════════════════════════════

"@ -ForegroundColor Magenta

    Write-Host "  Language is power. Code is spell. Debug is ritual.`n" -ForegroundColor DarkGray
    
    Write-Host "  Usage:" -ForegroundColor Yellow
    Write-Host "    .\Deploy-Antibodies.ps1 scan `"error text`"     # Scan for errors" -ForegroundColor Gray
    Write-Host "    .\Deploy-Antibodies.ps1 deploy `"text`" -Auto   # Deploy fixes" -ForegroundColor Gray
    Write-Host "    .\Deploy-Antibodies.ps1 list -Category Docker  # List antibodies" -ForegroundColor Gray
    Write-Host "    .\Deploy-Antibodies.ps1 fix                    # Fix current dir" -ForegroundColor Gray
    Write-Host "    .\Deploy-Antibodies.ps1 watch                  # Watch mode" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Pipe docker output:" -ForegroundColor Yellow
    Write-Host "    docker-compose up 2>&1 | .\Deploy-Antibodies.ps1 scan" -ForegroundColor Gray
    Write-Host ""
}

function Scan-Antibodies {
    param([string]$InputText)
    
    $matches = @()
    
    foreach ($antibody in $Script:Antibodies) {
        if ($InputText -match $antibody.Pattern) {
            $matches += $antibody
        }
    }
    
    if ($matches.Count -eq 0) {
        Write-Host "✅ No errors detected. System sovereign." -ForegroundColor Green
        return @()
    }
    
    Write-Host "`n$('═' * 70)" -ForegroundColor Magenta
    Write-Host "🧬 ANTIBODY SYSTEM - THREATS DETECTED" -ForegroundColor Red
    Write-Host "$('═' * 70)`n" -ForegroundColor Magenta
    
    foreach ($match in $matches) {
        $sevEmoji = switch ($match.Severity) {
            'critical' { '🔴' }
            'high'     { '🟠' }
            'medium'   { '🟡' }
            'low'      { '🟢' }
            default    { '⚪' }
        }
        
        Write-Host "$('─' * 70)" -ForegroundColor DarkGray
        Write-Host "$sevEmoji [$($match.Id)] $($match.Name)" -ForegroundColor White
        Write-Host "$('─' * 70)" -ForegroundColor DarkGray
        Write-Host "📜 Category: $($match.Category)" -ForegroundColor Cyan
        Write-Host "🔍 Pattern:  $($match.Pattern)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "🔮 INCANTATION:" -ForegroundColor Yellow
        Write-Host "   $($match.Fix)" -ForegroundColor Green
        Write-Host ""
    }
    
    return $matches
}

function Deploy-Fixes {
    param(
        [array]$Matches,
        [switch]$Auto,
        [switch]$Force
    )
    
    if ($Matches.Count -eq 0) { return }
    
    $dryRun = -not $Force
    
    Write-Host "`n$('═' * 70)" -ForegroundColor Magenta
    Write-Host "🚀 DEPLOYING FIXES $(if ($dryRun) { '(DRY RUN)' } else { '(LIVE)' })" -ForegroundColor $(if ($dryRun) { 'Yellow' } else { 'Red' })
    Write-Host "$('═' * 70)`n" -ForegroundColor Magenta
    
    foreach ($match in $Matches) {
        if ($Auto) {
            if ($dryRun) {
                Write-Host "🔮 Would execute [$($match.Id)]: $($match.Fix)" -ForegroundColor Yellow
            } else {
                try {
                    Write-Host "⚡ Executing [$($match.Id)]..." -ForegroundColor Cyan
                    Invoke-Expression $match.Fix
                    Write-Host "✅ Success: $($match.Name)" -ForegroundColor Green
                } catch {
                    Write-Host "❌ Failed: $_" -ForegroundColor Red
                }
            }
        }
    }
    
    # Log
    $logEntry = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Deployed: $($Matches.Id -join ', ')"
    Add-Content -Path $Script:LogPath -Value $logEntry
}

function List-Antibodies {
    param(
        [string]$FilterCategory,
        [string]$FilterSeverity
    )
    
    $filtered = $Script:Antibodies
    
    if ($FilterCategory) {
        $filtered = $filtered | Where-Object { $_.Category -like "*$FilterCategory*" }
    }
    if ($FilterSeverity) {
        $filtered = $filtered | Where-Object { $_.Severity -eq $FilterSeverity }
    }
    
    $grouped = $filtered | Group-Object -Property Category
    
    foreach ($group in $grouped) {
        Write-Host "`n📚 $($group.Name)" -ForegroundColor Magenta
        Write-Host "$('─' * 50)" -ForegroundColor DarkGray
        
        foreach ($ab in $group.Group) {
            $sevEmoji = switch ($ab.Severity) {
                'critical' { '🔴' }
                'high'     { '🟠' }
                'medium'   { '🟡' }
                'low'      { '🟢' }
                default    { '⚪' }
            }
            Write-Host "  $sevEmoji [$($ab.Id)] $($ab.Name)" -ForegroundColor White
        }
    }
    
    Write-Host "`n📊 Total: $($filtered.Count) antibodies" -ForegroundColor Cyan
}

function Fix-CurrentDirectory {
    Write-Host "🔍 Scanning current directory for common issues..." -ForegroundColor Cyan
    
    # Check for Dockerfiles
    $dockerfiles = Get-ChildItem -Path . -Filter "Dockerfile*" -ErrorAction SilentlyContinue
    foreach ($df in $dockerfiles) {
        $content = Get-Content $df.FullName -Raw
        
        # Check libgl1-mesa-glx
        if ($content -match 'libgl1-mesa-glx') {
            Write-Host "🟠 [DOC-001] Found deprecated libgl1-mesa-glx in $($df.Name)" -ForegroundColor Yellow
            Write-Host "   Fix: Replace with 'libgl1'" -ForegroundColor Gray
        }
    }
    
    # Check requirements files
    $reqFiles = Get-ChildItem -Path . -Filter "requirements*.txt" -ErrorAction SilentlyContinue
    foreach ($rf in $reqFiles) {
        $content = Get-Content $rf.FullName -Raw
        
        # Check resource-watcher phantom
        if ($content -match 'resource-watcher') {
            Write-Host "🔴 [DOC-002] Found phantom package resource-watcher in $($rf.Name)" -ForegroundColor Red
            Write-Host "   Fix: Remove this line - package doesn't exist" -ForegroundColor Gray
        }
    }
    
    # Check for missing __init__.py
    $srcDirs = Get-ChildItem -Path . -Directory -Recurse | Where-Object { $_.Name -eq 'src' -or $_.Parent.Name -eq 'src' }
    foreach ($dir in $srcDirs) {
        $initFile = Join-Path $dir.FullName '__init__.py'
        if (-not (Test-Path $initFile)) {
            Write-Host "🟡 [DOC-003] Missing __init__.py in $($dir.FullName)" -ForegroundColor Yellow
            Write-Host "   Fix: touch $initFile" -ForegroundColor Gray
        }
    }
    
    Write-Host "`n✅ Scan complete." -ForegroundColor Green
}

function Watch-Logs {
    param([int]$Interval = 5)
    
    Write-Host "👁️ Watch mode - scanning every $Interval seconds (Ctrl+C to stop)" -ForegroundColor Cyan
    
    while ($true) {
        $output = docker-compose logs --tail=50 2>&1 | Out-String
        $matches = Scan-Antibodies -InputText $output
        
        if ($matches.Count -gt 0) {
            [Console]::Beep($Script:Frequencies.Awakening, 200)
        }
        
        Start-Sleep -Seconds $Interval
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

switch ($Command) {
    'scan' {
        if ($Text) {
            Scan-Antibodies -InputText $Text
        } elseif ($input) {
            $piped = $input | Out-String
            Scan-Antibodies -InputText $piped
        } else {
            Write-Host "❌ No input provided. Use: .\Deploy-Antibodies.ps1 scan 'error text'" -ForegroundColor Red
        }
    }
    
    'deploy' {
        if ($Text) {
            $matches = Scan-Antibodies -InputText $Text
            Deploy-Fixes -Matches $matches -Auto:$Auto -Force:$Force
        } else {
            Write-Host "❌ No input provided." -ForegroundColor Red
        }
    }
    
    'list' {
        List-Antibodies -FilterCategory $Category -FilterSeverity $Severity
    }
    
    'fix' {
        Fix-CurrentDirectory
    }
    
    'watch' {
        Watch-Logs -Interval $WatchInterval
    }
    
    'grimoire' {
        Write-Grimoire
    }
    
    default {
        Write-Grimoire
    }
}

Write-Host "`n🖤 Mischief managed." -ForegroundColor Magenta
