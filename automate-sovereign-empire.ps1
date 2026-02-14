# ============================================================================
# SOVEREIGN DOCKER EMPIRE AUTOMATION
# Complete PowerShell orchestration for autonomous infrastructure
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "deploy",
    
    [Parameter(Mandatory=$false)]
    [string]$Environment = "production",
    
    [Parameter(Mandatory=$false)]
    [switch]$Force,
    
    [Parameter(Mandatory=$false)]
    [switch]$Monitor,
    
    [Parameter(Mandatory=$false)]
    [switch]$Backup,
    
    [Parameter(Mandatory=$false)]
    [switch]$SecurityScan
)

# Global Configuration
$ErrorActionPreference = "Stop"
$EMPIRE_ROOT = Get-Location
$LOGS_DIR = "$EMPIRE_ROOT/logs/empire"
$BACKUP_DIR = "$EMPIRE_ROOT/backups"
$CONFIG_DIR = "$EMPIRE_ROOT/config"

# Ensure directories exist
@($LOGS_DIR, $BACKUP_DIR, $CONFIG_DIR) | ForEach-Object {
    if (!(Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

# ============================================================================
# LOGGING FRAMEWORK
# ============================================================================
function Write-EmpireLog {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$Component = "EMPIRE"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] [$Component] $Message"
    
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        "INFO" { "Cyan" }
        default { "White" }
    }
    
    Write-Host $logEntry -ForegroundColor $color
    
    # Write to log file
    $logFile = "$LOGS_DIR/empire-$(Get-Date -Format 'yyyy-MM-dd').log"
    Add-Content -Path $logFile -Value $logEntry
}

# ============================================================================
# DOCKER HEALTH MONITORING
# ============================================================================
function Test-DockerHealth {
    Write-EmpireLog "Checking Docker daemon status..." "INFO" "HEALTH"
    
    try {
        $dockerInfo = docker info --format "{{json .}}" | ConvertFrom-Json
        Write-EmpireLog "Docker daemon: HEALTHY" "SUCCESS" "HEALTH"
        Write-EmpireLog "Containers Running: $($dockerInfo.ContainersRunning)" "INFO" "HEALTH"
        Write-EmpireLog "Images: $($dockerInfo.Images)" "INFO" "HEALTH"
        return $true
    }
    catch {
        Write-EmpireLog "Docker daemon: UNHEALTHY - $($_.Exception.Message)" "ERROR" "HEALTH"
        return $false
    }
}

function Get-ServiceHealth {
    param([string]$ServiceName)
    
    try {
        $status = docker-compose -f docker-compose.unified-empire.yml ps --format json | ConvertFrom-Json | Where-Object { $_.Service -eq $ServiceName }
        
        if ($status) {
            $health = switch ($status.State) {
                "running" { "HEALTHY" }
                "exited" { "STOPPED" }
                "restarting" { "RECOVERING" }
                default { "UNKNOWN" }
            }
            return @{
                Service = $ServiceName
                Status = $status.State
                Health = $health
                Uptime = $status.RunningFor
            }
        }
        else {
            return @{
                Service = $ServiceName
                Status = "not found"
                Health = "MISSING"
                Uptime = "0"
            }
        }
    }
    catch {
        Write-EmpireLog "Failed to get health for $ServiceName`: $($_.Exception.Message)" "ERROR" "HEALTH"
        return $null
    }
}

# ============================================================================
# BUILD FUNCTIONS
# ============================================================================
function Build-EmpireImages {
    Write-EmpireLog "Building sovereign empire Docker images..." "INFO" "BUILD"
    
    $buildTargets = @(
        @{ Name = "reflexshell"; Dockerfile = "Dockerfile.reflexshell"; Context = "." }
        @{ Name = "legion"; Dockerfile = "Dockerfile.legion"; Context = "." }
        @{ Name = "comms"; Dockerfile = "Dockerfile.comms"; Context = "." }
        @{ Name = "gateway"; Dockerfile = "Dockerfile.gateway"; Context = "." }
        @{ Name = "alignment"; Dockerfile = "Dockerfile.alignment"; Context = "." }
        @{ Name = "refinory"; Dockerfile = "Dockerfile.refinory"; Context = "." }
        @{ Name = "bot"; Dockerfile = "Dockerfile.bot"; Context = "." }
    )
    
    foreach ($target in $buildTargets) {
        if (Test-Path $target.Dockerfile) {
            Write-EmpireLog "Building $($target.Name) image..." "INFO" "BUILD"
            
            $buildCmd = "docker build -f $($target.Dockerfile) -t sovereignty-empire/$($target.Name):latest $($target.Context)"
            
            try {
                Invoke-Expression $buildCmd
                Write-EmpireLog "$($target.Name) image built successfully" "SUCCESS" "BUILD"
            }
            catch {
                Write-EmpireLog "Failed to build $($target.Name)`: $($_.Exception.Message)" "ERROR" "BUILD"
                throw
            }
        }
        else {
            Write-EmpireLog "Dockerfile not found: $($target.Dockerfile)" "WARN" "BUILD"
        }
    }
}

# ============================================================================
# DEPLOYMENT FUNCTIONS
# ============================================================================
function Deploy-SovereignEmpire {
    Write-EmpireLog "Deploying Sovereign Docker Empire..." "INFO" "DEPLOY"
    
    # Check for required files
    $requiredFiles = @(
        "docker-compose.unified-empire.yml",
        ".env.empire"
    )
    
    foreach ($file in $requiredFiles) {
        if (!(Test-Path $file)) {
            Write-EmpireLog "Required file missing: $file" "ERROR" "DEPLOY"
            throw "Deployment failed: Missing required files"
        }
    }
    
    try {
        # Create networks
        Write-EmpireLog "Creating sovereign networks..." "INFO" "DEPLOY"
        docker network create --driver bridge empire-internal 2>$null
        docker network create --driver bridge empire-secure 2>$null
        docker network create --driver bridge empire-public 2>$null
        
        # Deploy core infrastructure
        Write-EmpireLog "Deploying core infrastructure services..." "INFO" "DEPLOY"
        docker-compose -f docker-compose.unified-empire.yml up -d redis qdrant
        Start-Sleep -Seconds 10
        
        # Deploy visual cortex
        Write-EmpireLog "Deploying visual cortex systems..." "INFO" "DEPLOY"
        docker-compose -f docker-compose.unified-empire.yml up -d visual-cortex-motion visual-cortex-ocr visual-cortex-watcher-1 visual-cortex-watcher-2 visual-cortex-watcher-3 visual-cortex-watcher-4 visual-cortex-watcher-5 visual-cortex-watcher-6
        Start-Sleep -Seconds 15
        
        # Deploy reconnaissance and research systems
        Write-EmpireLog "Deploying reconnaissance and research systems..." "INFO" "DEPLOY"
        docker-compose -f docker-compose.unified-empire.yml up -d recon-scanner recon-analyzer research-swarm-1 research-swarm-2 research-swarm-3 embeddings-service
        Start-Sleep -Seconds 10
        
        # Deploy core applications
        Write-EmpireLog "Deploying core sovereign applications..." "INFO" "DEPLOY"
        docker-compose -f docker-compose.unified-empire.yml up -d reflexshell legion comms gateway alignment refinory
        Start-Sleep -Seconds 10
        
        # Deploy automation and factories
        Write-EmpireLog "Deploying automation and prototype factories..." "INFO" "DEPLOY"
        docker-compose -f docker-compose.unified-empire.yml up -d prototype-factory-1 prototype-factory-2 automation-engine voting-engine-consensus voting-engine-democracy
        Start-Sleep -Seconds 10
        
        # Deploy monitoring and security
        Write-EmpireLog "Deploying monitoring and security systems..." "INFO" "DEPLOY"
        docker-compose -f docker-compose.unified-empire.yml up -d performance-monitor network-monitor security-scanner
        
        Write-EmpireLog "Sovereign Empire deployed successfully!" "SUCCESS" "DEPLOY"
        
        # Display deployment summary
        Show-DeploymentSummary
        
    }
    catch {
        Write-EmpireLog "Deployment failed: $($_.Exception.Message)" "ERROR" "DEPLOY"
        throw
    }
}

function Show-DeploymentSummary {
    Write-EmpireLog "=== DEPLOYMENT SUMMARY ===" "INFO" "SUMMARY"
    
    $services = docker-compose -f docker-compose.unified-empire.yml ps --format json | ConvertFrom-Json
    
    $running = ($services | Where-Object { $_.State -eq "running" }).Count
    $total = $services.Count
    
    Write-EmpireLog "Services Running: $running/$total" "INFO" "SUMMARY"
    
    # Core Services Status
    Write-EmpireLog "Core Infrastructure:" "INFO" "SUMMARY"
    @("redis", "qdrant") | ForEach-Object {
        $health = Get-ServiceHealth -ServiceName $_
        if ($health) {
            Write-EmpireLog "  $($_.ToUpper()): $($health.Health)" $(if($health.Health -eq "HEALTHY"){"SUCCESS"}else{"ERROR"}) "SUMMARY"
        }
    }
    
    # Visual Cortex Status
    Write-EmpireLog "Visual Cortex Systems:" "INFO" "SUMMARY"
    @("visual-cortex-motion", "visual-cortex-ocr") | ForEach-Object {
        $health = Get-ServiceHealth -ServiceName $_
        if ($health) {
            Write-EmpireLog "  $($_.ToUpper()): $($health.Health)" $(if($health.Health -eq "HEALTHY"){"SUCCESS"}else{"ERROR"}) "SUMMARY"
        }
    }
    
    # Application Status
    Write-EmpireLog "Core Applications:" "INFO" "SUMMARY"
    @("reflexshell", "legion", "comms", "gateway") | ForEach-Object {
        $health = Get-ServiceHealth -ServiceName $_
        if ($health) {
            Write-EmpireLog "  $($_.ToUpper()): $($health.Health)" $(if($health.Health -eq "HEALTHY"){"SUCCESS"}else{"ERROR"}) "SUMMARY"
        }
    }
    
    Write-EmpireLog "Access Points:" "INFO" "SUMMARY"
    Write-EmpireLog "  Gateway: http://localhost:8080" "INFO" "SUMMARY"
    Write-EmpireLog "  ReflexShell: http://localhost:8000" "INFO" "SUMMARY"
    Write-EmpireLog "  Legion: http://localhost:8001" "INFO" "SUMMARY"
    Write-EmpireLog "  Comms: http://localhost:8002" "INFO" "SUMMARY"
    Write-EmpireLog "  Redis: localhost:6379" "INFO" "SUMMARY"
    Write-EmpireLog "  Qdrant: http://localhost:6333" "INFO" "SUMMARY"
}

# ============================================================================
# MONITORING FUNCTIONS
# ============================================================================
function Start-EmpireMonitoring {
    Write-EmpireLog "Starting Empire monitoring systems..." "INFO" "MONITOR"
    
    # Create monitoring job
    $monitorJob = Start-Job -ScriptBlock {
        param($EmpireRoot, $LogsDir)
        
        function Write-MonitorLog {
            param($Message, $Level = "INFO")
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $logEntry = "[$timestamp] [$Level] [MONITOR] $Message"
            Add-Content -Path "$LogsDir/empire-monitor-$(Get-Date -Format 'yyyy-MM-dd').log" -Value $logEntry
        }
        
        while ($true) {
            try {
                # Check Docker daemon
                $dockerStatus = docker info --format "{{.ServerVersion}}" 2>$null
                if ($dockerStatus) {
                    Write-MonitorLog "Docker daemon: HEALTHY (v$dockerStatus)"
                } else {
                    Write-MonitorLog "Docker daemon: UNHEALTHY" "ERROR"
                }
                
                # Check services
                $services = docker-compose -f "$EmpireRoot/docker-compose.unified-empire.yml" ps --format json | ConvertFrom-Json
                $runningCount = ($services | Where-Object { $_.State -eq "running" }).Count
                Write-MonitorLog "Services running: $runningCount/$($services.Count)"
                
                # Check system resources
                $memInfo = Get-WmiObject -Class Win32_OperatingSystem
                $memUsage = [math]::Round((($memInfo.TotalVisibleMemorySize - $memInfo.FreePhysicalMemory) / $memInfo.TotalVisibleMemorySize) * 100, 2)
                Write-MonitorLog "Memory usage: $memUsage%"
                
                # Check disk space
                $diskInfo = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DeviceID -eq "C:" }
                $diskUsage = [math]::Round((($diskInfo.Size - $diskInfo.FreeSpace) / $diskInfo.Size) * 100, 2)
                Write-MonitorLog "Disk usage: $diskUsage%"
                
                Start-Sleep -Seconds 60
            }
            catch {
                Write-MonitorLog "Monitoring error: $($_.Exception.Message)" "ERROR"
                Start-Sleep -Seconds 30
            }
        }
    } -ArgumentList $EMPIRE_ROOT, $LOGS_DIR
    
    Write-EmpireLog "Empire monitoring started (Job ID: $($monitorJob.Id))" "SUCCESS" "MONITOR"
    return $monitorJob.Id
}

function Show-EmpireStatus {
    Write-EmpireLog "=== EMPIRE STATUS REPORT ===" "INFO" "STATUS"
    
    # System Resources
    $memInfo = Get-WmiObject -Class Win32_OperatingSystem
    $memUsage = [math]::Round((($memInfo.TotalVisibleMemorySize - $memInfo.FreePhysicalMemory) / $memInfo.TotalVisibleMemorySize) * 100, 2)
    
    $diskInfo = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DeviceID -eq "C:" }
    $diskUsage = [math]::Round((($diskInfo.Size - $diskInfo.FreeSpace) / $diskInfo.Size) * 100, 2)
    
    Write-EmpireLog "System Resources:" "INFO" "STATUS"
    Write-EmpireLog "  Memory: $memUsage% used" "INFO" "STATUS"
    Write-EmpireLog "  Disk: $diskUsage% used" "INFO" "STATUS"
    
    # Docker Status
    if (Test-DockerHealth) {
        $dockerVersion = docker --version
        Write-EmpireLog "Docker: $dockerVersion" "SUCCESS" "STATUS"
    }
    
    # Services Status
    Write-EmpireLog "Service Health Check:" "INFO" "STATUS"
    
    $coreServices = @("redis", "qdrant", "reflexshell", "legion", "comms", "gateway")
    foreach ($service in $coreServices) {
        $health = Get-ServiceHealth -ServiceName $service
        if ($health) {
            $status = if ($health.Health -eq "HEALTHY") { "SUCCESS" } else { "ERROR" }
            Write-EmpireLog "  $($service.ToUpper()): $($health.Health) ($($health.Status))" $status "STATUS"
        }
    }
    
    # Network Status
    Write-EmpireLog "Network Status:" "INFO" "STATUS"
    $networks = docker network ls --format "{{.Name}}" | Where-Object { $_ -like "empire-*" }
    foreach ($network in $networks) {
        Write-EmpireLog "  $network: ACTIVE" "SUCCESS" "STATUS"
    }
}

# ============================================================================
# BACKUP FUNCTIONS
# ============================================================================
function Backup-EmpireData {
    Write-EmpireLog "Starting Empire data backup..." "INFO" "BACKUP"
    
    $backupTimestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupPath = "$BACKUP_DIR/empire-backup-$backupTimestamp"
    
    New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
    
    try {
        # Backup Redis data
        Write-EmpireLog "Backing up Redis data..." "INFO" "BACKUP"
        docker exec empire-redis redis-cli BGSAVE
        Start-Sleep -Seconds 5
        docker cp empire-redis:/data/dump.rdb "$backupPath/redis-dump.rdb"
        
        # Backup Qdrant collections
        Write-EmpireLog "Backing up Qdrant collections..." "INFO" "BACKUP"
        New-Item -ItemType Directory -Path "$backupPath/qdrant" -Force | Out-Null
        docker exec empire-qdrant tar -czf /tmp/qdrant-backup.tar.gz /qdrant/storage
        docker cp empire-qdrant:/tmp/qdrant-backup.tar.gz "$backupPath/qdrant/collections.tar.gz"
        
        # Backup configuration files
        Write-EmpireLog "Backing up configuration files..." "INFO" "BACKUP"
        Copy-Item -Path "docker-compose.unified-empire.yml" -Destination "$backupPath/"
        Copy-Item -Path ".env.empire" -Destination "$backupPath/" -ErrorAction SilentlyContinue
        Copy-Item -Path "$CONFIG_DIR/*" -Destination "$backupPath/config/" -Recurse -ErrorAction SilentlyContinue
        
        # Backup logs
        Write-EmpireLog "Backing up logs..." "INFO" "BACKUP"
        Copy-Item -Path "$LOGS_DIR/*" -Destination "$backupPath/logs/" -Recurse -ErrorAction SilentlyContinue
        
        # Create backup manifest
        $manifest = @{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            BackupType = "Full Empire Backup"
            Components = @("Redis", "Qdrant", "Configuration", "Logs")
            BackupSize = (Get-ChildItem -Path $backupPath -Recurse | Measure-Object -Property Length -Sum).Sum
        }
        
        $manifest | ConvertTo-Json -Depth 3 | Set-Content -Path "$backupPath/manifest.json"
        
        Write-EmpireLog "Backup completed successfully: $backupPath" "SUCCESS" "BACKUP"
        Write-EmpireLog "Backup size: $([math]::Round($manifest.BackupSize / 1MB, 2)) MB" "INFO" "BACKUP"
        
    }
    catch {
        Write-EmpireLog "Backup failed: $($_.Exception.Message)" "ERROR" "BACKUP"
        throw
    }
}

# ============================================================================
# SECURITY FUNCTIONS
# ============================================================================
function Start-SecurityScan {
    Write-EmpireLog "Starting comprehensive security scan..." "INFO" "SECURITY"
    
    try {
        # Docker security scan
        Write-EmpireLog "Scanning Docker images for vulnerabilities..." "INFO" "SECURITY"
        
        $images = docker images --format "{{.Repository}}:{{.Tag}}" | Where-Object { $_ -like "sovereignty-empire/*" }
        
        foreach ($image in $images) {
            Write-EmpireLog "Scanning $image..." "INFO" "SECURITY"
            
            # Use docker scan if available, otherwise use basic checks
            try {
                $scanResult = docker scan $image 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-EmpireLog "Security scan completed for $image" "SUCCESS" "SECURITY"
                } else {
                    Write-EmpireLog "Security scan found issues in $image" "WARN" "SECURITY"
                }
            }
            catch {
                Write-EmpireLog "Docker scan not available, performing basic checks..." "INFO" "SECURITY"
            }
        }
        
        # Network security check
        Write-EmpireLog "Checking network security..." "INFO" "SECURITY"
        
        $exposedPorts = docker ps --format "{{.Names}}:{{.Ports}}" | Where-Object { $_ -match "0\.0\.0\.0" }
        
        if ($exposedPorts) {
            Write-EmpireLog "Found externally exposed services:" "WARN" "SECURITY"
            $exposedPorts | ForEach-Object {
                Write-EmpireLog "  $_" "WARN" "SECURITY"
            }
        } else {
            Write-EmpireLog "No external port exposure detected" "SUCCESS" "SECURITY"
        }
        
        # Container privilege check
        Write-EmpireLog "Checking container privileges..." "INFO" "SECURITY"
        
        $privilegedContainers = docker ps --format "{{.Names}}" | ForEach-Object {
            $inspect = docker inspect $_ --format "{{.HostConfig.Privileged}}"
            if ($inspect -eq "true") {
                $_
            }
        }
        
        if ($privilegedContainers) {
            Write-EmpireLog "Found privileged containers:" "WARN" "SECURITY"
            $privilegedContainers | ForEach-Object {
                Write-EmpireLog "  $_" "WARN" "SECURITY"
            }
        } else {
            Write-EmpireLog "No privileged containers detected" "SUCCESS" "SECURITY"
        }
        
        # File system security
        Write-EmpireLog "Checking file system security..." "INFO" "SECURITY"
        
        $sensitiveFiles = @(".env.empire", "config/*", "logs/*")
        foreach ($pattern in $sensitiveFiles) {
            $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
            $files | ForEach-Object {
                $acl = Get-Acl $_.FullName
                $worldReadable = $acl.Access | Where-Object { $_.IdentityReference -eq "Everyone" -and $_.FileSystemRights -match "Read" }
                
                if ($worldReadable) {
                    Write-EmpireLog "World-readable sensitive file: $($_.FullName)" "WARN" "SECURITY"
                }
            }
        }
        
        Write-EmpireLog "Security scan completed" "SUCCESS" "SECURITY"
        
    }
    catch {
        Write-EmpireLog "Security scan failed: $($_.Exception.Message)" "ERROR" "SECURITY"
        throw
    }
}

# ============================================================================
# MAINTENANCE FUNCTIONS
# ============================================================================
function Stop-SovereignEmpire {
    Write-EmpireLog "Stopping Sovereign Empire..." "INFO" "SHUTDOWN"
    
    try {
        docker-compose -f docker-compose.unified-empire.yml down
        Write-EmpireLog "Empire shutdown completed" "SUCCESS" "SHUTDOWN"
    }
    catch {
        Write-EmpireLog "Shutdown failed: $($_.Exception.Message)" "ERROR" "SHUTDOWN"
        throw
    }
}

function Reset-SovereignEmpire {
    Write-EmpireLog "Resetting Sovereign Empire..." "WARN" "RESET"
    
    if (!$Force) {
        $confirmation = Read-Host "This will destroy all data. Type 'CONFIRM' to proceed"
        if ($confirmation -ne "CONFIRM") {
            Write-EmpireLog "Reset cancelled" "INFO" "RESET"
            return
        }
    }
    
    try {
        # Stop and remove all containers
        docker-compose -f docker-compose.unified-empire.yml down -v --remove-orphans
        
        # Remove custom networks
        @("empire-internal", "empire-secure", "empire-public") | ForEach-Object {
            docker network rm $_ 2>$null
        }
        
        # Clean up images
        docker system prune -f
        
        Write-EmpireLog "Empire reset completed" "SUCCESS" "RESET"
    }
    catch {
        Write-EmpireLog "Reset failed: $($_.Exception.Message)" "ERROR" "RESET"
        throw
    }
}

# ============================================================================
# MAIN EXECUTION LOGIC
# ============================================================================
function Main {
    Write-EmpireLog "=== SOVEREIGN EMPIRE AUTOMATION ===" "INFO" "MAIN"
    Write-EmpireLog "Action: $Action" "INFO" "MAIN"
    Write-EmpireLog "Environment: $Environment" "INFO" "MAIN"
    
    # Check prerequisites
    if (!(Test-DockerHealth)) {
        throw "Docker daemon not available. Please start Docker first."
    }
    
    switch ($Action.ToLower()) {
        "build" {
            Build-EmpireImages
        }
        "deploy" {
            if ($Force) {
                Build-EmpireImages
            }
            Deploy-SovereignEmpire
            
            if ($Monitor) {
                Start-EmpireMonitoring
            }
        }
        "status" {
            Show-EmpireStatus
        }
        "monitor" {
            Start-EmpireMonitoring
            Write-EmpireLog "Monitoring started. Press Ctrl+C to stop." "INFO" "MAIN"
            try {
                while ($true) {
                    Start-Sleep -Seconds 5
                }
            }
            catch [System.Management.Automation.PipelineStoppedException] {
                Write-EmpireLog "Monitoring stopped by user" "INFO" "MAIN"
            }
        }
        "backup" {
            Backup-EmpireData
        }
        "security" {
            Start-SecurityScan
        }
        "stop" {
            Stop-SovereignEmpire
        }
        "reset" {
            Reset-SovereignEmpire
        }
        "full" {
            Build-EmpireImages
            Deploy-SovereignEmpire
            Start-SecurityScan
            Backup-EmpireData
            Start-EmpireMonitoring
        }
        default {
            Write-EmpireLog "Unknown action: $Action" "ERROR" "MAIN"
            Write-Host @"

SOVEREIGN EMPIRE AUTOMATION COMMANDS:

  build     - Build all Docker images
  deploy    - Deploy the complete empire infrastructure
  status    - Show current empire status
  monitor   - Start real-time monitoring
  backup    - Create full data backup
  security  - Run comprehensive security scan
  stop      - Stop all empire services
  reset     - Complete reset (destroys all data)
  full      - Complete build, deploy, scan, backup, and monitor

OPTIONS:
  -Force        Force rebuild of images during deploy
  -Monitor      Start monitoring after deploy
  -Backup       Create backup after deploy
  -SecurityScan Run security scan after deploy

EXAMPLES:
  .\automate-sovereign-empire.ps1 deploy -Force -Monitor
  .\automate-sovereign-empire.ps1 full
  .\automate-sovereign-empire.ps1 status
  .\automate-sovereign-empire.ps1 backup

"@
            throw "Invalid action specified"
        }
    }
    
    # Execute additional operations if requested
    if ($Backup -and $Action -eq "deploy") {
        Backup-EmpireData
    }
    
    if ($SecurityScan -and $Action -eq "deploy") {
        Start-SecurityScan
    }
    
    Write-EmpireLog "=== EMPIRE AUTOMATION COMPLETED ===" "SUCCESS" "MAIN"
}

# Execute main function with error handling
try {
    Main
}
catch {
    Write-EmpireLog "FATAL ERROR: $($_.Exception.Message)" "ERROR" "MAIN"
    Write-EmpireLog "Stack Trace: $($_.ScriptStackTrace)" "ERROR" "MAIN"
    exit 1
}