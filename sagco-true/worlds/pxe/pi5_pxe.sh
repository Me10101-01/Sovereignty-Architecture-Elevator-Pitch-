#!/usr/bin/env bash
# SAGCO PXE Server — Pi 5 Edition
# Run this on the Pi 5. Pi is already on the LAN — no NAT problem.
# Pi 5 becomes the PXE server. Lyra becomes the NFS root server (optional).
#
# Usage (from Z Fold or Lyra SSH):
#   ssh pi@<pi5-ip>
#   sudo bash pi5_pxe.sh [--server-ip <pi-ip>]

set -euo pipefail

PI_IP=$(ip addr show eth0 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1 | head -1 || \
        ip addr show wlan0 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1 | head -1)

if [[ "$1" == "--server-ip" && -n "${2:-}" ]]; then
    PI_IP="$2"
fi

echo "Pi 5 IP: $PI_IP"
echo "This Pi will serve PXE boot to the HP OmniDesk."

TFTP_ROOT="/srv/tftp"
ALPINE_VERSION="3.20"
ALPINE_BASE="https://dl-cdn.alpinelinux.org/alpine/v${ALPINE_VERSION}/releases/x86_64/netboot"

# Install
apt-get install -y -q dnsmasq tftpd-hpa wget grub-efi-amd64-bin

# TFTP dirs
mkdir -p "$TFTP_ROOT/efi64" "$TFTP_ROOT/grub"

# Bootloader
cp /usr/lib/grub/x86_64-efi/grub.efi "$TFTP_ROOT/efi64/" 2>/dev/null || true

# GRUB menu
cat > "$TFTP_ROOT/grub/grub.cfg" <<EOF
set timeout=10
set default=0

menuentry "SAGCO Node — HP OmniDesk (UEFI)" {
    linuxefi  /efi64/vmlinuz ip=dhcp sagco_node=hp-omnidesk sagco_server=$PI_IP
    initrdefi /efi64/initramfs
}
menuentry "Boot local disk" { exit }
EOF

# Download Alpine netboot
[[ -f "$TFTP_ROOT/efi64/vmlinuz"   ]] || wget -q "${ALPINE_BASE}/vmlinuz-lts"   -O "$TFTP_ROOT/efi64/vmlinuz"
[[ -f "$TFTP_ROOT/efi64/initramfs" ]] || wget -q "${ALPINE_BASE}/initramfs-lts" -O "$TFTP_ROOT/efi64/initramfs"

# dnsmasq — proxy DHCP (won't conflict with your router)
cat > /etc/dnsmasq.d/sagco-pxe.conf <<EOF
interface=eth0
bind-interfaces
dhcp-range=192.168.1.0,proxy
log-dhcp
pxe-service=x86-64_EFI,"SAGCO Node Boot (UEFI)",efi64/grub.efi,$PI_IP
enable-tftp
tftp-root=$TFTP_ROOT
EOF

# tftpd-hpa
sed -i "s|TFTP_DIRECTORY=.*|TFTP_DIRECTORY=\"$TFTP_ROOT\"|" /etc/default/tftpd-hpa

# Start
systemctl restart tftpd-hpa dnsmasq

echo ""
echo "═══════════════════════════════════════════"
echo "  SAGCO PXE — Pi 5 Server ACTIVE"
echo "  Pi IP     : $PI_IP"
echo "  TFTP      : $TFTP_ROOT"
echo "  HP next:  : Set Network Adapter = Boot #1"
echo "  Watch:    : journalctl -fu dnsmasq"
echo "═══════════════════════════════════════════"
