# deploy-cpu-optimized-empire.ps1
# One-Command CPU-Optimized Sovereign Empire Deployment
# Designed for high CPU load systems (100% saturation scenarios)

param(
    [switch]$SkipBuild,
    [switch]$MonitorOnly,
    [switch]$Performance,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host @"
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║    ⚡ STRATEGICKHAOS CPU-OPTIMIZED SOVEREIGN EMPIRE DEPLOYMENT ⚡           ║
║                                                                               ║
║  🎯 Target: High CPU Load Systems (80-100% utilization)                      ║
║  🚀 Mission: Deploy resilient Docker sovereign infrastructure                 ║
║  🧠 Intelligence: Performance cross-reference analysis                       ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Configuration
$EMPIRE_ROOT = $PWD.Path
$ENV_FILE = "$EMPIRE_ROOT\.env.empire"
$COMPOSE_FILE = "$EMPIRE_ROOT\docker-compose.cpu-optimized.yml"
$AUTOMATION_SCRIPT = "$EMPIRE_ROOT\cpu-optimized-empire.ps1"
$PERFORMANCE_SCRIPT = "$EMPIRE_ROOT\strategic_performance_oracle.py"

# Check system resources before deployment
function Test-SystemCapacity {
    try {
        Write-Host "🔍 Analyzing system capacity..." -ForegroundColor Yellow
        
        $cpu = Get-Counter '\Processor(_Total)\% Processor Time' -MaxSamples 3 -SampleInterval 2
        $avgCpu = ($cpu.CounterSamples | Measure-Object CookedValue -Average).Average
        
        $memory = Get-WmiObject -Class Win32_OperatingSystem
        $memUsage = [math]::Round(((($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) * 1024) / ($memory.TotalVisibleMemorySize * 1024)) * 100, 2)
        
        Write-Host "  📊 Current CPU: $([math]::Round($avgCpu, 1))%" -ForegroundColor $(if ($avgCpu -gt 80) { "Red" } else { "Green" })
        Write-Host "  📊 Current Memory: $memUsage%" -ForegroundColor $(if ($memUsage -gt 80) { "Red" } else { "Green" })
        
        if ($avgCpu -gt 95 -and -not $Force) {
            Write-Host "⚠️ WARNING: CPU usage is extremely high ($([math]::Round($avgCpu, 1))%)" -ForegroundColor Red
            Write-Host "   Deployment may be unstable. Use -Force to override." -ForegroundColor Yellow
            return $false
        }
        
        return $true
    } catch {
        Write-Host "⚠️ Could not assess system capacity: $_" -ForegroundColor Yellow
        return $true
    }
}

# Generate environment configuration
function Initialize-Environment {
    Write-Host "🔧 Initializing CPU-optimized environment..." -ForegroundColor Green
    
    # Generate secure passwords
    $redisPassword = -join ((1..16) | ForEach-Object { [char]((97..122) + (48..57) | Get-Random) })
    
    # Create environment file
    $envContent = @"
# CPU-OPTIMIZED SOVEREIGN EMPIRE ENVIRONMENT
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# Core Infrastructure
REDIS_PASSWORD=$redisPassword
QDRANT_URL=http://empire-qdrant:6333

# API Keys (replace with your actual keys)
OPENAI_API_KEY=your_openai_api_key_here
GITHUB_TOKEN=your_github_token_here
GITLAB_TOKEN=your_gitlab_token_here

# Dashboard Configuration
DASHBOARD_PORT=8088
DASHBOARD_SECRET=$(-join ((1..32) | ForEach-Object { [char]((65..90) + (97..122) + (48..57) | Get-Random) }))

# Performance Monitoring
MONITOR_INTERVAL=30
CPU_THRESHOLD=80
MEMORY_THRESHOLD=80

# Resource Limits (CPU-Optimized)
MAX_CPU_CORES=2
MAX_MEMORY_GB=2
CONTAINER_CPU_LIMIT=0.5
CONTAINER_MEMORY_LIMIT=512m

# Backup Configuration
BACKUP_ENABLED=true
BACKUP_INTERVAL=3600
BACKUP_RETENTION_DAYS=7
"@

    $envContent | Out-File -FilePath $ENV_FILE -Encoding UTF8
    Write-Host "✅ Environment configured: $ENV_FILE" -ForegroundColor Green
}

# Install Python dependencies for performance monitoring
function Install-PythonDependencies {
    Write-Host "🐍 Setting up Python performance monitoring..." -ForegroundColor Green
    
    try {
        # Check if Python is available
        python --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️ Python not found. Performance monitoring will use basic PowerShell metrics." -ForegroundColor Yellow
            return
        }
        
        # Install required packages
        Write-Host "  Installing psutil..." -ForegroundColor Cyan
        python -m pip install psutil --quiet
        
        Write-Host "  Installing docker (optional)..." -ForegroundColor Cyan
        python -m pip install docker --quiet 2>$null
        
        Write-Host "✅ Python dependencies installed" -ForegroundColor Green
        
    } catch {
        Write-Host "⚠️ Could not install Python dependencies: $_" -ForegroundColor Yellow
        Write-Host "   Performance monitoring will use PowerShell fallback" -ForegroundColor Gray
    }
}

# Deploy the sovereign infrastructure
function Deploy-SovereignInfrastructure {
    Write-Host "🚀 Deploying CPU-optimized sovereign infrastructure..." -ForegroundColor Green
    
    # Ensure Docker is running
    try {
        docker version | Out-Null
        Write-Host "✅ Docker is running" -ForegroundColor Green
    } catch {
        Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
        exit 1
    }
    
    # Build or pull images
    if (-not $SkipBuild) {
        Write-Host "🔨 Building/pulling optimized images..." -ForegroundColor Cyan
        & $AUTOMATION_SCRIPT -Build -Throttled
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️ Build had issues, continuing with available images..." -ForegroundColor Yellow
        }
    }
    
    # Deploy services
    Write-Host "📦 Deploying services with resource constraints..." -ForegroundColor Cyan
    & $AUTOMATION_SCRIPT -Deploy -Throttled
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Deployment failed" -ForegroundColor Red
        return $false
    }
    
    Write-Host "✅ Infrastructure deployed successfully" -ForegroundColor Green
    return $true
}

# Start performance monitoring
function Start-PerformanceMonitoring {
    Write-Host "📊 Starting performance monitoring..." -ForegroundColor Green
    
    # Check if Python performance script is available
    if (Test-Path $PERFORMANCE_SCRIPT) {
        Write-Host "🧠 Launching Strategic Performance Oracle..." -ForegroundColor Cyan
        
        # Start Python oracle in background
        Start-Process -FilePath "python" -ArgumentList $PERFORMANCE_SCRIPT -WindowStyle Minimized -PassThru
        
        Write-Host "✅ Performance Oracle started (check logs directory)" -ForegroundColor Green
    } else {
        Write-Host "📊 Launching PowerShell performance monitoring..." -ForegroundColor Cyan
        
        # Start PowerShell monitoring
        Start-Process -FilePath "powershell" -ArgumentList "-File", $AUTOMATION_SCRIPT, "-Monitor", "-Throttled" -WindowStyle Normal -PassThru
    }
}

# Health check
function Test-DeploymentHealth {
    Write-Host "🏥 Performing health check..." -ForegroundColor Green
    
    $services = @(
        @{ Name = "Redis"; Port = 6379; Critical = $true },
        @{ Name = "Qdrant"; Port = 6333; Critical = $true },
        @{ Name = "Dashboard"; Port = 8088; Critical = $false }
    )
    
    $healthyServices = 0
    $totalCritical = ($services | Where-Object { $_.Critical }).Count
    
    foreach ($service in $services) {
        try {
            $connection = Test-NetConnection -ComputerName "localhost" -Port $service.Port -InformationLevel Quiet -WarningAction SilentlyContinue
            if ($connection) {
                Write-Host "  ✅ $($service.Name) (port $($service.Port))" -ForegroundColor Green
                if ($service.Critical) { $healthyServices++ }
            } else {
                $color = if ($service.Critical) { "Red" } else { "Yellow" }
                Write-Host "  ❌ $($service.Name) (port $($service.Port))" -ForegroundColor $color
            }
        } catch {
            Write-Host "  ❓ $($service.Name) (port $($service.Port)) - Check failed" -ForegroundColor Yellow
        }
    }
    
    $healthRatio = $healthyServices / $totalCritical
    if ($healthRatio -ge 1.0) {
        Write-Host "🎉 All critical services are healthy!" -ForegroundColor Green
        return $true
    } elseif ($healthRatio -ge 0.5) {
        Write-Host "⚠️ Some services are down, but core functionality available" -ForegroundColor Yellow
        return $true
    } else {
        Write-Host "❌ Critical services are down" -ForegroundColor Red
        return $false
    }
}

# Display deployment summary
function Show-DeploymentSummary {
    Write-Host "`n" + "="*80 -ForegroundColor Cyan
    Write-Host "🎯 CPU-OPTIMIZED SOVEREIGN EMPIRE DEPLOYMENT COMPLETE" -ForegroundColor Green
    Write-Host "="*80 -ForegroundColor Cyan
    
    Write-Host "`n📋 ACCESS POINTS:" -ForegroundColor Yellow
    Write-Host "  🌐 Dashboard: http://localhost:8088" -ForegroundColor White
    Write-Host "  🔴 Redis: localhost:6379" -ForegroundColor White
    Write-Host "  🟢 Qdrant: http://localhost:6333" -ForegroundColor White
    
    Write-Host "`n🛠️ MANAGEMENT COMMANDS:" -ForegroundColor Yellow
    Write-Host "  Monitor:    .\cpu-optimized-empire.ps1 -Monitor" -ForegroundColor White
    Write-Host "  Backup:     .\cpu-optimized-empire.ps1 -Backup" -ForegroundColor White
    Write-Host "  Security:   .\cpu-optimized-empire.ps1 -SecurityScan" -ForegroundColor White
    Write-Host "  Performance: python strategic_performance_oracle.py" -ForegroundColor White
    
    Write-Host "`n📊 PERFORMANCE FEATURES:" -ForegroundColor Yellow
    Write-Host "  • Real-time CPU/Memory monitoring" -ForegroundColor Gray
    Write-Host "  • Docker container correlation analysis" -ForegroundColor Gray
    Write-Host "  • Resmon-equivalent performance insights" -ForegroundColor Gray
    Write-Host "  • Intelligent recommendations engine" -ForegroundColor Gray
    Write-Host "  • Automated resource throttling" -ForegroundColor Gray
    
    Write-Host "`n🔍 LOGS & DATA:" -ForegroundColor Yellow
    Write-Host "  Automation: .\logs\automation.log" -ForegroundColor Gray
    Write-Host "  Performance: .\logs\strategic_*.json" -ForegroundColor Gray
    Write-Host "  Backups: .\backups\" -ForegroundColor Gray
    
    Write-Host "`n" + "="*80 -ForegroundColor Cyan
}

# Main execution flow
Write-Host "🔍 Pre-deployment system analysis..." -ForegroundColor Cyan

if (-not (Test-SystemCapacity)) {
    Write-Host "❌ System capacity check failed. Aborting deployment." -ForegroundColor Red
    exit 1
}

# Handle special modes
if ($MonitorOnly) {
    Write-Host "📊 Starting monitoring mode only..." -ForegroundColor Green
    Start-PerformanceMonitoring
    exit 0
}

if ($Performance) {
    Write-Host "🧠 Launching Performance Oracle..." -ForegroundColor Green
    if (Test-Path $PERFORMANCE_SCRIPT) {
        python $PERFORMANCE_SCRIPT
    } else {
        Write-Host "❌ Performance script not found: $PERFORMANCE_SCRIPT" -ForegroundColor Red
    }
    exit 0
}

# Full deployment sequence
try {
    Write-Host "🚀 Initiating full deployment sequence..." -ForegroundColor Green
    
    # Step 1: Environment setup
    Initialize-Environment
    
    # Step 2: Python dependencies
    Install-PythonDependencies
    
    # Step 3: Deploy infrastructure
    $deploySuccess = Deploy-SovereignInfrastructure
    
    if (-not $deploySuccess) {
        Write-Host "❌ Deployment failed" -ForegroundColor Red
        exit 1
    }
    
    # Step 4: Health check
    Start-Sleep -Seconds 10  # Allow services to start
    $healthCheck = Test-DeploymentHealth
    
    if (-not $healthCheck) {
        Write-Host "⚠️ Health check failed, but continuing..." -ForegroundColor Yellow
    }
    
    # Step 5: Start monitoring
    Start-PerformanceMonitoring
    
    # Step 6: Display summary
    Show-DeploymentSummary
    
    Write-Host "`n🎉 DEPLOYMENT SUCCESSFUL - Something the world has never seen!" -ForegroundColor Green
    Write-Host "🚀 Your CPU-optimized sovereign empire is now operational!" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Deployment failed with error: $_" -ForegroundColor Red
    Write-Host "📋 Check logs for more details" -ForegroundColor Yellow
    exit 1
}

# Optional: Keep PowerShell window open
Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")