# Strategic Khaos Boot - Quick Reference

## One-Line Boot
```powershell
.\strategic-khaos-boot.ps1
```

## Common Scenarios

### Full Fresh Boot
```powershell
# Everything from scratch
.\strategic-khaos-boot.ps1
```

### Quick Restart
```powershell
# Services already running, just reopen workspaces
.\strategic-khaos-boot.ps1 -SkipDocker -SkipVPN -SkipOllama
```

### Infrastructure Only
```powershell
# Start services, skip IDE and browser
.\strategic-khaos-boot.ps1 -SkipVSCode -SkipBrowser
```

### Developer Focus
```powershell
# Skip VPN and browser, focus on coding
.\strategic-khaos-boot.ps1 -SkipVPN -SkipBrowser
```

### Minimal Dev Setup
```powershell
# Just workspaces, no infrastructure changes
.\strategic-khaos-boot.ps1 -SkipDocker -SkipVPN -SkipOllama -SkipBrowser
```

## Flags Reference

| Flag | Description |
|------|-------------|
| `-SkipDocker` | Don't start Docker Desktop |
| `-SkipVPN` | Don't start WireGuard VPN |
| `-SkipOllama` | Don't start Ollama service |
| `-SkipVSCode` | Don't open VS Code windows |
| `-SkipBrowser` | Don't open browser tabs |
| `-Verbose` | Enable verbose output (future) |

## Expected Services

After boot, check these are running:

```powershell
# Docker containers
docker ps

# Expected to see:
# - solver*
# - map-server*
# - ollama*
```

## Service URLs

| Service | URL |
|---------|-----|
| Map Server | http://localhost:3000 |
| Ollama API | http://localhost:11434 |
| Traefik/k9s | http://localhost:8080 |
| GitHub | https://github.com/Me10101-01/strategic-khaos |

## Troubleshooting

### Docker not starting?
```powershell
# Check if Docker Desktop is installed
Test-Path "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Manually start
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Wait and retry
Start-Sleep 30
docker ps
```

### VS Code not opening?
```powershell
# Check VS Code is in PATH
code --version

# Check containers exist
docker ps --format "{{.Names}}"
```

### Kubernetes not deploying?
```powershell
# Check kubectl works
kubectl cluster-info

# Check kind cluster
kind get clusters

# Create if missing
kind create cluster --name strategic-khaos
```

## Full Documentation

See [STRATEGIC_KHAOS_BOOT.md](../STRATEGIC_KHAOS_BOOT.md) for complete documentation.

---

**8 screens. Zero mercy. DOM_010101 // 2025** 🔥
