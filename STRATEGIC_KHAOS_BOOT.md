# Strategic Khaos Boot Explosion

**8 screens. Zero mercy. DOM_010101 // 2025**

## Overview

The `strategic-khaos-boot.ps1` script is a comprehensive Windows PowerShell automation tool designed to orchestrate the complete startup sequence of the Strategic Khaos development environment. This script transforms a cold boot into a fully operational multi-monitor development workspace in under 2 minutes.

## Features

### 🚀 Automated Service Startup
- **Docker Desktop**: Launches and waits for Docker daemon readiness
- **WireGuard VPN**: Activates multi-configuration VPN swarm
- **Ollama**: Starts local LLM inference server
- **Kubernetes**: Deploys cluster configurations via kind

### 🖥️ Multi-Monitor Workspace Setup
- **8 VS Code Windows**: Automatically opens attached to running containers
- **Project Workspaces**: Opens dedicated windows for map-server, agents, and root
- **Browser Tabs**: Launches all critical service interfaces
  - Map server (localhost:3000)
  - Ollama API (localhost:11434)
  - GitHub repository
  - Kubernetes dashboard (localhost:8080)

### 🎯 Intelligent Orchestration
- **Sequential Stages**: Organized boot sequence with proper wait times
- **Error Handling**: Graceful degradation when components are unavailable
- **Status Feedback**: Real-time progress updates with color-coded output
- **Validation**: Checks Docker daemon and service readiness

## Usage

### Basic Usage
```powershell
# Full boot sequence
.\strategic-khaos-boot.ps1

# Skip specific components
.\strategic-khaos-boot.ps1 -SkipDocker
.\strategic-khaos-boot.ps1 -SkipVPN
.\strategic-khaos-boot.ps1 -SkipOllama
.\strategic-khaos-boot.ps1 -SkipVSCode
.\strategic-khaos-boot.ps1 -SkipBrowser

# Combine flags
.\strategic-khaos-boot.ps1 -SkipVPN -SkipBrowser
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `-SkipDocker` | Skip Docker Desktop startup |
| `-SkipVPN` | Skip WireGuard VPN initialization |
| `-SkipOllama` | Skip Ollama service startup |
| `-SkipVSCode` | Skip VS Code window launches |
| `-SkipBrowser` | Skip browser tab opening |
| `-Verbose` | Enable verbose output (future use) |

## Prerequisites

### Required Software
- **Windows 10/11** (PowerShell 5.1 or later)
- **Docker Desktop** installed at `C:\Program Files\Docker\Docker\Docker Desktop.exe`
- **Visual Studio Code** with Remote-Containers extension
- **kubectl** for Kubernetes management
- **kind** (Kubernetes in Docker) cluster named `strategic-khaos`

### Optional Software
- **WireGuard** with `wg-quick-multi-up.ps1` script
- **Ollama** LLM inference server
- **Google Chrome** or Microsoft Edge

### Directory Structure
```
strategic-khaos/
├── strategic-khaos-boot.ps1    # This script
├── bootstrap/k8s/              # Kubernetes configs
│   ├── bot-deployment.yaml
│   ├── gateway-deployment.yaml
│   └── ...
├── map-server/                 # Map server project
├── agents/                     # Agents project
└── wg-quick-multi-up.ps1       # Optional VPN script
```

## Boot Sequence

### Stage 1: Service Initialization (0-5s)
- Start Docker Desktop (if not running)
- Start WireGuard VPN swarm
- Start Ollama inference server

### Stage 2: Stabilization (5-40s)
- Wait 35 seconds for Docker/WSL2/Kubernetes initialization
- Verify Docker daemon responsiveness
- Ensure Kubernetes API is available

### Stage 3: Cluster Deployment (40-60s)
- Load Docker images into kind cluster
- Apply Kubernetes configurations from:
  - `k8s/overlays/dev/` (development overlay)
  - `bootstrap/k8s/` (fallback)

### Stage 4: Workspace Explosion (60-90s)
- Enumerate running Docker containers
- Open VS Code windows for:
  - Containers matching: `solver`, `map-server`, `ollama`
  - Root project directory
  - map-server subdirectory
  - agents subdirectory
  - ollama-01 container workspace

### Stage 5: Browser Launch (90-100s)
- Open tabs for all service interfaces
- Prefer Chrome, fallback to Edge, then default browser

### Stage 6: Notification (100-105s)
- Play ascension notification sound
- Display completion status
- Show quick service overview

## Container Naming Convention

The script automatically discovers containers with these patterns:
- `*solver*` - Solver service containers
- `*map-server*` - Map server containers
- `*ollama*` - Ollama inference containers

Each discovered container gets its own VS Code window attached to `/home/dom` workspace.

## Troubleshooting

### Docker Desktop Not Starting
```powershell
# Check if Docker is installed
Test-Path "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Manually start Docker
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

### Kubernetes Apply Fails
```powershell
# Verify kubectl is configured
kubectl cluster-info

# Check kind cluster exists
kind get clusters

# Create cluster if needed
kind create cluster --name strategic-khaos
```

### VS Code Windows Not Opening
```powershell
# Verify VS Code is in PATH
code --version

# Check Docker containers are running
docker ps --format "table {{.Names}}\t{{.Status}}"

# Manually open a container
code --new-window --folder-uri "vscode-remote://attached-container+CONTAINER_NAME/home/dom"
```

### WireGuard Script Not Found
The script will continue without error if `wg-quick-multi-up.ps1` is not present. This is optional infrastructure.

## Customization

### Change Docker Path
Edit line 49:
```powershell
$dockerPath = "C:\Your\Custom\Path\Docker Desktop.exe"
```

### Modify Wait Time
Edit line 111:
```powershell
$waitSeconds = 35  # Adjust based on your system
```

### Add/Remove Browser URLs
Edit lines 285-290:
```powershell
$urls = @(
    "http://localhost:3000",
    "http://localhost:11434",
    "https://github.com/YOUR-USERNAME/YOUR-REPO",
    "http://localhost:8080",
    "http://localhost:9090"  # Add more URLs
)
```

### Change Container Patterns
Edit line 216:
```powershell
$containerNames = docker ps --filter "name=YOUR-PATTERN" --format "{{.Names}}"
```

## Performance Tips

### Fast Boot (Skip Components)
```powershell
# If services already running
.\strategic-khaos-boot.ps1 -SkipDocker -SkipVPN -SkipOllama
```

### Minimal Boot (Development Focus)
```powershell
# Just open workspaces, skip infrastructure
.\strategic-khaos-boot.ps1 -SkipDocker -SkipVPN -SkipOllama -SkipBrowser
```

### Infrastructure Only
```powershell
# Start services, skip IDE and browser
.\strategic-khaos-boot.ps1 -SkipVSCode -SkipBrowser
```

## Integration

### Startup Shortcut
Create a desktop shortcut:
```powershell
Target: powershell.exe -ExecutionPolicy Bypass -File "C:\path\to\strategic-khaos-boot.ps1"
Start in: C:\path\to\strategic-khaos
```

### Windows Task Scheduler
Schedule boot on login:
```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -File C:\path\to\strategic-khaos-boot.ps1"
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName "StrategicKhaosBoot" -Action $action -Trigger $trigger
```

### Custom Launch Script
Create `quick-boot.ps1`:
```powershell
# Your custom pre-boot logic
Write-Host "Custom initialization..."

# Run main boot
& .\strategic-khaos-boot.ps1 -SkipVPN

# Your custom post-boot logic
Write-Host "Opening additional tools..."
```

## Architecture

The script follows a **stage-gate pattern** where each stage must complete (or gracefully fail) before proceeding:

```
STAGE 1: Services     → STAGE 2: Wait         → STAGE 3: K8s
(Docker, VPN, Ollama)   (Docker/WSL2/k8s)      (kind, kubectl)
                                                      ↓
STAGE 6: Notify    ← STAGE 5: Browser    ← STAGE 4: Workspaces
(Sound, Status)      (Chrome, URLs)        (VS Code, Containers)
```

### Error Philosophy
- **Non-blocking**: Missing components don't halt execution
- **Informative**: Clear status messages for each operation
- **Graceful**: Fallback options for critical operations
- **Resilient**: Continues even when individual steps fail

## Related Files

- `start-cloudos.ps1` - Alternative CloudOS-focused startup
- `start-desktop.sh` - Linux/WSL equivalent script
- `launch-recon.sh` - Recon service launcher
- `bootstrap/k8s/*.yaml` - Kubernetes deployment configs
- `docker-compose*.yml` - Docker Compose configurations

## Security Notes

### Execution Policy
You may need to allow script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Container Access
The script assumes:
- Container paths: `/home/dom`
- Remote-SSH/Containers extension configured
- Docker socket access available

### VPN Security
WireGuard configuration is external and should be secured separately.

## Support

For issues or enhancements:
1. Check the troubleshooting section
2. Review related documentation (BOOT_RECON.md)
3. Verify prerequisites are installed
4. Open an issue on GitHub

## License

Part of the Strategic Khaos Sovereignty Architecture project.
See LICENSE file in repository root.

---

**Built for strategic chaos. 🔥**

*DOM_010101 // 2025*
