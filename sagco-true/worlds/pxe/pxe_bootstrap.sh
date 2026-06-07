#!/usr/bin/env bash
# SAGCO PXE Bootstrap — Lyra WSL2 Edition
# Run this ON LYRA inside WSL2.
# Sets up dnsmasq (UEFI PXE) + tftpd-hpa + NFS for SAGCO netboot.
#
# BEFORE YOU RUN THIS — fix the WSL2 network problem first:
#   See: wsl2_mirror_fix.md in this directory
#
# Usage:
#   chmod +x pxe_bootstrap.sh
#   sudo bash pxe_bootstrap.sh

set -euo pipefail

# ── Detect which IP to use ────────────────────────────────────────────────
# WSL2 default NAT IP (won't work for LAN PXE):
WSL_IP=$(ip addr show eth0 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1 | head -1)

# Windows host IP (the one LAN clients actually see):
WIN_IP=$(ip route | grep default | awk '{print $3}' | head -1)

# If mirrored networking is enabled, WSL_IP == WIN_IP
# If still NATed, you need the Windows IP route
echo "WSL2 eth0 IP  : $WSL_IP"
echo "Windows GW IP : $WIN_IP"

if [[ "$WSL_IP" == 192.168.* ]]; then
    SERVER_IP="$WSL_IP"
    echo "Mirrored networking ACTIVE — using $SERVER_IP"
elif [[ "$WSL_IP" == 172.* ]]; then
    echo "WARNING: WSL2 is NATed (IP $WSL_IP)"
    echo "         HP OmniDesk cannot reach this IP for PXE."
    echo ""
    echo "Fix options:"
    echo "  A) Enable WSL2 mirrored networking (recommended) — see wsl2_mirror_fix.md"
    echo "  B) Use Pi 5 as PXE server instead — see pi5_pxe.sh"
    echo "  C) Continue anyway if you know your bridged IP:"
    read -p "Enter server IP to use (or press Enter to abort): " MANUAL_IP
    if [[ -z "$MANUAL_IP" ]]; then
        echo "Aborted. Fix WSL2 networking first."; exit 1
    fi
    SERVER_IP="$MANUAL_IP"
else
    SERVER_IP="$WSL_IP"
fi

echo ""
echo "PXE Server IP : $SERVER_IP"
echo "Z Fold IP     : 192.168.1.89 (SAGCO-GTA node)"

TFTP_ROOT="/srv/tftp"
NFS_ROOT="/srv/nfs/sagco-boot"

# ── Install packages ──────────────────────────────────────────────────────
echo "Installing PXE stack..."
apt-get install -y -q \
    dnsmasq \
    tftpd-hpa \
    nfs-kernel-server \
    syslinux-efi \
    grub-efi-amd64-bin \
    wget \
    curl 2>&1 | tail -5

# ── TFTP root setup ───────────────────────────────────────────────────────
mkdir -p "$TFTP_ROOT/efi64" "$TFTP_ROOT/bios"

# Copy UEFI bootloader files
echo "Copying EFI bootloader files..."
cp /usr/lib/grub/x86_64-efi/grub.efi "$TFTP_ROOT/efi64/" 2>/dev/null || true

# Create GRUB PXE config
mkdir -p "$TFTP_ROOT/grub"
cat > "$TFTP_ROOT/grub/grub.cfg" <<GRUB_EOF
set timeout=10
set default=0

menuentry "SAGCO Node Boot — Alpine Linux" {
    linuxefi  /efi64/vmlinuz ip=dhcp console=tty0
    initrdefi /efi64/initramfs
}

menuentry "SAGCO Node Boot — Shell Only" {
    linuxefi  /efi64/vmlinuz ip=dhcp console=tty0 sagco_node=hp-omnidesk
    initrdefi /efi64/initramfs
}

menuentry "Boot from local disk" {
    exit
}
GRUB_EOF

# Download Alpine netboot if not present
ALPINE_VERSION="3.20"
ALPINE_BASE="https://dl-cdn.alpinelinux.org/alpine/v${ALPINE_VERSION}/releases/x86_64"
if [[ ! -f "$TFTP_ROOT/efi64/vmlinuz" ]]; then
    echo "Downloading Alpine ${ALPINE_VERSION} netboot kernel..."
    wget -q "${ALPINE_BASE}/netboot/vmlinuz-lts" -O "$TFTP_ROOT/efi64/vmlinuz" || \
    echo "WARN: Alpine download failed — place vmlinuz manually in $TFTP_ROOT/efi64/"
fi
if [[ ! -f "$TFTP_ROOT/efi64/initramfs" ]]; then
    echo "Downloading Alpine ${ALPINE_VERSION} initramfs..."
    wget -q "${ALPINE_BASE}/netboot/initramfs-lts" -O "$TFTP_ROOT/efi64/initramfs" || \
    echo "WARN: Alpine download failed — place initramfs manually in $TFTP_ROOT/efi64/"
fi

# ── tftpd-hpa config ──────────────────────────────────────────────────────
cat > /etc/default/tftpd-hpa <<TFTP_EOF
TFTP_USERNAME="tftp"
TFTP_DIRECTORY="$TFTP_ROOT"
TFTP_ADDRESS=":69"
TFTP_OPTIONS="--secure --create"
TFTP_EOF

# ── dnsmasq PXE config ────────────────────────────────────────────────────
# Using proxy DHCP mode — does NOT hand out IPs (your router still does that)
# Just adds PXE boot options to existing DHCP responses
cat > /etc/dnsmasq.d/sagco-pxe.conf <<DNSMASQ_EOF
# SAGCO PXE Boot — proxy DHCP mode
# Attaches to existing DHCP without replacing it

interface=eth0
bind-interfaces

# Proxy DHCP — respond to PXE requests but don't assign IPs
dhcp-range=192.168.1.0,proxy

# Log DHCP requests for debugging
log-dhcp

# UEFI PXE boot (type 7 = EFI x86-64)
pxe-service=x86-64_EFI,"Boot SAGCO Node (UEFI)",efi64/grub.efi,$SERVER_IP

# Legacy BIOS fallback
pxe-service=0,"Boot SAGCO Node (BIOS)",bios/pxelinux.0,$SERVER_IP

# TFTP server location
dhcp-boot=efi64/grub.efi,$SERVER_IP

enable-tftp
tftp-root=$TFTP_ROOT
DNSMASQ_EOF

# ── NFS root ──────────────────────────────────────────────────────────────
mkdir -p "$NFS_ROOT"

# Write SAGCO node init script into NFS root
mkdir -p "$NFS_ROOT/etc" "$NFS_ROOT/sagco"
cat > "$NFS_ROOT/sagco/node_init.sh" <<NODE_EOF
#!/bin/sh
# Runs on the booted HP OmniDesk to register it as a SAGCO node
echo "SAGCO Node HP-OmniDesk booting..."
echo "Server: $SERVER_IP"
MY_IP=\$(ip route get 1 | awk '{print \$NF; exit}')
echo "Node IP: \$MY_IP"
echo '{
  "node": "hp-omnidesk",
  "ip": "'\$MY_IP'",
  "server": "$SERVER_IP",
  "world": "pxe-linux",
  "status": "booted",
  "sagco_version": "0.1.0"
}' > /sagco/node.json
cat /sagco/node.json
NODE_EOF
chmod +x "$NFS_ROOT/sagco/node_init.sh"

# NFS export
echo "$NFS_ROOT *(ro,sync,no_subtree_check,no_root_squash)" >> /etc/exports
exportfs -ra 2>/dev/null || true

# ── Start services ────────────────────────────────────────────────────────
echo ""
echo "Starting services..."
systemctl restart tftpd-hpa 2>/dev/null || service tftpd-hpa restart 2>/dev/null || true
systemctl restart dnsmasq    2>/dev/null || service dnsmasq restart    2>/dev/null || true

echo ""
echo "═══════════════════════════════════════════"
echo "  SAGCO PXE Server ACTIVE"
echo "  Server IP : $SERVER_IP"
echo "  TFTP root : $TFTP_ROOT"
echo "  NFS root  : $NFS_ROOT"
echo "  Mode      : Proxy DHCP (UEFI + BIOS)"
echo ""
echo "  HP OmniDesk: set Network Adapter as boot #1"
echo "  It should see: 'Boot SAGCO Node (UEFI)'"
echo "═══════════════════════════════════════════"
echo ""
echo "Watch for PXE requests:"
echo "  journalctl -fu dnsmasq | grep -i pxe"
echo "  OR: tail -f /var/log/syslog | grep -i pxe"
