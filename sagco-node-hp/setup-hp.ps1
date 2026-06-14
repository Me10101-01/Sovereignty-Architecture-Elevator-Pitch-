# ============================================================
# SAGCO HP Node — Windows Setup Script (PowerShell)
# Run this in PowerShell as Administrator on the HP
#
# Configures: Claude Code, OpenSSH, Ollama DirectML,
#             Docker Desktop, WSL2, Node.js, Python, Git
# ============================================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "  ══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  SAGCO HP Node — Windows Developer Setup" -ForegroundColor Cyan
Write-Host "  AMD Radeon 740M | 31.1 GB RAM | 932 GB NVMe" -ForegroundColor Cyan
Write-Host "  IP: 192.168.1.98 | attlocal.net (AT&T Ethernet)" -ForegroundColor Cyan
Write-Host "  ══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ── 1. OpenSSH Server (so iPad/other nodes can SSH in) ───────────────────────
Write-Host "  [1/7] Configuring OpenSSH Server..." -ForegroundColor Yellow

$sshd = Get-Service -Name sshd -ErrorAction SilentlyContinue
if ($null -eq $sshd) {
    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
}

Set-Service -Name sshd -StartupType Automatic
Start-Service sshd -ErrorAction SilentlyContinue

# Allow SSH through firewall
New-NetFirewallRule -Name "SAGCO-SSH" -DisplayName "SAGCO SSH" `
    -Enabled True -Direction Inbound -Protocol TCP -Action Allow `
    -LocalPort 22 -ErrorAction SilentlyContinue

Write-Host "  SSH: enabled on port 22 (192.168.1.98:22)" -ForegroundColor Green

# ── 2. Ollama DirectML (AMD GPU on Windows — no ROCm needed) ─────────────────
Write-Host "  [2/7] Configuring Ollama (DirectML for AMD 740M)..." -ForegroundColor Yellow

# Ollama on Windows uses DirectML automatically for AMD GPUs
# Set environment variables for AMD GPU preference
[System.Environment]::SetEnvironmentVariable(
    "OLLAMA_GPU_DRIVER", "directml",
    [System.EnvironmentVariableTarget]::Machine
)
[System.Environment]::SetEnvironmentVariable(
    "OLLAMA_HOST", "0.0.0.0:11434",
    [System.EnvironmentVariableTarget]::Machine
)

# Allow Ollama through firewall for LAN access
New-NetFirewallRule -Name "SAGCO-Ollama" -DisplayName "SAGCO Ollama LAN" `
    -Enabled True -Direction Inbound -Protocol TCP -Action Allow `
    -LocalPort 11434 -ErrorAction SilentlyContinue

Write-Host "  Ollama: port 11434 open on LAN (192.168.1.98:11434)" -ForegroundColor Green

# ── 3. Claude Code — dangerous mode config ────────────────────────────────────
Write-Host "  [3/7] Configuring Claude Code (developer/dangerous mode)..." -ForegroundColor Yellow

$claudeConfigDir = "$env:USERPROFILE\.claude"
New-Item -ItemType Directory -Force -Path $claudeConfigDir | Out-Null

$settingsJson = @"
{
  "dangerouslySkipPermissions": true,
  "model": "claude-sonnet-4-6",
  "env": {
    "SAGCO_NODE": "hp",
    "SAGCO_NODE_IP": "192.168.1.98",
    "OLLAMA_HOST": "http://localhost:11434",
    "SAGCO_ENV": "sovereign"
  }
}
"@

$settingsJson | Out-File -FilePath "$claudeConfigDir\settings.json" -Encoding utf8
Write-Host "  Claude Code: $claudeConfigDir\settings.json" -ForegroundColor Green
Write-Host "  dangerouslySkipPermissions: true" -ForegroundColor Green

# ── 4. SAGCO node config ──────────────────────────────────────────────────────
Write-Host "  [4/7] Writing SAGCO node config..." -ForegroundColor Yellow

$sagcoDir = "$env:USERPROFILE\.sagco"
New-Item -ItemType Directory -Force -Path $sagcoDir | Out-Null

$nodesJson = @"
{
  "nodes": {
    "hp": { "ip": "192.168.1.98", "ssh_user": "$env:USERNAME", "os": "windows11" },
    "ipad": { "ip": "", "note": "set when known" }
  }
}
"@
$nodesJson | Out-File -FilePath "$sagcoDir\nodes.json" -Encoding utf8
Write-Host "  SAGCO nodes: $sagcoDir\nodes.json" -ForegroundColor Green

# ── 5. Docker Desktop — expose API for SAGCO ─────────────────────────────────
Write-Host "  [5/7] Docker Desktop config note..." -ForegroundColor Yellow
Write-Host "  In Docker Desktop Settings → General:" -ForegroundColor Gray
Write-Host "    Enable: 'Expose daemon on tcp://localhost:2375'" -ForegroundColor Gray
Write-Host "  (requires manual toggle — Docker Desktop GUI only)" -ForegroundColor Gray
New-NetFirewallRule -Name "SAGCO-Docker" -DisplayName "SAGCO Docker API" `
    -Enabled True -Direction Inbound -Protocol TCP -Action Allow `
    -LocalPort 2375 -ErrorAction SilentlyContinue

# ── 6. AMD GPU driver check ───────────────────────────────────────────────────
Write-Host "  [6/7] AMD Radeon 740M driver info..." -ForegroundColor Yellow
$gpu = Get-WmiObject Win32_VideoController | Where-Object { $_.Name -like "*Radeon*" }
if ($gpu) {
    Write-Host "  GPU:    $($gpu.Name)" -ForegroundColor Green
    Write-Host "  Driver: $($gpu.DriverVersion)" -ForegroundColor Green
    Write-Host "  VRAM:   $([math]::Round($gpu.AdapterRAM/1GB, 2)) GB dedicated" -ForegroundColor Green
}

# ── 7. Final status ───────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  [7/7] HP Node Status" -ForegroundColor Yellow
Write-Host "  ── Services ────────────────────────────────────────"
@(
    @("sshd",    22),
    @("ollama",  11434),
    @("docker",  2375)
) | ForEach-Object {
    $svc = $_[0]; $port = $_[1]
    try {
        $conn = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
        $ok = if ($conn.TcpTestSucceeded) { "✓ OPEN" } else { "✗ CLOSED" }
    } catch { $ok = "? UNKNOWN" }
    Write-Host ("  {0,-10} :{1}  {2}" -f $svc, $port, $ok)
}

Write-Host ""
Write-Host "  ══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  HP Node configured. From iPad / any SAGCO node:" -ForegroundColor Cyan
Write-Host "    sagco node hp set-ip 192.168.1.98" -ForegroundColor White
Write-Host "    sagco node hp probe" -ForegroundColor White
Write-Host "    sagco node hp ollama" -ForegroundColor White
Write-Host "    sagco node hp ssh" -ForegroundColor White
Write-Host "  ══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
