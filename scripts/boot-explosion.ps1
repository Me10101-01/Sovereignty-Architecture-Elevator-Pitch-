# ╔══════════════════════════════════════════════════════════╗
# ║               strategic-khaos — BOOT EXPLOSION           ║
# ║          8 screens. Zero mercy. DOM_010101 // 2025       ║
# ╚══════════════════════════════════════════════════════════╝

# 1. Start everything that must be alive
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
Start-Process "wg-quick-multi-up.ps1" -ArgumentList "all"   # your WireGuard swarm
Start-Process ollama serve --nowait

# 2. Wait for Docker + WSL2 + k8s to calm down
Start-Sleep -Seconds 35

# 3. Bring the cluster up (kind / k3s / whatever you're running)
kind load docker-image --name strategic-khaos localregistry/local-all-images:latest 2>$null
kubectl apply -k k8s/overlays/dev

# 4. Nuke 8 VS Code windows across all monitors, each attached to something beautiful
$containers = docker ps --filter "name=solver|map-server|ollama" --format "{{.Names}}"

foreach ($c in $containers) {
    code --new-window --folder-uri "vscode-remote://attached-container+$c/home/dom"
}

# Extra dedicated windows
code --new-window .  # root of strategic-khaos
code --new-window ./map-server
code --new-window ./agents
code --new-window --folder-uri "vscode-remote://attached-container+ollama-01/usr/src/app"

# 5. Open the important browser tabs on monitor 8
Start-Process "chrome.exe" -ArgumentList `
  "http://localhost:3000",              # map-server live
  "http://localhost:11434",             # Ollama
  "https://github.com/Me10101-01/strategic-khaos",
  "http://localhost:8080"               # k9s web or lens or whatever you use

# 6. Final chaos touch — play the ascension sound
(Start-Process "powershell.exe" -ArgumentList "-c (New-Object Media.SoundPlayer 'C:\Windows\Media\notify.wav').PlaySync()") | Out-Null

Write-Host "strategic-khaos online. The swarm is awake." -ForegroundColor Cyan
