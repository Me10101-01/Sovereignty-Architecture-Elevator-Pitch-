# SAGCO-FUZZ-IMPOSSIBLE-001 — Live Attempt Log

## Fleet State at Attempt Start

```
Lyra (Windows/WSL2)
  sagco-daemon: RUNNING
  nodes mapped: 33,791
  chain: VERIFIED

HP OmniDesk
  BIOS: OPEN
  Network boot: ENABLED
  IPv4+IPv6 UEFI: READY
  Status: waiting for PXE response

Pi 5 (8GB)
  Light: GREEN
  Network: CONNECTED
  Role: PXE server candidate

Z Fold (192.168.1.89)
  SAGCO-GTA: RUNNING
  sagco-daemon: ACTIVE
  Role: mobile node / command terminal
```

---

## The Landmine — WSL2 Networking

**Problem:** WSL2 default IP is 172.x.x.x (NATed). HP OmniDesk can't see it.

**Fix A — Mirrored Networking (Windows 11 22H2+):**

```powershell
# On Lyra Windows side:
# Edit C:\Users\<you>\.wslconfig
[wsl2]
networkingMode=mirrored
```

Then:
```powershell
wsl --shutdown
# reopen WSL2, check ip addr show eth0 → should be 192.168.1.x
```

**Fix B — Use Pi 5 (simpler, recommended):**
```bash
ssh pi@<pi5-ip>
sudo bash sagco-true/worlds/pxe/pi5_pxe.sh
```

---

## Step by Step (Once IP is Known)

### On Lyra WSL2 (or Pi 5):

```bash
# 1. Find your IP
ip addr show eth0
# Look for: inet 192.168.1.X/24

# 2. Run bootstrap
sudo bash sagco-true/worlds/pxe/pxe_bootstrap.sh

# 3. Watch for HP to call home
journalctl -fu dnsmasq | grep -E "pxe|DHCP|boot"
# OR
tail -f /var/log/syslog | grep -iE "pxe|tftp"
```

### On HP OmniDesk BIOS:
```
Boot Options → Boot Order
  [1] Network Adapter / PXE IPv4
  [2] Network Adapter / PXE IPv6
  [3] Local SSD (escape hatch)
Save → Reboot
```

### Expected output on the PXE server when HP calls:
```
dnsmasq-dhcp: DHCPDISCOVER from aa:bb:cc:dd:ee:ff via eth0
dnsmasq-dhcp: DHCPOFFER on 192.168.1.XX to hp-omnidesk via eth0
dnsmasq-tftp: sent /srv/tftp/efi64/grub.efi to 192.168.1.XX
dnsmasq-tftp: sent /srv/tftp/grub/grub.cfg to 192.168.1.XX
```

### HP screen should show:
```
SAGCO Node Boot Menu
HP OmniDesk — Network Boot

> SAGCO Node — Alpine Linux (UEFI Netboot)
  SAGCO Node — Shell + SAGCO daemon (NFS root)
  Boot from local disk (escape hatch)
```

---

## After Boot — Register HP as SAGCO Node

```bash
# From Lyra or Z Fold:
python3 -c "
from sagco_true.language.vm.vm import run_file
vm = run_file('sagco-true/worlds/pxe/hp_omnidesk_node.sagco')
print('Fleet nodes:', {k: v for k, v in vm.memory.items() if k.startswith('fleet.')})
"
```

---

## Fleet Graph After Success

```
Lyra (WSL2)          ←→  sagco-daemon  ←→  33,791 nodes
  ↓ PXE serves
HP OmniDesk           ←→  SAGCO node    ←→  boots Alpine
  ↑ same LAN
Pi 5 (edge)           ←→  PXE server    ←→  green light
  ↑ same LAN
Z Fold (192.168.1.89) ←→  SAGCO-GTA     ←→  mobile command terminal
```

```
Fleet: 4 nodes
Status: ATTEMPTING → TARGET: VERIFIED
```
