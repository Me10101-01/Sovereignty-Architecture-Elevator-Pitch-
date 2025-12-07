# KhaosOS Configuration Files

This directory contains all configuration files for the KhaosOS sovereign operating system and associated tools.

## Directory Structure

```
configs/
├── nixos/               # NixOS system configurations
│   ├── khaosos-configuration.nix    # Main system config
│   └── README.md                    # NixOS setup instructions
├── khaos-tools/         # Individual tool configurations
│   └── README.md                    # Tool configuration guide
└── README.md            # This file
```

## Quick Start

### NixOS Configuration

1. **Install NixOS** using the official ISO from https://nixos.org
2. **Copy configuration:**
   ```bash
   sudo cp configs/nixos/khaosos-configuration.nix /etc/nixos/configuration.nix
   ```
3. **Rebuild system:**
   ```bash
   sudo nixos-rebuild switch
   ```

### Tool Configurations

Individual tool configurations are stored in `khaos-tools/`. Each tool has its own subdirectory with:
- Docker Compose file (if containerized)
- Configuration files
- Setup instructions
- Migration guides from vendor services

## Configuration Philosophy

All KhaosOS configurations follow these principles:

1. **Declarative:** System state defined in version-controlled files
2. **Reproducible:** Exact same build on any hardware
3. **Secure by Default:** Hardened settings, minimal attack surface
4. **Self-Documenting:** Comments explain every non-obvious choice
5. **Modular:** Easy to enable/disable components

## Related Documentation

- [KHAOSOS_ARCHITECTURE.md](../KHAOSOS_ARCHITECTURE.md) - Overall architecture
- [KHAOSOS_ROADMAP.md](../KHAOSOS_ROADMAP.md) - Implementation plan
- [QUEEN_CLI.md](../QUEEN_CLI.md) - Command-line interface

## Security Notes

⚠️ **Before deploying to production:**

1. Generate unique secrets (don't use defaults)
2. Configure GPG keys for signing
3. Set up SSH keys for authentication
4. Review firewall rules for your environment
5. Enable disk encryption
6. Configure backup procedures

## Support

For questions or issues:
- 📖 Documentation: https://docs.strategickhaos.ai
- 💬 Forum: https://forum.strategickhaos.ai
- 🔒 Security: security@strategickhaos.ai

---

*"Configuration as Code. Sovereignty as Design."* ⚔️
