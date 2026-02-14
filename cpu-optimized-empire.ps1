# cpu-optimized-empire.ps1
# CPU-OPTIMIZED Sovereign Docker Automation for Resource-Constrained Systems

param(
    [switch]$Build,
    [switch]$Deploy,
    [switch]$Monitor,
    [switch]$Backup,
    [switch]$Restore,
    [switch]$SecurityScan,
    [switch]$Throttled = $true  # Default to throttled mode for high CPU systems
)

$ErrorActionPreference = "Stop"

# Configuration - Optimized for high CPU usage systems
$EMPIRE_ROOT = $PWD.Path
$BACKUP_DIR = Join-Path $EMPIRE_ROOT "backups"
$LOG_DIR = Join-Path $EMPIRE_ROOT "logs"
$CPU_THRESHOLD = 80  # Pause operations if CPU > 80%
$MAX_CONCURRENT_BUILDS = 2  # Limit concurrent Docker builds

# Ensure directories exist
New-Item -ItemType Directory -Force -Path $BACKUP_DIR, $LOG_DIR | Out-Null

function Write-SovereignLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage -ForegroundColor $(
        switch ($Level) {
            "ERROR" { "Red" }
            "WARNING" { "Yellow" }
            "SUCCESS" { "Green" }
            default { "Cyan" }
        }
    )
    Add-Content -Path "$LOG_DIR\automation.log" -Value $logMessage
}

function Test-SystemResources {
    try {
        # Use Performance Counter for accurate CPU reading
        $cpu = Get-Counter '\Processor(_Total)\% Processor Time' -MaxSamples 1 -ErrorAction SilentlyContinue
        $cpuValue = [math]::Round($cpu.CounterSamples[0].CookedValue, 2)
        
        # Memory calculation
        $memory = Get-WmiObject -Class Win32_OperatingSystem
        $memUsage = [math]::Round(((($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) * 1024) / ($memory.TotalVisibleMemorySize * 1024)) * 100, 2)
        
        return @{
            CPU = $cpuValue
            Memory = $memUsage
            CanProceed = ($cpuValue -lt $CPU_THRESHOLD)
        }
    } catch {
        Write-SovereignLog "Could not read system metrics, proceeding with caution" "WARNING"
        return @{ CPU = 0; Memory = 0; CanProceed = $true }
    }
}

function Wait-ForSystemCooldown {
    if (-not $Throttled) { return }
    
    while ($true) {
        $resources = Test-SystemResources
        if ($resources.CanProceed) {
            Write-SovereignLog "System resources OK: CPU $($resources.CPU)%, Memory $($resources.Memory)%" "INFO"
            break
        }
        Write-SovereignLog "System overloaded: CPU $($resources.CPU)%, Memory $($resources.Memory)% - waiting..." "WARNING"
        Start-Sleep -Seconds 10
    }
}

function Start-SovereignBuild {
    Write-SovereignLog "🔨 Building sovereign Docker infrastructure (CPU-OPTIMIZED)..." "BUILD"
    
    # Essential services only for resource-constrained systems
    $coreImages = @(
        @{ Name = "redis"; Path = "." },
        @{ Name = "qdrant"; Path = "." },
        @{ Name = "research-promptsvc"; Path = "research-swarm/promptsvc" },
        @{ Name = "research-langchain"; Path = "research-swarm/langchain" },
        @{ Name = "empire-dashboard"; Path = "empire-dashboard" }
    )
    
    $builtCount = 0
    foreach ($image in $coreImages) {
        Wait-ForSystemCooldown
        
        $imageName = "strategickhaos/$($image.Name):latest"
        $imagePath = Join-Path $EMPIRE_ROOT $image.Path
        
        Write-SovereignLog "Building $($image.Name)... ($($builtCount + 1)/$($coreImages.Count))" "BUILD"
        
        if (Test-Path "$imagePath\Dockerfile") {
            try {
                # Resource-constrained build with memory and CPU limits
                docker build -t $imageName $imagePath --no-cache=false --memory=2g --cpus=1
                Write-SovereignLog "✅ Built $($image.Name)" "SUCCESS"
            } catch {
                Write-SovereignLog "❌ Failed to build $($image.Name): $_" "ERROR"
            }
        } else {
            # Create minimal Dockerfile for missing services
            $dockerfileContent = @"
FROM alpine:3.18
RUN apk add --no-cache curl
WORKDIR /app
CMD ["sh", "-c", "echo 'Service placeholder for $($image.Name)' && sleep 3600"]
"@
            New-Item -ItemType Directory -Force -Path $imagePath | Out-Null
            $dockerfileContent | Out-File -FilePath "$imagePath\Dockerfile" -Encoding UTF8
            
            docker build -t $imageName $imagePath
            Write-SovereignLog "✅ Created placeholder for $($image.Name)" "SUCCESS"
        }
        
        $builtCount++
        Start-Sleep -Seconds 5  # Cool down between builds
    }
    
    Write-SovereignLog "✅ Build complete ($builtCount images)" "SUCCESS"
}

function Start-SovereignDeploy {
    Write-SovereignLog "🚀 Deploying sovereign empire (RESOURCE-OPTIMIZED)..." "DEPLOY"
    
    Wait-ForSystemCooldown
    
    # Stop existing containers gracefully
    try {
        docker-compose -f "$EMPIRE_ROOT\docker-compose.unified-empire.yml" down --remove-orphans 2>$null
    } catch {
        Write-SovereignLog "No existing compose stack to stop" "INFO"
    }
    
    # Create networks
    try {
        docker network create empire 2>$null | Out-Null
        docker network create sovereign-private 2>$null | Out-Null
    } catch {
        Write-SovereignLog "Networks already exist" "INFO"
    }
    
    Wait-ForSystemCooldown
    
    # Start core infrastructure first (sequential to avoid CPU spike)
    Write-SovereignLog "Starting Redis..." "DEPLOY"
    docker-compose -f "$EMPIRE_ROOT\docker-compose.unified-empire.yml" up -d redis
    Start-Sleep -Seconds 15
    
    Wait-ForSystemCooldown
    
    Write-SovereignLog "Starting Qdrant..." "DEPLOY"
    docker-compose -f "$EMPIRE_ROOT\docker-compose.unified-empire.yml" up -d qdrant
    Start-Sleep -Seconds 15
    
    Wait-ForSystemCooldown
    
    Write-SovereignLog "Starting core services..." "DEPLOY"
    docker-compose -f "$EMPIRE_ROOT\docker-compose.unified-empire.yml" up -d research-promptsvc research-langchain
    Start-Sleep -Seconds 10
    
    Wait-ForSystemCooldown
    
    Write-SovereignLog "Starting dashboard..." "DEPLOY"
    docker-compose -f "$EMPIRE_ROOT\docker-compose.unified-empire.yml" up -d empire-dashboard
    
    Write-SovereignLog "✅ Core deployment complete" "SUCCESS"
}

function Start-SovereignMonitor {
    Write-SovereignLog "📊 Starting sovereign monitoring (LIGHTWEIGHT)..." "MONITOR"
    
    while ($true) {
        try {
            Clear-Host
            Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
            Write-Host "⚡ STRATEGICKHAOS EMPIRE - CPU-OPTIMIZED MONITOR" -ForegroundColor Green
            Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
            Write-Host ""
            
            # System resources
            $resources = Test-SystemResources
            Write-Host "💻 SYSTEM RESOURCES:" -ForegroundColor Yellow
            Write-Host "  CPU Usage: $($resources.CPU)%" -ForegroundColor $(if ($resources.CPU -gt 80) { "Red" } else { "Green" })
            Write-Host "  Memory Usage: $($resources.Memory)%" -ForegroundColor $(if ($resources.Memory -gt 80) { "Red" } else { "Green" })
            Write-Host ""
            
            # Container status (lightweight check)
            Write-Host "🐋 CONTAINERS:" -ForegroundColor Yellow
            $containers = docker ps --format "table {{.Names}}\t{{.Status}}" 2>$null
            if ($containers) {
                $containers | Out-String | Write-Host
            } else {
                Write-Host "  No containers running" -ForegroundColor Gray
            }
            
            # Quick service check
            Write-Host "`n🔍 SERVICE HEALTH:" -ForegroundColor Yellow
            $services = @(
                @{ Name = "Redis"; Port = 6379 },
                @{ Name = "Qdrant"; Port = 6333 },
                @{ Name = "Dashboard"; Port = 8088 }
            )
            
            foreach ($service in $services) {
                try {
                    $connection = Test-NetConnection -ComputerName "localhost" -Port $service.Port -InformationLevel Quiet -WarningAction SilentlyContinue
                    $status = if ($connection) { "✅ Online" } else { "❌ Offline" }
                    Write-Host "  $($service.Name): $status" -ForegroundColor $(if ($connection) { "Green" } else { "Red" })
                } catch {
                    Write-Host "  $($service.Name): ❓ Unknown" -ForegroundColor Yellow
                }
            }
            
            Write-Host "`n[Ctrl+C to exit] - Next refresh in 10 seconds..." -ForegroundColor Gray
            Start-Sleep -Seconds 10
        } catch {
            Write-SovereignLog "Monitor error: $_" "ERROR"
            Start-Sleep -Seconds 5
        }
    }
}

function Start-PerformanceAnalysis {
    Write-SovereignLog "📈 Performance Analysis & Resource Cross-Reference (RESMON INTEGRATION)" "ANALYSIS"
    
    # Create performance monitoring that "the world has never seen"
    $performanceData = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        system_metrics = @{}
        docker_metrics = @{}
        analysis = @{}
        recommendations = @()
    }
    
    # Collect system-wide metrics (like resmon)
    try {
        # CPU detailed breakdown
        $cpuCounters = Get-Counter @(
            '\Processor(_Total)\% Processor Time',
            '\Processor(_Total)\% User Time',
            '\Processor(_Total)\% Privileged Time'
        ) -MaxSamples 3 -SampleInterval 2
        
        $performanceData.system_metrics.cpu = @{
            total = [math]::Round(($cpuCounters[0].CounterSamples | Measure-Object CookedValue -Average).Average, 2)
            user = [math]::Round(($cpuCounters[1].CounterSamples | Measure-Object CookedValue -Average).Average, 2)
            system = [math]::Round(($cpuCounters[2].CounterSamples | Measure-Object CookedValue -Average).Average, 2)
        }
        
        # Memory detailed breakdown
        $memory = Get-WmiObject -Class Win32_OperatingSystem
        $performanceData.system_metrics.memory = @{
            total_gb = [math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)
            available_gb = [math]::Round($memory.FreePhysicalMemory / 1MB, 2)
            used_percent = [math]::Round(((($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize) * 100), 2)
        }
        
        # Disk I/O
        $diskCounters = Get-Counter @(
            '\PhysicalDisk(_Total)\Disk Reads/sec',
            '\PhysicalDisk(_Total)\Disk Writes/sec'
        ) -MaxSamples 1
        
        $performanceData.system_metrics.disk = @{
            reads_per_sec = [math]::Round($diskCounters[0].CounterSamples[0].CookedValue, 2)
            writes_per_sec = [math]::Round($diskCounters[1].CounterSamples[0].CookedValue, 2)
        }
    } catch {
        Write-SovereignLog "Could not collect detailed system metrics" "WARNING"
    }
    
    # Docker container performance analysis
    try {
        $dockerStats = docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>$null
        if ($dockerStats) {
            $performanceData.docker_metrics.containers = @()
            foreach ($line in $dockerStats | Select-Object -Skip 1) {
                if ($line -match '^(.+?)\s+(.+?)%\s+(.+?) / (.+?)$') {
                    $performanceData.docker_metrics.containers += @{
                        name = $matches[1].Trim()
                        cpu_percent = $matches[2].Trim()
                        memory_usage = $matches[3].Trim()
                        memory_limit = $matches[4].Trim()
                    }
                }
            }
        }
    } catch {
        Write-SovereignLog "Could not collect Docker metrics" "WARNING"
    }
    
    # Intelligent analysis (AI-like reasoning)
    $cpuUsage = $performanceData.system_metrics.cpu.total
    $memUsage = $performanceData.system_metrics.memory.used_percent
    
    if ($cpuUsage -gt 90) {
        $performanceData.recommendations += "CRITICAL: CPU usage at $cpuUsage% - Consider scaling down Docker services"
        $performanceData.analysis.cpu_status = "CRITICAL"
    } elseif ($cpuUsage -gt 70) {
        $performanceData.recommendations += "WARNING: CPU usage at $cpuUsage% - Monitor for performance degradation"
        $performanceData.analysis.cpu_status = "WARNING"
    } else {
        $performanceData.analysis.cpu_status = "OPTIMAL"
    }
    
    if ($memUsage -gt 85) {
        $performanceData.recommendations += "Memory usage at $memUsage% - Consider adding swap or reducing container memory limits"
        $performanceData.analysis.memory_status = "WARNING"
    } else {
        $performanceData.analysis.memory_status = "OPTIMAL"
    }
    
    # Cross-reference with external tools (like resmon would do)
    $performanceData.analysis.resmon_equivalent = @{
        cpu_efficiency = if ($cpuUsage -lt 50) { "Underutilized" } elseif ($cpuUsage -lt 80) { "Optimal" } else { "Overloaded" }
        memory_efficiency = if ($memUsage -lt 60) { "Sufficient" } elseif ($memUsage -lt 80) { "Moderate" } else { "Constrained" }
        overall_health = if ($cpuUsage -lt 70 -and $memUsage -lt 70) { "EXCELLENT" } elseif ($cpuUsage -lt 85 -and $memUsage -lt 85) { "GOOD" } else { "NEEDS ATTENTION" }
    }
    
    # Save performance report
    $reportPath = "$LOG_DIR\performance-analysis-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $performanceData | ConvertTo-Json -Depth 4 | Out-File $reportPath
    
    # Display results
    Clear-Host
    Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║                    🧠 PERFORMANCE ANALYSIS REPORT 🧠                        ║" -ForegroundColor Magenta
    Write-Host "║           (Cross-Referenced Performance Intelligence)                        ║" -ForegroundColor Magenta
    Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
    
    Write-Host "📊 SYSTEM PERFORMANCE:" -ForegroundColor Yellow
    Write-Host "  CPU: $($performanceData.system_metrics.cpu.total)% (User: $($performanceData.system_metrics.cpu.user)%, System: $($performanceData.system_metrics.cpu.system)%)" -ForegroundColor White
    Write-Host "  Memory: $($performanceData.system_metrics.memory.used_percent)% ($($performanceData.system_metrics.memory.available_gb)GB available)" -ForegroundColor White
    Write-Host "  Disk I/O: $($performanceData.system_metrics.disk.reads_per_sec) R/s, $($performanceData.system_metrics.disk.writes_per_sec) W/s" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🔍 INTELLIGENT ANALYSIS:" -ForegroundColor Yellow
    Write-Host "  CPU Status: $($performanceData.analysis.cpu_status)" -ForegroundColor $(if ($performanceData.analysis.cpu_status -eq "CRITICAL") { "Red" } elseif ($performanceData.analysis.cpu_status -eq "WARNING") { "Yellow" } else { "Green" })
    Write-Host "  Memory Status: $($performanceData.analysis.memory_status)" -ForegroundColor $(if ($performanceData.analysis.memory_status -eq "WARNING") { "Yellow" } else { "Green" })
    Write-Host "  Overall Health: $($performanceData.analysis.resmon_equivalent.overall_health)" -ForegroundColor $(if ($performanceData.analysis.resmon_equivalent.overall_health -eq "NEEDS ATTENTION") { "Red" } elseif ($performanceData.analysis.resmon_equivalent.overall_health -eq "GOOD") { "Yellow" } else { "Green" })
    Write-Host ""
    
    if ($performanceData.recommendations.Count -gt 0) {
        Write-Host "💡 RECOMMENDATIONS:" -ForegroundColor Yellow
        foreach ($rec in $performanceData.recommendations) {
            Write-Host "  • $rec" -ForegroundColor Cyan
        }
        Write-Host ""
    }
    
    Write-Host "📁 Report saved: $reportPath" -ForegroundColor Gray
    
    return $performanceData
}

function Start-SovereignBackup {
    Write-SovereignLog "💾 Starting sovereign backup..." "BACKUP"
    
    Wait-ForSystemCooldown
    
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupPath = Join-Path $BACKUP_DIR "backup-$timestamp"
    New-Item -ItemType Directory -Force -Path $backupPath | Out-Null
    
    # Backup compose files
    Write-SovereignLog "Backing up configuration..." "BACKUP"
    Copy-Item "$EMPIRE_ROOT\docker-compose*.yml" $backupPath -ErrorAction SilentlyContinue
    Copy-Item "$EMPIRE_ROOT\.env*" $backupPath -ErrorAction SilentlyContinue
    Copy-Item "$EMPIRE_ROOT\discovery.yml" $backupPath -ErrorAction SilentlyContinue
    
    # Backup small volumes only (avoid large data during high CPU)
    try {
        $volumes = docker volume ls -q 2>$null
        if ($volumes) {
            Write-SovereignLog "Backing up critical volumes only..." "BACKUP"
            foreach ($volume in $volumes) {
                if ($volume -match "(redis|config|logs)" -and $volume.Length -lt 50) {
                    docker run --rm -v ${volume}:/volume -v ${backupPath}:/backup alpine:3.18 tar czf /backup/${volume}.tar.gz -C /volume . 2>$null
                }
            }
        }
    } catch {
        Write-SovereignLog "Volume backup skipped due to system load" "WARNING"
    }
    
    # Create lightweight manifest
    @{
        timestamp = $timestamp
        system = @{
            cpu_usage = (Test-SystemResources).CPU
            memory_usage = (Test-SystemResources).Memory
        }
        containers = @(docker ps --format "{{.Names}}" 2>$null)
        compose_files = @(Get-ChildItem "$EMPIRE_ROOT\docker-compose*.yml" | Select-Object -ExpandProperty Name)
    } | ConvertTo-Json -Depth 3 | Out-File "$backupPath\manifest.json"
    
    Write-SovereignLog "✅ Backup complete: $backupPath" "SUCCESS"
}

function Start-SovereignSecurityScan {
    Write-SovereignLog "🔒 Starting lightweight security scan..." "SECURITY"
    
    Wait-ForSystemCooldown
    
    # Check for exposed ports (lightweight)
    Write-SovereignLog "Checking for exposed ports..." "SECURITY"
    $exposedPorts = docker ps --format "{{.Names}}\t{{.Ports}}" 2>$null | Where-Object { $_ -match "0.0.0.0" }
    if ($exposedPorts) {
        foreach ($port in $exposedPorts) {
            Write-SovereignLog "WARNING: Exposed port detected - $port" "WARNING"
        }
    } else {
        Write-SovereignLog "✅ No dangerous exposed ports found" "SUCCESS"
    }
    
    # Check for privileged containers
    Write-SovereignLog "Checking for privileged containers..." "SECURITY"
    $containers = docker ps -q 2>$null
    if ($containers) {
        foreach ($container in $containers) {
            try {
                $privileged = docker inspect --format='{{.HostConfig.Privileged}}' $container 2>$null
                if ($privileged -eq "true") {
                    $name = docker inspect --format='{{.Name}}' $container 2>$null
                    Write-SovereignLog "WARNING: Privileged container - $name" "WARNING"
                }
            } catch {
                # Skip if container inspection fails
            }
        }
    }
    
    Write-SovereignLog "✅ Security scan complete" "SUCCESS"
}

# Main execution
Write-Host @"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ⚡ STRATEGICKHAOS CPU-OPTIMIZED AUTOMATION ⚡            ║
║                                                               ║
║  System Load: HIGH | Throttled Mode: $($Throttled.ToString().ToUpper())              ║
║  Performance Analysis: RESMON-EQUIVALENT                      ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Check initial system state
$initialResources = Test-SystemResources
Write-SovereignLog "Initial system state: CPU $($initialResources.CPU)%, Memory $($initialResources.Memory)%" "INFO"

if ($Build) { Start-SovereignBuild }
if ($Deploy) { Start-SovereignDeploy }
if ($Monitor) { Start-SovereignMonitor }
if ($Backup) { Start-SovereignBackup }
if ($SecurityScan) { Start-SovereignSecurityScan }

# Special performance analysis mode
if (-not ($Build -or $Deploy -or $Monitor -or $Backup -or $SecurityScan)) {
    $performanceResult = Start-PerformanceAnalysis
    
    Write-Host "`nUsage:" -ForegroundColor Yellow
    Write-Host "  .\cpu-optimized-empire.ps1 -Build          # Build core images only" -ForegroundColor White
    Write-Host "  .\cpu-optimized-empire.ps1 -Deploy         # Deploy optimized stack" -ForegroundColor White
    Write-Host "  .\cpu-optimized-empire.ps1 -Monitor        # Lightweight monitoring" -ForegroundColor White
    Write-Host "  .\cpu-optimized-empire.ps1 -Backup         # Quick backup" -ForegroundColor White
    Write-Host "  .\cpu-optimized-empire.ps1 -SecurityScan   # Security check" -ForegroundColor White
    Write-Host "`nAdd -Throttled:`$false to disable CPU throttling" -ForegroundColor Gray
    Write-Host "`nRun without parameters for performance analysis" -ForegroundColor Magenta
}