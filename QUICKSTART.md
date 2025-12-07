# KhaosOS Quick Start Guide
## Get Up and Running in 30 Minutes

This guide will help you quickly deploy the KhaosOS architecture on your local machine or server.

---

## Prerequisites

- **Hardware:** 16GB RAM, 256GB SSD, 4-core CPU minimum
- **Host OS:** Windows 10+, macOS 10.15+, or Linux
- **Virtualization:** VT-x/AMD-V enabled in BIOS
- **Software:** Git, Docker, VirtualBox (or Proxmox)
- **Time:** 30-60 minutes

---

## Option 1: Quick Demo (VirtualBox)

Perfect for testing and development.

### Step 1: Install VirtualBox

```bash
# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install virtualbox virtualbox-ext-pack

# macOS
brew install --cask virtualbox

# Windows
# Download from https://www.virtualbox.org/
```

### Step 2: Clone Repository

```bash
git clone https://github.com/Me10101-01/Sovereignty-Architecture-Elevator-Pitch-.git
cd Sovereignty-Architecture-Elevator-Pitch-
```

### Step 3: Create VMs

```bash
# Create Kali Linux VM (Red Team)
cd scripts/vm-setup
./create-kali-vm.sh

# Create Parrot OS VM (Privacy)
./create-parrot-vm.sh

# Both scripts will:
# - Download ISOs (3-4GB each)
# - Create VMs with optimal settings
# - Configure networking
# - Create snapshots
```

### Step 4: Install Operating Systems

```bash
# Start Kali VM
VBoxManage startvm "KhaosOS-Kali" --type gui

# Start Parrot VM (in another terminal)
VBoxManage startvm "KhaosOS-Parrot" --type gui

# Follow on-screen installation wizards for both
# Use default settings unless you have specific requirements
```

### Step 5: Deploy KhaosOS (NixOS)

```bash
# Download NixOS ISO
wget https://channels.nixos.org/nixos-23.11/latest-nixos-minimal-x86_64-linux.iso

# Create KhaosOS VM
VBoxManage createvm --name "KhaosOS" --ostype "Linux_64" --register
VBoxManage modifyvm "KhaosOS" --cpus 8 --memory 16384 --vram 128
# ... (see scripts/vm-setup/create-khaosos-vm.sh for full config)

# Start VM and install NixOS
VBoxManage startvm "KhaosOS" --type gui

# After NixOS installation, run bootstrap
sudo ./scripts/vm-setup/bootstrap-khaosos.sh
```

---

## Option 2: Production Setup (Proxmox)

For dedicated hardware and production use.

### Step 1: Install Proxmox VE

```bash
# Download Proxmox VE ISO
wget https://www.proxmox.com/en/downloads/category/iso-images-pve

# Create bootable USB
sudo dd if=proxmox-ve_*.iso of=/dev/sdX bs=1M status=progress

# Boot from USB and follow installation wizard
```

### Step 2: Access Web UI

```bash
# After installation, access Proxmox at:
https://<proxmox-ip>:8006

# Login with root credentials set during installation
```

### Step 3: Upload ISOs

1. Download ISOs on your workstation:
   - Kali Linux: https://www.kali.org/get-kali/
   - Parrot OS: https://www.parrotsec.org/download/
   - NixOS: https://nixos.org/download.html

2. Upload to Proxmox:
   - Navigate to Storage → local → ISO Images
   - Click "Upload" and select each ISO

### Step 4: Create VMs via Web UI

**VM 1: Kali Linux**
- Name: KhaosOS-Kali
- OS: Linux 6.x - 2.6 Kernel
- CPUs: 4 cores
- RAM: 8192 MB
- Disk: 80 GB
- Network: vmbr0

**VM 2: Parrot OS**
- Name: KhaosOS-Parrot
- OS: Linux 6.x - 2.6 Kernel
- CPUs: 4 cores
- RAM: 8192 MB
- Disk: 80 GB
- Network: vmbr0

**VM 3: KhaosOS**
- Name: KhaosOS-Sovereign
- OS: Linux 6.x - 2.6 Kernel
- CPUs: 8 cores
- RAM: 16384 MB
- Disk: 256 GB
- Network: vmbr0
- GPU: Passthrough (optional)

---

## Option 3: Docker Compose (Fastest)

Deploy sovereign tools without full VMs.

### Step 1: Install Docker

```bash
# Linux
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# macOS
brew install --cask docker

# Windows
# Install Docker Desktop from docker.com
```

### Step 2: Deploy KhaosSearch

```bash
cd docker-compose

# Create network
docker network create khaosnet

# Deploy SearXNG (meta-search)
docker-compose -f khaossearch.yml up -d

# Access at: http://localhost:8888
```

### Step 3: Deploy KhaosLLM

```bash
# Deploy Ollama + Qdrant (AI stack)
docker-compose -f khaosllm.yml up -d

# Pull models (this takes time - 40GB+ download)
docker exec khaosllm-ollama ollama pull qwen2.5:72b
docker exec khaosllm-ollama ollama pull llama3.2:70b

# Test inference
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:72b",
  "prompt": "Explain digital sovereignty in 3 sentences."
}'
```

### Step 4: Deploy Additional Tools

```bash
# KhaosBase (NocoDB - Airtable alternative)
docker run -d \
  --name khaosbase \
  -p 8080:8080 \
  -v khaosbase-data:/usr/app/data \
  nocodb/nocodb:latest

# KhaosForge (Gitea - GitHub alternative)
docker run -d \
  --name khaosforge \
  -p 3000:3000 \
  -p 222:22 \
  -v khaosforge-data:/data \
  gitea/gitea:latest

# KhaosVault (Vaultwarden - password manager)
docker run -d \
  --name khaosvault \
  -p 8000:80 \
  -v khaosvault-data:/data \
  vaultwarden/server:latest
```

---

## Verification

### Check VM Status (VirtualBox)

```bash
VBoxManage list runningvms
VBoxManage list vms
```

### Check Docker Services

```bash
docker ps
docker-compose -f docker-compose/khaossearch.yml ps
docker-compose -f docker-compose/khaosllm.yml ps
```

### Test Services

```bash
# KhaosSearch
curl http://localhost:8888

# KhaosLLM (Ollama)
curl http://localhost:11434/api/tags

# Qdrant (Vector DB)
curl http://localhost:6333/

# KhaosBase (NocoDB)
curl http://localhost:8080
```

---

## Common Issues

### Issue: Virtualization Not Enabled

**Solution:**
1. Reboot and enter BIOS/UEFI
2. Enable VT-x (Intel) or AMD-V (AMD)
3. Save and reboot

### Issue: Port Already in Use

**Solution:**
```bash
# Find process using port
sudo lsof -i :8888

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
```

### Issue: Out of Disk Space

**Solution:**
```bash
# Clean Docker
docker system prune -a

# Clean VirtualBox
VBoxManage list hdds
VBoxManage closemedium disk <uuid> --delete
```

### Issue: Slow VM Performance

**Solution:**
1. Allocate more RAM to VM
2. Enable VT-x/AMD-V
3. Use SSD instead of HDD
4. Enable nested virtualization

---

## Next Steps

### 1. Configure Networking

```bash
# Set up WireGuard VPN
sudo wg genkey | tee /etc/wireguard/private.key | wg pubkey > /etc/wireguard/public.key

# Configure Tailscale
sudo tailscale up
```

### 2. Harden Security

```bash
# Enable firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw allow 22/tcp

# Set up GPG keys
gpg --full-generate-key

# Configure SSH keys
ssh-keygen -t ed25519 -C "your_email@example.com"
```

### 3. Deploy Full Stack

```bash
# Follow the implementation roadmap
# See: KHAOSOS_ARCHITECTURE.md

# Phase 0: Foundation (Week 1)
# - VMs running ✓
# - Docker services deployed ✓

# Phase 1: Tool Integration (Month 2)
# - Deploy remaining sovereign tools
# - Configure Queen CLI
# - Set up monitoring

# Phase 2: Security Hardening (Month 3)
# - Custom kernel compilation
# - Air-gap AI node
# - Hardware key integration
```

### 4. Backup Everything

```bash
# Export VMs
VBoxManage export KhaosOS-Kali -o backup/kali-$(date +%Y%m%d).ova

# Backup Docker volumes
docker run --rm -v khaosbase-data:/data -v $(pwd)/backup:/backup \
  alpine tar czf /backup/khaosbase-$(date +%Y%m%d).tar.gz /data
```

---

## Resources

- **Full Documentation:** [KHAOSOS_ARCHITECTURE.md](../KHAOSOS_ARCHITECTURE.md)
- **Hypervisor Guide:** [docs/HYPERVISOR_SETUP.md](../docs/HYPERVISOR_SETUP.md)
- **Tool Stack:** [docs/SOVEREIGN_TOOL_STACK.md](../docs/SOVEREIGN_TOOL_STACK.md)
- **Scripts:** [scripts/vm-setup/](../scripts/vm-setup/)

---

## Support

- **Issues:** GitHub Issues
- **Security:** security@strategickhaos.ai
- **Community:** Discord (coming soon)

---

**Time Investment:**
- VirtualBox Setup: 30-60 minutes (+ ISO download time)
- Proxmox Setup: 2-4 hours
- Docker-only: 15-30 minutes

**Difficulty:**
- Docker: ⭐ Beginner
- VirtualBox: ⭐⭐ Intermediate
- Proxmox: ⭐⭐⭐ Advanced

---

*"Own the stack. Own the data. Own the destiny."* ⚔️🔥

**Last Updated:** 2025-12-07  
**Version:** 1.0
