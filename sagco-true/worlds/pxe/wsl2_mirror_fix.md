# WSL2 Mirrored Networking Fix
# The problem: WSL2 default networking is NATed.
# Lyra's WSL2 gets IP 172.x.x.x — invisible to LAN devices.
# HP OmniDesk can't reach it for PXE.
#
# The fix: Enable mirrored networking so WSL2 shares Lyra's 192.168.1.x IP.
# Requires: Windows 11 22H2+ with WSL2 2.0+

## Step 1 — Check your WSL2 version (run in PowerShell on Lyra)

```powershell
wsl --version
# Must show: WSL version 2.0.0 or higher
```

## Step 2 — Enable mirrored networking

Create or edit `%USERPROFILE%\.wslconfig` on Windows (Lyra):

```ini
[wsl2]
networkingMode=mirrored
dnsTunneling=true
firewall=true
autoProxy=true
```

File location: `C:\Users\<YourUsername>\.wslconfig`

## Step 3 — Restart WSL2

```powershell
# In PowerShell on Lyra (Windows side):
wsl --shutdown
# Wait 8 seconds, then reopen WSL2
wsl
```

## Step 4 — Verify

```bash
# Inside WSL2 after restart:
ip addr show eth0
# Should now show: 192.168.1.x  (matching Lyra's Windows IP)
ping 192.168.1.89
# Should reach Z Fold
```

## If WSL2 version is too old

```powershell
# Upgrade WSL2:
wsl --update
wsl --shutdown
```

## Alternative: Use Pi 5 as PXE server

If mirrored networking doesn't work, the Pi 5 is ALREADY on the physical LAN.
Pi 5 is the better PXE server anyway — it's always on, no NAT issues.

```bash
# On Pi 5 (SSH in from Z Fold or Lyra):
ssh pi@<pi5-ip>
sudo bash sagco-true/worlds/pxe/pi5_pxe.sh
```

## Verify fix worked

```bash
# WSL2: after mirrored networking
ip addr show eth0
# → inet 192.168.1.X/24  ← must match your LAN subnet

# Then check HP can reach it (run from Windows Lyra):
ping <WSL2-ip>
# Should respond

# Watch PXE requests in WSL2:
sudo journalctl -fu dnsmasq 2>/dev/null || sudo tail -f /var/log/syslog | grep -i "dnsmasq\|tftp\|pxe"
```
