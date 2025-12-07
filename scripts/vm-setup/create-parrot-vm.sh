#!/bin/bash
# create-parrot-vm.sh
# Automated Parrot OS VM creation for VirtualBox
# Part of KhaosOS Architecture - Privacy & Stealth Operations

set -euo pipefail

# Configuration
VM_NAME="KhaosOS-Parrot"
VM_CPUS=4
VM_RAM=8192  # MB
VM_VRAM=128  # MB
VM_DISK_SIZE=81920  # MB (80 GB)
VM_NETWORK="NAT"
VM_HOSTONLYNET="vboxnet0"
ISO_URL="https://deb.parrot.sh/parrot/iso/6.1/Parrot-security-6.1_amd64.iso"
ISO_NAME="Parrot-security-6.1_amd64.iso"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   KhaosOS - Parrot OS VM Setup (Privacy & Stealth)   ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if VirtualBox is installed
if ! command -v VBoxManage &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} VirtualBox not found. Please install VirtualBox first."
    exit 1
fi

echo -e "${YELLOW}[INFO]${NC} Checking for existing VM..."
if VBoxManage list vms | grep -q "\"$VM_NAME\""; then
    echo -e "${YELLOW}[WARN]${NC} VM '$VM_NAME' already exists."
    read -p "Do you want to delete and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}[INFO]${NC} Deleting existing VM..."
        VBoxManage unregistervm "$VM_NAME" --delete
    else
        echo -e "${YELLOW}[INFO]${NC} Exiting without changes."
        exit 0
    fi
fi

# Download Parrot ISO if not present
if [ ! -f "$ISO_NAME" ]; then
    echo -e "${YELLOW}[INFO]${NC} Downloading Parrot OS ISO..."
    echo -e "${YELLOW}[INFO]${NC} This may take a while (3-4 GB download)..."
    wget -c "$ISO_URL" -O "$ISO_NAME"
    echo -e "${GREEN}[SUCCESS]${NC} ISO downloaded."
else
    echo -e "${GREEN}[INFO]${NC} Using existing ISO: $ISO_NAME"
fi

# Create VM
echo -e "${YELLOW}[INFO]${NC} Creating VM: $VM_NAME..."
VBoxManage createvm --name "$VM_NAME" --ostype "Debian_64" --register

# Configure VM settings
echo -e "${YELLOW}[INFO]${NC} Configuring VM settings..."
VBoxManage modifyvm "$VM_NAME" \
    --cpus $VM_CPUS \
    --memory $VM_RAM \
    --vram $VM_VRAM \
    --graphicscontroller vmsvga \
    --nic1 nat \
    --nic2 hostonly \
    --hostonlyadapter2 $VM_HOSTONLYNET \
    --boot1 disk \
    --boot2 dvd \
    --boot3 none \
    --boot4 none \
    --audio none \
    --usb on \
    --usbxhci on \
    --clipboard bidirectional \
    --draganddrop bidirectional

# Create virtual hard disk
echo -e "${YELLOW}[INFO]${NC} Creating virtual hard disk..."
VM_DIR="$HOME/VirtualBox VMs/$VM_NAME"
VBoxManage createhd --filename "$VM_DIR/$VM_NAME.vdi" --size $VM_DISK_SIZE --variant Standard

# Create SATA controller and attach disk
echo -e "${YELLOW}[INFO]${NC} Attaching virtual hard disk..."
VBoxManage storagectl "$VM_NAME" --name "SATA" --add sata --controller IntelAhci
VBoxManage storageattach "$VM_NAME" --storagectl "SATA" --port 0 --device 0 --type hdd --medium "$VM_DIR/$VM_NAME.vdi"

# Create IDE controller for DVD
echo -e "${YELLOW}[INFO]${NC} Attaching installation ISO..."
VBoxManage storagectl "$VM_NAME" --name "IDE" --add ide
VBoxManage storageattach "$VM_NAME" --storagectl "IDE" --port 0 --device 0 --type dvddrive --medium "$(pwd)/$ISO_NAME"

# Enable nested virtualization
echo -e "${YELLOW}[INFO]${NC} Enabling nested virtualization..."
VBoxManage modifyvm "$VM_NAME" --nested-hw-virt on

# Configure port forwarding for SSH
echo -e "${YELLOW}[INFO]${NC} Configuring port forwarding (SSH: 2223 -> 22)..."
VBoxManage modifyvm "$VM_NAME" --natpf1 "ssh,tcp,,2223,,22"

# Take initial snapshot
echo -e "${YELLOW}[INFO]${NC} Creating initial snapshot..."
VBoxManage snapshot "$VM_NAME" take "fresh-install" --description "Clean Parrot OS installation"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                VM CREATION COMPLETE                   ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}VM Name:${NC} $VM_NAME"
echo -e "${GREEN}CPUs:${NC} $VM_CPUS"
echo -e "${GREEN}RAM:${NC} $VM_RAM MB"
echo -e "${GREEN}Disk:${NC} $VM_DISK_SIZE MB"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Start the VM: VBoxManage startvm \"$VM_NAME\" --type gui"
echo "2. Complete Parrot OS installation"
echo "3. After installation, eject the ISO:"
echo "   VBoxManage storageattach \"$VM_NAME\" --storagectl \"IDE\" --port 0 --device 0 --type dvddrive --medium none"
echo "4. Install VirtualBox Guest Additions for better integration"
echo "5. SSH access: ssh -p 2223 parrot@localhost"
echo ""
echo -e "${YELLOW}Recommended Post-Install Configuration:${NC}"
echo "   - Enable AnonSurf: sudo anonsurf start"
echo "   - Configure Tor Browser"
echo "   - Install I2P: sudo apt install i2p"
echo "   - Install MAT2: sudo apt install mat2"
echo "   - Configure OnionShare"
echo ""
echo -e "${YELLOW}Privacy Tools Included:${NC}"
echo "   - AnonSurf (System-wide Tor)"
echo "   - Tor Browser"
echo "   - OnionShare"
echo "   - MAT2 (Metadata Anonymization)"
echo "   - Electrum (Bitcoin Wallet)"
echo ""

# Optional: Start VM automatically
read -p "Do you want to start the VM now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}[INFO]${NC} Starting VM..."
    VBoxManage startvm "$VM_NAME" --type gui
fi

echo -e "${GREEN}[COMPLETE]${NC} Parrot OS VM setup finished!"
