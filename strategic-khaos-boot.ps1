# ╔══════════════════════════════════════════════════════════╗
# ║               strategic-khaos — BOOT EXPLOSION           ║
# ║          8 screens. Zero mercy. DOM_010101 // 2025       ║
# ╚══════════════════════════════════════════════════════════╝

param(
    [switch]$SkipDocker,
    [switch]$SkipVPN,
    [switch]$SkipOllama,
    [switch]$SkipVSCode,
    [switch]$SkipBrowser,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"

# Color output functions
function Write-Stage {
    param([string]$Message)
    Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║ $Message" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "  ✓ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "  → $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "  ✗ $Message" -ForegroundColor Red
}

# ═══════════════════════════════════════════════════════════
# STAGE 1: Start everything that must be alive
# ═══════════════════════════════════════════════════════════

Write-Stage "STAGE 1: Starting critical services"

# Start Docker Desktop
if (-not $SkipDocker) {
    Write-Info "Starting Docker Desktop..."
    $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    
    if (Test-Path $dockerPath) {
        try {
            $dockerProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
            if (-not $dockerProcess) {
                Start-Process $dockerPath -WindowStyle Hidden
                Write-Success "Docker Desktop started"
            } else {
                Write-Success "Docker Desktop already running"
            }
        } catch {
            Write-Error-Custom "Failed to start Docker Desktop: $_"
        }
    } else {
        Write-Error-Custom "Docker Desktop not found at $dockerPath"
    }
} else {
    Write-Info "Skipping Docker Desktop (--SkipDocker flag)"
}

# Start WireGuard VPN swarm
if (-not $SkipVPN) {
    Write-Info "Starting WireGuard VPN swarm..."
    $wgScript = "wg-quick-multi-up.ps1"
    
    if (Test-Path $wgScript) {
        try {
            Start-Process powershell -ArgumentList "-File `"$wgScript`" all" -WindowStyle Hidden -NoNewWindow
            Write-Success "WireGuard VPN swarm initiated"
        } catch {
            Write-Error-Custom "Failed to start WireGuard: $_"
        }
    } else {
        Write-Info "WireGuard script not found: $wgScript (continuing...)"
    }
} else {
    Write-Info "Skipping WireGuard VPN (--SkipVPN flag)"
}

# Start Ollama service
if (-not $SkipOllama) {
    Write-Info "Starting Ollama service..."
    try {
        $ollamaProcess = Get-Process "ollama" -ErrorAction SilentlyContinue
        if (-not $ollamaProcess) {
            Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden -NoNewWindow
            Write-Success "Ollama service started"
        } else {
            Write-Success "Ollama already running"
        }
    } catch {
        Write-Error-Custom "Failed to start Ollama: $_"
    }
} else {
    Write-Info "Skipping Ollama (--SkipOllama flag)"
}

# ═══════════════════════════════════════════════════════════
# STAGE 2: Wait for Docker + WSL2 + k8s to calm down
# ═══════════════════════════════════════════════════════════

Write-Stage "STAGE 2: Waiting for Docker/WSL2/k8s initialization"

if (-not $SkipDocker) {
    Write-Info "Waiting 35 seconds for Docker + WSL2 + k8s..."
    $waitSeconds = 35
    for ($i = 1; $i -le $waitSeconds; $i++) {
        if ($i % 5 -eq 0 -or $i -eq $waitSeconds) {
            Write-Progress -Activity "Waiting for services" -Status "$i/$waitSeconds seconds" -PercentComplete (($i / $waitSeconds) * 100)
        }
        Start-Sleep -Seconds 1
    }
    Write-Progress -Activity "Waiting for services" -Completed
    Write-Success "Docker initialization wait complete"
    
    # Verify Docker is actually ready
    Write-Info "Verifying Docker daemon..."
    try {
        $dockerCheck = docker ps 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker daemon is ready"
        } else {
            Write-Error-Custom "Docker daemon not responding yet"
        }
    } catch {
        Write-Error-Custom "Docker command failed: $_"
    }
}

# ═══════════════════════════════════════════════════════════
# STAGE 3: Bring the cluster up (kind / k3s)
# ═══════════════════════════════════════════════════════════

Write-Stage "STAGE 3: Kubernetes cluster deployment"

if (-not $SkipDocker) {
    # Load Docker images into kind cluster
    Write-Info "Loading Docker images into kind cluster..."
    try {
        $kindOutput = kind load docker-image --name strategic-khaos localregistry/local-all-images:latest 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker images loaded into kind cluster"
        } else {
            Write-Info "Image load skipped or failed (non-critical): $kindOutput"
        }
    } catch {
        Write-Info "Kind image load skipped: $_"
    }
    
    # Apply Kubernetes configurations
    Write-Info "Applying Kubernetes configurations..."
    
    # Try k8s/overlays/dev first (as per problem statement)
    if (Test-Path "k8s/overlays/dev") {
        try {
            kubectl apply -k k8s/overlays/dev 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Kubernetes dev overlay applied"
            } else {
                Write-Info "Dev overlay apply had issues (may not exist)"
            }
        } catch {
            Write-Info "Dev overlay path exists but apply failed: $_"
        }
    }
    
    # Fallback to bootstrap/k8s if overlays don't exist
    if (Test-Path "bootstrap/k8s") {
        try {
            kubectl apply -f bootstrap/k8s/ 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Bootstrap Kubernetes configs applied"
            }
        } catch {
            Write-Info "Bootstrap k8s apply encountered issues: $_"
        }
    }
}

# ═══════════════════════════════════════════════════════════
# STAGE 4: Nuke 8 VS Code windows across all monitors
# ═══════════════════════════════════════════════════════════

Write-Stage "STAGE 4: Launching VS Code workspace explosion"

if (-not $SkipVSCode) {
    Write-Info "Enumerating Docker containers..."
    
    try {
        # Get containers matching the pattern
        $containerNames = docker ps --filter "name=solver" --filter "name=map-server" --filter "name=ollama" --format "{{.Names}}" 2>&1
        
        if ($containerNames -and $LASTEXITCODE -eq 0) {
            $containers = $containerNames -split "`n" | Where-Object { $_ -ne "" }
            
            Write-Info "Found $($containers.Count) matching containers"
            
            foreach ($container in $containers) {
                $containerName = $container.Trim()
                if ($containerName) {
                    Write-Info "Opening VS Code for container: $containerName"
                    try {
                        Start-Process "code" -ArgumentList "--new-window --folder-uri `"vscode-remote://attached-container+$containerName/home/dom`"" -NoNewWindow
                    } catch {
                        Write-Error-Custom "Failed to open VS Code for $containerName"
                    }
                }
            }
            Write-Success "Container VS Code windows launched"
        } else {
            Write-Info "No matching containers found (solver, map-server, ollama)"
        }
    } catch {
        Write-Error-Custom "Failed to enumerate containers: $_"
    }
    
    # Open dedicated project windows
    Write-Info "Opening dedicated project windows..."
    
    $projectPaths = @(
        @{Path="."; Name="Root (strategic-khaos)"},
        @{Path="./map-server"; Name="map-server"},
        @{Path="./agents"; Name="agents"}
    )
    
    foreach ($project in $projectPaths) {
        if (Test-Path $project.Path) {
            try {
                Start-Process "code" -ArgumentList "--new-window `"$($project.Path)`"" -NoNewWindow
                Write-Success "Opened: $($project.Name)"
            } catch {
                Write-Error-Custom "Failed to open $($project.Name)"
            }
        } else {
            Write-Info "$($project.Name) path not found, skipping"
        }
    }
    
    # Extra: Ollama-01 container workspace
    Write-Info "Opening Ollama-01 container workspace..."
    try {
        Start-Process "code" -ArgumentList "--new-window --folder-uri `"vscode-remote://attached-container+ollama-01/usr/src/app`"" -NoNewWindow
        Write-Success "Ollama-01 workspace opened"
    } catch {
        Write-Info "Ollama-01 workspace open failed (container may not exist)"
    }
    
    Write-Success "VS Code workspace explosion complete"
} else {
    Write-Info "Skipping VS Code windows (--SkipVSCode flag)"
}

# ═══════════════════════════════════════════════════════════
# STAGE 5: Open important browser tabs on monitor 8
# ═══════════════════════════════════════════════════════════

Write-Stage "STAGE 5: Browser interface launch"

if (-not $SkipBrowser) {
    Write-Info "Opening browser tabs..."
    
    $urls = @(
        "http://localhost:3000",              # map-server live
        "http://localhost:11434",             # Ollama
        "https://github.com/Me10101-01/strategic-khaos",
        "http://localhost:8080"               # k9s web or lens
    )
    
    try {
        # Try Chrome first
        $chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
        if (Test-Path $chromePath) {
            Start-Process $chromePath -ArgumentList ($urls -join " ")
            Write-Success "Browser tabs opened in Chrome"
        } 
        # Fallback to Edge
        elseif (Get-Command "msedge" -ErrorAction SilentlyContinue) {
            Start-Process "msedge" -ArgumentList ($urls -join " ")
            Write-Success "Browser tabs opened in Edge"
        }
        # Fallback to default browser
        else {
            foreach ($url in $urls) {
                Start-Process $url
            }
            Write-Success "Browser tabs opened in default browser"
        }
    } catch {
        Write-Error-Custom "Failed to open browser tabs: $_"
    }
} else {
    Write-Info "Skipping browser tabs (--SkipBrowser flag)"
}

# ═══════════════════════════════════════════════════════════
# STAGE 6: Final chaos touch — play the ascension sound
# ═══════════════════════════════════════════════════════════

Write-Stage "STAGE 6: Ascension sequence"

Write-Info "Playing notification sound..."
try {
    $soundPath = "C:\Windows\Media\notify.wav"
    if (Test-Path $soundPath) {
        $player = New-Object Media.SoundPlayer $soundPath
        $player.PlaySync()
        Write-Success "Ascension sound played"
    } else {
        # Fallback to system beep
        [Console]::Beep(800, 200)
        [Console]::Beep(1000, 200)
        [Console]::Beep(1200, 400)
        Write-Success "Ascension beep sequence complete"
    }
} catch {
    Write-Info "Sound playback skipped: $_"
}

# ═══════════════════════════════════════════════════════════
# FINAL STATUS
# ═══════════════════════════════════════════════════════════

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║                                                           ║" -ForegroundColor Magenta
Write-Host "║      strategic-khaos online. The swarm is awake.         ║" -ForegroundColor Magenta
Write-Host "║                                                           ║" -ForegroundColor Magenta
Write-Host "║      DOM_010101 // 2025 - 8 SCREENS OPERATIONAL          ║" -ForegroundColor Magenta
Write-Host "║                                                           ║" -ForegroundColor Magenta
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

# Show quick status
Write-Info "Quick Status Check:"
Write-Host ""
Write-Host "  Services:" -ForegroundColor Cyan
try {
    $dockerRunning = (docker ps --format "table {{.Names}}" 2>&1 | Measure-Object -Line).Lines - 1
    Write-Host "    • Docker containers: $dockerRunning running" -ForegroundColor White
} catch {
    Write-Host "    • Docker: Status unknown" -ForegroundColor Gray
}

Write-Host ""
Write-Host "  Interfaces:" -ForegroundColor Cyan
Write-Host "    • Map Server:     http://localhost:3000" -ForegroundColor White
Write-Host "    • Ollama:         http://localhost:11434" -ForegroundColor White
Write-Host "    • Traefik/k9s:    http://localhost:8080" -ForegroundColor White
Write-Host "    • GitHub:         https://github.com/Me10101-01/strategic-khaos" -ForegroundColor White

Write-Host ""
Write-Host "Ready for strategic chaos. 🔥" -ForegroundColor Green
Write-Host ""
