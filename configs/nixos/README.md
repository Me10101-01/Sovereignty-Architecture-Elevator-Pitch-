# KhaosOS NixOS Configuration

This directory contains the declarative NixOS configuration for KhaosOS - the sovereign operating system.

## Files

- `khaosos-configuration.nix` - Main system configuration
- `README.md` - This file

## Installation

### Prerequisites

- NixOS 24.05 or later
- Minimum 16GB RAM (32GB recommended)
- Minimum 100GB storage (200GB recommended)
- UEFI-capable system

### Fresh Installation

1. **Download NixOS ISO:**
   ```bash
   wget https://channels.nixos.org/nixos-24.05/latest-nixos-minimal-x86_64-linux.iso
   ```

2. **Create bootable USB:**
   ```bash
   dd if=latest-nixos-minimal-x86_64-linux.iso of=/dev/sdX bs=4M status=progress
   ```

3. **Boot from USB and partition disk:**
   ```bash
   # For UEFI systems
   parted /dev/sda -- mklabel gpt
   parted /dev/sda -- mkpart ESP fat32 1MiB 512MiB
   parted /dev/sda -- set 1 esp on
   parted /dev/sda -- mkpart primary 512MiB 100%
   
   # Format partitions
   mkfs.fat -F 32 -n boot /dev/sda1
   mkfs.ext4 -L nixos /dev/sda2
   
   # For encrypted root (recommended):
   cryptsetup luksFormat /dev/sda2
   cryptsetup luksOpen /dev/sda2 cryptroot
   mkfs.ext4 -L nixos /dev/mapper/cryptroot
   ```

4. **Mount filesystems:**
   ```bash
   mount /dev/disk/by-label/nixos /mnt
   mkdir -p /mnt/boot
   mount /dev/disk/by-label/boot /mnt/boot
   ```

5. **Generate initial config:**
   ```bash
   nixos-generate-config --root /mnt
   ```

6. **Copy KhaosOS configuration:**
   ```bash
   curl -o /mnt/etc/nixos/configuration.nix \
     https://raw.githubusercontent.com/strategickhaos/khaosos/main/configs/nixos/khaosos-configuration.nix
   ```

7. **Install NixOS:**
   ```bash
   nixos-install
   ```

8. **Reboot:**
   ```bash
   reboot
   ```

### Updating Existing Installation

If you already have NixOS installed:

1. **Backup current config:**
   ```bash
   sudo cp /etc/nixos/configuration.nix /etc/nixos/configuration.nix.backup
   ```

2. **Copy KhaosOS config:**
   ```bash
   sudo cp khaosos-configuration.nix /etc/nixos/configuration.nix
   ```

3. **Review and customize:**
   ```bash
   sudo vim /etc/nixos/configuration.nix
   # Update hostname, user accounts, SSH keys, etc.
   ```

4. **Test configuration:**
   ```bash
   sudo nixos-rebuild test
   ```

5. **Apply permanently:**
   ```bash
   sudo nixos-rebuild switch
   ```

## Customization

### Required Changes

Before deploying, you MUST customize:

1. **SSH Public Keys** (line ~220):
   ```nix
   openssh.authorizedKeys.keys = [
     "ssh-ed25519 AAAAC3... your-key-here"
   ];
   ```

2. **Time Zone** (line ~240):
   ```nix
   time.timeZone = "America/Chicago";  # Change to your timezone
   ```

3. **User Account** (line ~215):
   ```nix
   users.users.khaos = {
     # Change username if desired
   };
   ```

### Optional Customizations

1. **Enable Desktop Environment:**
   ```nix
   services.xserver.enable = true;
   services.xserver.displayManager.gdm.enable = true;
   services.xserver.desktopManager.gnome.enable = true;
   ```

2. **Add More Packages:**
   ```nix
   environment.systemPackages = with pkgs; [
     # Add your packages here
     vscode
     firefox
     signal-desktop
   ];
   ```

3. **Configure WireGuard Peers:**
   ```nix
   networking.wireguard.interfaces.wg0.peers = [
     {
       publicKey = "PEER_PUBLIC_KEY";
       allowedIPs = [ "10.100.0.2/32" ];
       endpoint = "peer.example.com:51820";
     }
   ];
   ```

## Security Features

### Kernel Hardening

The configuration includes:
- Hardened kernel package
- Security-focused sysctls
- BPF JIT hardening
- Kernel pointer protection
- ASLR enabled

### Network Security

- Default-deny firewall
- Connection rate limiting
- Invalid packet dropping
- IPv6 privacy extensions

### System Security

- Automatic security updates
- GPG agent for key management
- SSH key-only authentication
- Sudo timeout configured
- No root login

## Services

### Enabled by Default

- **Ollama:** Local LLM inference (port 11434)
- **Docker:** Container runtime
- **Tailscale:** Mesh VPN
- **OpenSSH:** Remote access (key-based only)

### Disabled by Default

To enable additional services, add to configuration:

```nix
# Example: Enable PostgreSQL
services.postgresql.enable = true;

# Example: Enable Nginx
services.nginx.enable = true;
```

## Troubleshooting

### Boot Issues

If system doesn't boot:
1. Boot from NixOS live USB
2. Mount root filesystem
3. Chroot into system:
   ```bash
   nixos-enter --root /mnt
   ```
4. Rollback to previous generation:
   ```bash
   nixos-rebuild switch --rollback
   ```

### Package Not Found

If a package is not available:
1. Search NixOS packages: https://search.nixos.org
2. Check package name spelling
3. Update channel:
   ```bash
   sudo nix-channel --update
   sudo nixos-rebuild switch
   ```

### Service Won't Start

Check service status:
```bash
systemctl status servicename
journalctl -u servicename
```

## Maintenance

### Regular Updates

```bash
# Update package definitions
sudo nix-channel --update

# Rebuild system with updates
sudo nixos-rebuild switch

# Clean old generations (keep last 30 days)
sudo nix-collect-garbage --delete-older-than 30d
```

### Rollback

NixOS keeps all previous configurations:

```bash
# List available generations
nixos-rebuild list-generations

# Boot into specific generation
sudo nixos-rebuild switch --rollback

# Or select at boot time from GRUB menu
```

## Advanced Topics

### Flakes (Experimental)

For reproducible builds with locked dependencies:

```bash
# Enable flakes
nix.settings.experimental-features = [ "nix-command" "flakes" ];

# Convert to flake
nix flake init
nix flake update
```

### Custom Packages

Create package overlays in `/etc/nixos/overlays/`:

```nix
self: super: {
  mypackage = super.callPackage ./mypackage.nix {};
}
```

### NixOps Deployment

For managing multiple machines:

```bash
nixops create network.nix -d khaos-network
nixops deploy -d khaos-network
```

## Resources

- [NixOS Manual](https://nixos.org/manual/nixos/stable/)
- [NixOS Options Search](https://search.nixos.org/options)
- [NixOS Discourse](https://discourse.nixos.org/)
- [NixOS Wiki](https://nixos.wiki/)

## Support

- 🐛 Issues: https://github.com/strategickhaos/khaosos/issues
- 💬 Discussions: https://github.com/strategickhaos/khaosos/discussions
- 🔒 Security: security@strategickhaos.ai

---

*"Declarative. Reproducible. Sovereign."* ⚔️
