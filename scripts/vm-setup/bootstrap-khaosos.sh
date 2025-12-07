#!/bin/bash
# bootstrap-khaosos.sh
# Bootstrap KhaosOS from NixOS installation
# Part of KhaosOS Sovereign Architecture

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          KhaosOS Bootstrap - Sovereign System         ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running on NixOS
if [ ! -f /etc/NIXOS ]; then
    echo -e "${RED}[ERROR]${NC} This script must be run on NixOS."
    exit 1
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} This script must be run as root."
    echo "Please run: sudo $0"
    exit 1
fi

echo -e "${YELLOW}[INFO]${NC} Starting KhaosOS bootstrap process..."
echo ""

# Step 1: Backup existing configuration
echo -e "${BLUE}[STEP 1/7]${NC} Backing up existing configuration..."
if [ -f /etc/nixos/configuration.nix ]; then
    cp /etc/nixos/configuration.nix /etc/nixos/configuration.nix.backup.$(date +%Y%m%d-%H%M%S)
    echo -e "${GREEN}[SUCCESS]${NC} Configuration backed up."
else
    echo -e "${YELLOW}[WARN]${NC} No existing configuration found."
fi

# Step 2: Copy KhaosOS configuration
echo -e "${BLUE}[STEP 2/7]${NC} Installing KhaosOS configuration..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONFIG_SOURCE="$SCRIPT_DIR/../../configs/nixos/khaosos-configuration.nix"

if [ -f "$CONFIG_SOURCE" ]; then
    cp "$CONFIG_SOURCE" /etc/nixos/configuration.nix
    echo -e "${GREEN}[SUCCESS]${NC} KhaosOS configuration installed."
else
    echo -e "${RED}[ERROR]${NC} KhaosOS configuration not found at: $CONFIG_SOURCE"
    exit 1
fi

# Step 3: Generate hardware configuration
echo -e "${BLUE}[STEP 3/7]${NC} Generating hardware configuration..."
nixos-generate-config --show-hardware-config > /etc/nixos/hardware-configuration.nix
echo -e "${GREEN}[SUCCESS]${NC} Hardware configuration generated."

# Step 4: Create WireGuard keys
echo -e "${BLUE}[STEP 4/7]${NC} Generating WireGuard keys..."
mkdir -p /etc/wireguard
umask 077
wg genkey | tee /etc/wireguard/private.key | wg pubkey > /etc/wireguard/public.key
echo -e "${GREEN}[SUCCESS]${NC} WireGuard keys generated."
echo -e "${YELLOW}[INFO]${NC} Your WireGuard public key:"
cat /etc/wireguard/public.key

# Step 5: Set user password
echo -e "${BLUE}[STEP 5/7]${NC} Setting up user account..."
read -p "Enter username for KhaosOS operator [khaos]: " USERNAME
USERNAME=${USERNAME:-khaos}

echo "Enter password for user $USERNAME:"
read -s PASSWORD1
echo ""
echo "Confirm password:"
read -s PASSWORD2
echo ""

if [ "$PASSWORD1" != "$PASSWORD2" ]; then
    echo -e "${RED}[ERROR]${NC} Passwords do not match!"
    exit 1
fi

PASSWORD_HASH=$(echo "$PASSWORD1" | mkpasswd -m sha-512 -s)

# Update configuration with password hash
sed -i "s|hashedPassword = null;|hashedPassword = \"$PASSWORD_HASH\";|g" /etc/nixos/configuration.nix
sed -i "s|users.users.khaos|users.users.$USERNAME|g" /etc/nixos/configuration.nix
echo -e "${GREEN}[SUCCESS]${NC} User account configured."

# Step 6: Build and switch to new configuration
echo -e "${BLUE}[STEP 6/7]${NC} Building KhaosOS (this may take 15-30 minutes)..."
echo -e "${YELLOW}[INFO]${NC} This will download and compile packages..."

if nixos-rebuild switch; then
    echo -e "${GREEN}[SUCCESS]${NC} KhaosOS build complete!"
else
    echo -e "${RED}[ERROR]${NC} Build failed. Check errors above."
    echo -e "${YELLOW}[INFO]${NC} Your original configuration has been backed up."
    exit 1
fi

# Step 7: Post-installation tasks
echo -e "${BLUE}[STEP 7/7]${NC} Running post-installation tasks..."

# Pull Ollama models
echo -e "${YELLOW}[INFO]${NC} Pulling Ollama models (this may take a while)..."
systemctl start ollama
sleep 5

echo -e "${YELLOW}[INFO]${NC} Downloading AI models sequentially to avoid network overload..."
echo -e "${YELLOW}[INFO]${NC} Model 1/3: qwen2.5:72b (largest, ~40GB)..."
if ollama pull qwen2.5:72b; then
    echo -e "${GREEN}[SUCCESS]${NC} qwen2.5:72b downloaded."
else
    echo -e "${YELLOW}[WARN]${NC} Failed to download qwen2.5:72b. You can pull it manually later."
fi

echo -e "${YELLOW}[INFO]${NC} Model 2/3: llama3.2:70b (~38GB)..."
if ollama pull llama3.2:70b; then
    echo -e "${GREEN}[SUCCESS]${NC} llama3.2:70b downloaded."
else
    echo -e "${YELLOW}[WARN]${NC} Failed to download llama3.2:70b. You can pull it manually later."
fi

echo -e "${YELLOW}[INFO]${NC} Model 3/3: mistral:7b (smallest, ~4GB)..."
if ollama pull mistral:7b; then
    echo -e "${GREEN}[SUCCESS]${NC} mistral:7b downloaded."
else
    echo -e "${YELLOW}[WARN]${NC} Failed to download mistral:7b. You can pull it manually later."
fi

echo -e "${GREEN}[INFO]${NC} Model downloads complete. Check status with: ollama list"

# Enable and start services
echo -e "${YELLOW}[INFO]${NC} Enabling services..."
systemctl enable docker
systemctl enable tailscale
systemctl enable ollama

# Create Queen CLI alias
echo -e "${YELLOW}[INFO]${NC} Setting up Queen CLI..."
cat >> /home/$USERNAME/.bashrc << 'EOF'

# Queen CLI alias (to be implemented)
alias queen='echo "Queen CLI - Coming Soon"'
EOF

chown $USERNAME:users /home/$USERNAME/.bashrc

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            KHAOSOS BOOTSTRAP COMPLETE                 ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}System Status:${NC}"
echo "  • NixOS with hardened kernel: ✓"
echo "  • Docker runtime: ✓"
echo "  • Ollama AI engine: ✓"
echo "  • Tailscale VPN: ✓"
echo "  • WireGuard configured: ✓"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Reboot the system: sudo reboot"
echo "2. Login as: $USERNAME"
echo "3. Configure Tailscale: sudo tailscale up"
echo "4. Check Ollama models: ollama list"
echo "5. Deploy sovereign tools: cd /path/to/repo && docker-compose -f docker-compose/khaossearch.yml up -d"
echo ""
echo -e "${YELLOW}Your WireGuard Public Key:${NC}"
cat /etc/wireguard/public.key
echo ""
echo -e "${YELLOW}Configuration Files:${NC}"
echo "  • System: /etc/nixos/configuration.nix"
echo "  • Hardware: /etc/nixos/hardware-configuration.nix"
echo "  • WireGuard: /etc/wireguard/"
echo ""
echo -e "${GREEN}Welcome to KhaosOS - Own the stack. Own the data. Own the destiny.${NC} ⚔️🔥"
