# Hypervisor Setup Guide
## KhaosOS Virtual Machine Infrastructure

This guide provides instructions for setting up the KhaosOS hypervisor layer with three virtual machines: Kali Linux, Parrot OS, and KhaosOS itself.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Hypervisor Selection](#hypervisor-selection)
3. [VirtualBox Setup (Development)](#virtualbox-setup)
4. [Proxmox VE Setup (Production)](#proxmox-ve-setup)
5. [QEMU/KVM Setup (Advanced)](#qemukvm-setup)
6. [VM Configuration](#vm-configuration)
7. [Network Configuration](#network-configuration)
8. [Security Hardening](#security-hardening)

---

## Prerequisites

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores (with VT-x/AMD-V) |
| RAM | 16 GB | 32+ GB |
| Storage | 256 GB SSD | 1 TB NVMe SSD |
| GPU | Integrated | NVIDIA RTX 4090 (for AI) |
| Network | 1 Gbps | 10 Gbps |

### Software Requirements

- Host OS: Windows 10/11, macOS, or Linux
- Virtualization enabled in BIOS/UEFI
- Latest hypervisor software (see sections below)

---

## Hypervisor Selection

### Comparison Matrix

| Feature | VirtualBox | Proxmox VE | QEMU/KVM |
|---------|-----------|------------|----------|
| **Type** | Type 2 | Type 1 | Type 1 |
| **Cost** | Free | Free | Free |
| **Performance** | Good | Excellent | Excellent |
| **GPU Passthrough** | Limited | Yes | Yes |
| **Ease of Setup** | Easy | Medium | Hard |
| **Use Case** | Development | Production Server | Advanced Users |

### Recommendation

- **Development/Testing:** VirtualBox
- **Production Server:** Proxmox VE
- **KhaosOS Native:** QEMU/KVM with GPU passthrough

---

## VirtualBox Setup

### Installation

#### Windows/macOS
```bash
# Download from https://www.virtualbox.org/
# Install with default options
# Enable extension pack for USB 3.0, RDP, etc.
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install virtualbox virtualbox-ext-pack
```

#### Linux (Fedora/RHEL)
```bash
sudo dnf install VirtualBox
```

### Create Virtual Network

```bash
# Create host-only network for VM communication
VBoxManage hostonlyif create
VBoxManage hostonlyif ipconfig vboxnet0 --ip 192.168.56.1 --netmask 255.255.255.0
```

### VM Creation Scripts

See `scripts/vm-setup/virtualbox/` for automated VM creation scripts.

---

## Proxmox VE Setup

### Installation

1. **Download Proxmox VE ISO**
   ```bash
   wget https://www.proxmox.com/en/downloads/category/iso-images-pve
   ```

2. **Create Bootable USB**
   ```bash
   # Linux
   sudo dd if=proxmox-ve_*.iso of=/dev/sdX bs=1M status=progress
   
   # macOS
   sudo dd if=proxmox-ve_*.iso of=/dev/rdiskX bs=1m
   
   # Windows - use Rufus or balenaEtcher
   ```

3. **Install on Dedicated Hardware**
   - Boot from USB
   - Follow installation wizard
   - Set static IP for management interface
   - Note root password

4. **Access Web UI**
   ```
   https://<proxmox-ip>:8006
   Login: root
   Password: <set during install>
   ```

### Configure Storage

```bash
# SSH into Proxmox
ssh root@<proxmox-ip>

# Create ZFS pool (recommended)
zpool create -f tank /dev/sda /dev/sdb  # RAID 1 example

# Or use LVM
pvcreate /dev/sda
vgcreate pve /dev/sda
lvcreate -L 500G -n vm-storage pve
```

### Network Configuration

```bash
# Edit /etc/network/interfaces
auto vmbr0
iface vmbr0 inet static
    address 10.0.0.1/24
    bridge-ports none
    bridge-stp off
    bridge-fd 0
    # Internal network for VMs

# Restart networking
systemctl restart networking
```

---

## QEMU/KVM Setup

### Installation (Linux)

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager
```

#### Fedora/RHEL
```bash
sudo dnf install @virtualization
```

#### Arch Linux
```bash
sudo pacman -S qemu libvirt virt-manager
```

### Enable and Start Services

```bash
sudo systemctl enable libvirtd
sudo systemctl start libvirtd

# Add user to libvirt group
sudo usermod -aG libvirt $USER
sudo usermod -aG kvm $USER

# Re-login for group changes to take effect
```

### GPU Passthrough (Advanced)

#### 1. Enable IOMMU in BIOS

- Intel: VT-d
- AMD: AMD-Vi

#### 2. Enable IOMMU in Kernel

Edit `/etc/default/grub`:
```bash
# Intel
GRUB_CMDLINE_LINUX_DEFAULT="quiet intel_iommu=on iommu=pt"

# AMD
GRUB_CMDLINE_LINUX_DEFAULT="quiet amd_iommu=on iommu=pt"
```

Update GRUB:
```bash
sudo update-grub  # Ubuntu/Debian
sudo grub2-mkconfig -o /boot/grub2/grub.cfg  # Fedora/RHEL
```

#### 3. Configure VFIO

```bash
# Find GPU PCI IDs
lspci -nn | grep -i nvidia

# Example output: 01:00.0 VGA compatible controller [0300]: NVIDIA Corporation ...

# Bind GPU to VFIO driver
echo "options vfio-pci ids=10de:XXXX,10de:YYYY" | sudo tee /etc/modprobe.d/vfio.conf
sudo update-initramfs -u
```

#### 4. Reboot and Verify

```bash
sudo reboot

# After reboot, check IOMMU groups
./scripts/check-iommu.sh
```

---

## VM Configuration

### VM1: Kali Linux (Red Team Operations)

| Parameter | Value |
|-----------|-------|
| **CPUs** | 4 |
| **RAM** | 8 GB |
| **Disk** | 80 GB |
| **Network** | NAT + Host-Only |
| **ISO** | https://www.kali.org/get-kali/ |

**Setup:**
```bash
cd scripts/vm-setup
./create-kali-vm.sh
```

**Tools Included:**
- Metasploit Framework
- Burp Suite Professional
- Nmap, Wireshark
- Aircrack-ng
- Hashcat
- SQLmap

### VM2: Parrot OS (Privacy & Stealth)

| Parameter | Value |
|-----------|-------|
| **CPUs** | 4 |
| **RAM** | 8 GB |
| **Disk** | 80 GB |
| **Network** | NAT + Host-Only + Tor |
| **ISO** | https://www.parrotsec.org/download/ |

**Setup:**
```bash
cd scripts/vm-setup
./create-parrot-vm.sh
```

**Tools Included:**
- AnonSurf (Tor routing)
- I2P integration
- MAT2 (metadata cleaner)
- OnionShare
- Tails-like privacy features

### VM3: KhaosOS (Sovereign System)

| Parameter | Value |
|-----------|-------|
| **CPUs** | 8 |
| **RAM** | 16 GB |
| **Disk** | 256 GB |
| **Network** | NAT + Host-Only + WireGuard |
| **ISO** | NixOS 23.11 (download from nixos.org) |
| **GPU** | Passthrough (if available) |

**Setup:**
```bash
cd scripts/vm-setup
./create-khaosos-vm.sh
```

---

## Network Configuration

### Internal Network Topology

```
┌─────────────────────────────────────────────────────────────┐
│                    Host Machine                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐      │
│  │ Kali Linux  │   │ Parrot OS   │   │  KhaosOS    │      │
│  │ 10.0.0.10   │   │ 10.0.0.20   │   │ 10.0.0.30   │      │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘      │
│         │                 │                 │              │
│         └─────────────────┴─────────────────┘              │
│                           │                                │
│                  Internal Bridge (vmbr0)                   │
│                      10.0.0.1/24                           │
│                           │                                │
│                    ┌──────┴──────┐                         │
│                    │   NAT/FW    │                         │
│                    └──────┬──────┘                         │
│                           │                                │
└───────────────────────────┼─────────────────────────────────┘
                            │
                       Internet
```

### Firewall Rules

```bash
# Allow inter-VM communication
iptables -A FORWARD -i vmbr0 -o vmbr0 -j ACCEPT

# NAT for internet access
iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o eth0 -j MASQUERADE

# Block VM-to-host access (security)
iptables -A INPUT -s 10.0.0.0/24 -j DROP
iptables -A INPUT -s 10.0.0.30 -p tcp --dport 22 -j ACCEPT  # KhaosOS SSH only
```

---

## Security Hardening

### Host System

1. **Enable Full Disk Encryption**
   ```bash
   # During OS installation, enable LUKS encryption
   ```

2. **Disable Unused Services**
   ```bash
   sudo systemctl disable bluetooth
   sudo systemctl disable cups
   ```

3. **Configure Firewall**
   ```bash
   sudo ufw enable
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw allow 22/tcp  # SSH
   ```

### VM Isolation

1. **Separate Networks**
   - Red Team (Kali): Isolated, monitored
   - Privacy (Parrot): Tor-only network
   - Sovereign (KhaosOS): WireGuard mesh

2. **Snapshot Strategy**
   ```bash
   # VirtualBox
   VBoxManage snapshot "KhaosOS" take "clean-install"
   
   # QEMU/KVM
   virsh snapshot-create-as khaosos clean-install
   
   # Proxmox
   qm snapshot <vmid> clean-install
   ```

3. **Resource Limits**
   ```bash
   # Limit CPU/RAM to prevent resource exhaustion
   VBoxManage modifyvm "Kali" --cpus 4 --memory 8192 --vram 128
   ```

---

## Backup and Disaster Recovery

### Automated Backups

```bash
#!/bin/bash
# Backup script for VMs

BACKUP_DIR="/backup/vms"
DATE=$(date +%Y%m%d)

# VirtualBox
VBoxManage export KhaosOS -o "$BACKUP_DIR/khaosos-$DATE.ova"

# Proxmox
vzdump <vmid> --mode snapshot --compress zstd --storage local

# QEMU/KVM
virsh dumpxml khaosos > "$BACKUP_DIR/khaosos-$DATE.xml"
cp /var/lib/libvirt/images/khaosos.qcow2 "$BACKUP_DIR/khaosos-$DATE.qcow2"
```

### Recovery Procedure

```bash
# VirtualBox
VBoxManage import khaosos-backup.ova

# Proxmox
qmrestore /backup/vzdump-qemu-*.vma.zst <new-vmid>

# QEMU/KVM
virsh define khaosos-backup.xml
cp khaosos-backup.qcow2 /var/lib/libvirt/images/khaosos.qcow2
virsh start khaosos
```

---

## Troubleshooting

### VM Won't Start

```bash
# Check virtualization support
egrep -c '(vmx|svm)' /proc/cpuinfo  # Should be > 0

# Check KVM modules
lsmod | grep kvm

# Check libvirt status
sudo systemctl status libvirtd
```

### Poor Performance

1. Enable nested virtualization (if needed)
2. Allocate more resources (CPU/RAM)
3. Use virtio drivers for better I/O
4. Enable KVM hardware acceleration

### Network Issues

```bash
# Check bridge status
ip link show vmbr0

# Check VM network
virsh domiflist khaosos

# Test connectivity
ping -c 3 10.0.0.30
```

---

## Next Steps

1. [Install KhaosOS](../scripts/vm-setup/bootstrap-khaosos.sh)
2. [Configure Queen CLI](../KHAOSOS_ARCHITECTURE.md#queen-cli)
3. [Deploy Sovereign Tools](../docs/SOVEREIGN_TOOL_STACK.md)

---

**Last Updated:** 2025-12-07  
**Maintained By:** Strategickhaos DAO LLC
