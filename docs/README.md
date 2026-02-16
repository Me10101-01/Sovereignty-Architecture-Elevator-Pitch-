# KhaosOS Documentation Index

Welcome to the KhaosOS documentation. This directory contains all technical documentation for the Sovereign Operating System Architecture.

---

## Quick Navigation

### 🚀 Getting Started

| Document | Purpose | Audience |
|----------|---------|----------|
| [QUICKSTART.md](../QUICKSTART.md) | Get up and running in 30 minutes | Beginners |
| [KHAOSOS_ARCHITECTURE.md](../KHAOSOS_ARCHITECTURE.md) | Complete architecture overview | Everyone |
| [HYPERVISOR_SETUP.md](HYPERVISOR_SETUP.md) | Detailed hypervisor setup guide | Intermediate |

### 📚 Core Documentation

| Document | Purpose | Last Updated |
|----------|---------|--------------|
| [SOVEREIGN_TOOL_STACK.md](SOVEREIGN_TOOL_STACK.md) | Complete reference for all 36 tools | 2025-12-07 |
| [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) | Timeline, milestones, and dependencies | 2025-12-07 |

### 🛠️ Technical Resources

| Resource | Location | Description |
|----------|----------|-------------|
| NixOS Configuration | [configs/nixos/](../configs/nixos/) | System configuration files |
| Docker Compose | [docker-compose/](../docker-compose/) | Service deployment configs |
| VM Setup Scripts | [scripts/vm-setup/](../scripts/vm-setup/) | Automated VM creation |

---

## Document Structure

```
docs/
├── README.md                      # This file
├── HYPERVISOR_SETUP.md           # Hypervisor installation guide
├── SOVEREIGN_TOOL_STACK.md       # Complete tool reference
└── IMPLEMENTATION_ROADMAP.md     # Project timeline

configs/
└── nixos/
    └── khaosos-configuration.nix  # NixOS system config

docker-compose/
├── khaossearch.yml               # Search engine deployment
└── khaosllm.yml                  # AI stack deployment

scripts/
└── vm-setup/
    ├── create-kali-vm.sh         # Kali Linux VM setup
    ├── create-parrot-vm.sh       # Parrot OS VM setup
    └── bootstrap-khaosos.sh      # KhaosOS bootstrap
```

---

## Documentation Standards

### File Naming

- Use `UPPERCASE_WITH_UNDERSCORES.md` for main documents
- Use `lowercase-with-hyphens.md` for supplementary docs
- Use descriptive names that indicate content

### Format

- Use Markdown for all documentation
- Include table of contents for docs > 500 lines
- Use code blocks with language specification
- Include diagrams where helpful (ASCII or Mermaid)

### Updates

- Update "Last Updated" date when modified
- Increment version numbers for major changes
- Document breaking changes clearly
- Keep changelog at bottom of major docs

---

## Contribution Guidelines

### Editing Documentation

1. Fork the repository
2. Create a branch: `docs/topic-name`
3. Make changes following standards above
4. Test all code examples
5. Submit pull request

### Adding New Documentation

1. Determine appropriate location
2. Follow naming conventions
3. Update this index
4. Cross-reference related docs
5. Submit for review

---

## Support

- **GitHub Issues:** For bugs and feature requests
- **Security:** security@strategickhaos.ai
- **General:** See [COMMUNITY.md](../COMMUNITY.md)

---

## License

All documentation is licensed under CC BY-SA 4.0 unless otherwise noted.

Code examples and configurations are licensed under MIT.

---

**Maintained by:** Strategickhaos DAO LLC  
**Version:** 1.0  
**Last Updated:** 2025-12-07
