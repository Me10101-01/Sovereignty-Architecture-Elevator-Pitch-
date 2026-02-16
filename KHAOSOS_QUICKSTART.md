# KhaosOS Quick Reference Guide
## One-Page Reference for the Sovereign Operating System

**Version:** 1.0 TORUK | **Updated:** 2025-12-07

---

## 📚 DOCUMENTATION MAP

```
├── KHAOSOS_ARCHITECTURE.md       Main architecture specification (370 lines)
├── KHAOSOS_ROADMAP.md            Implementation timeline (501 lines)  
├── QUEEN_CLI.md                  Command reference (518 lines)
├── configs/nixos/                NixOS configuration files
│   ├── khaosos-configuration.nix  Declarative system config
│   └── README.md                  Installation guide
├── docker-compose.khaossearch.yml Self-hosted search engine
└── deploy-khaossearch.sh         Quick deployment script
```

---

## 🚀 QUICK DEPLOYMENT COMMANDS

```bash
# 1. Deploy KhaosSearch (takes 2 minutes)
./deploy-khaossearch.sh
# Access: http://localhost:8888

# 2. Install KhaosOS on NixOS
sudo cp configs/nixos/khaosos-configuration.nix /etc/nixos/configuration.nix
sudo nixos-rebuild switch

# 3. Deploy specific tool
docker-compose -f docker-compose.khaossearch.yml up -d

# 4. Check Queen CLI status
queen status --all
```

---

## 🛡️ THE 36-TOOL SOVEREIGN STACK

### ✅ Operational (9 tools)
- KhaosCloud, KhaosNet, KhaosLLM, KhaosVector, KhaosTreasury
- KhaosAudit, KhaosGov, KhaosCompliance, KhaosVPN

### 🔄 In Progress (3 tools)
- KhaosBase, KhaosAgent, KhaosTrader

### 📋 Planned (24 tools)
- All Tier 1-5 tools (see KHAOSOS_ARCHITECTURE.md for full list)

---

## 🔧 HYPERVISOR RECOMMENDATIONS

| Use Case | Hypervisor | Why |
|----------|-----------|-----|
| **Development** | VirtualBox | Free, easy snapshots |
| **Production** | Proxmox VE | Type-1, dedicated hardware |
| **KhaosOS Native** | QEMU/KVM | Best Linux performance |

---

## 📅 IMPLEMENTATION TIMELINE

```
Phase 0 (Week 1)      → VMs & Foundation
Phase 1 (Weeks 2-4)   → KhaosOS Alpha Build
Phase 2 (Weeks 5-12)  → Tool Integration
Phase 3 (Weeks 13-16) → Security Hardening
Phase 4 (Weeks 17-26) → Full Sovereignty
```

**Current Status:** Phase 0 - Specifications Complete

---

## 💰 COST COMPARISON

| Stack | Annual Cost | Vendor Lock-in |
|-------|-------------|----------------|
| **Current Vendors** | $1,000+ | ⚠️ CRITICAL |
| **Sovereign Stack** | $260 | ✅ ZERO |
| **Savings** | **74%** | **+FREEDOM** |

---

## 🎯 SUCCESS METRICS

- [x] Specifications complete
- [ ] Vendor dependencies: 0 in critical path
- [ ] Data sovereignty: 100%
- [ ] Reproducibility: 100% (`nixos-rebuild` succeeds)
- [ ] Air-gap capable: Yes
- [ ] 24-hour data export: All data

---

## 🔐 SECURITY FEATURES

### NixOS Hardening
- Hardened kernel with security sysctls
- Default-deny firewall
- BPF JIT hardening
- Kernel pointer protection
- Automatic security updates

### Network Security
- WireGuard mesh VPN
- Tailscale for easy mesh
- Connection rate limiting
- Invalid packet dropping

### Authentication
- GPG-signed everything
- SSH key-only (no passwords)
- YubiKey support
- Multi-factor for critical ops

---

## 🌐 KHAOSSEARCH FEATURES

- **Meta-search:** Google + DuckDuckGo + Brave + Bing
- **Privacy:** No tracking, no cookies, no data collection
- **Tor routing:** Optional anonymous queries
- **Self-hosted:** Search history never leaves your server
- **Custom ranking:** Boost/penalize sources programmatically

**Deployment:** `./deploy-khaossearch.sh`

---

## 👑 QUEEN CLI TOP COMMANDS

```bash
# Status checks
queen status                          # All systems
queen status --treasury               # Financial health

# Deployments
queen deploy <service>                # Deploy service
queen rollback <service> <version>    # Rollback
queen scale <service> --replicas 3    # Scale

# Security
queen chaos --inject <failure>        # Chaos engineering
queen audit --export json             # Security audit

# Treasury
queen treasury --balance              # View balance
queen treasury --distribute 7%        # Charity distribution

# AI Board
queen board --vote "<proposal>"       # Submit vote
queen board --consensus               # Check consensus
```

---

## 📦 NIXOS PACKAGE HIGHLIGHTS

### Core Tools
`git` `gnupg` `age` `wireguard-tools` `tailscale` `tor`

### Development
`docker` `kubectl` `k9s` `helm` `terraform` `ansible`

### Languages
`nodejs` `python` `go` `rust`

### Security
`nmap` `wireshark` `tcpdump` `nftables`

### AI/ML
`ollama` (with Qwen2.5:72b, Llama3.2:70b, CodeLlama:34b)

---

## 🔍 WHERE TO FIND ANSWERS

| Question | Document | Section |
|----------|----------|---------|
| "What is KhaosOS?" | KHAOSOS_ARCHITECTURE.md | Executive Summary |
| "How do I install it?" | configs/nixos/README.md | Installation |
| "What tools are included?" | KHAOSOS_ARCHITECTURE.md | 36-Tool Stack |
| "When will it be ready?" | KHAOSOS_ROADMAP.md | Timeline |
| "How do I use Queen CLI?" | QUEEN_CLI.md | Command Reference |
| "How much will it cost?" | KHAOSOS_ARCHITECTURE.md | Cost Analysis |
| "Is it secure?" | configs/nixos/README.md | Security Features |

---

## 🆘 TROUBLESHOOTING

### KhaosSearch won't start
```bash
# Check logs
docker-compose -f docker-compose.khaossearch.yml logs

# Restart services
docker-compose -f docker-compose.khaossearch.yml restart

# Check .env file exists
ls -la searxng/.env
```

### NixOS rebuild fails
```bash
# Check configuration syntax
nix-instantiate --parse /etc/nixos/configuration.nix

# Rollback to previous generation
sudo nixos-rebuild switch --rollback

# Check logs
journalctl -xe
```

### Queen CLI not working
```bash
# Verify GPG configuration
queen config verify

# Check server connectivity
ping queen.strategickhaos.ai

# Test with direct mode
queen config set privacy-mode direct
```

---

## 📞 SUPPORT CHANNELS

- 📖 **Documentation:** All .md files in this repository
- 🐛 **Issues:** GitHub Issues
- 💬 **Forum:** https://forum.strategickhaos.ai
- 🔒 **Security:** security@strategickhaos.ai

---

## 🎓 LEARNING PATH

### Week 1: Understand the Vision
Read KHAOSOS_ARCHITECTURE.md, understand the 36-tool stack

### Week 2: Try KhaosSearch
Deploy with `./deploy-khaossearch.sh`, use it for a week

### Week 3: Explore NixOS
Read configs/nixos/README.md, try in VM

### Week 4: Plan Your Migration
Review KHAOSOS_ROADMAP.md, identify your vendor dependencies

---

## 🔑 KEY PRINCIPLES

1. **Own the Stack** - No vendor lock-in in critical path
2. **Own the Data** - 100% data sovereignty
3. **Own the Destiny** - Reproducible, declarative configuration
4. **Air-gap Capable** - Function without internet connectivity
5. **24-hour Export** - All data exportable in one day
6. **Security First** - Hardened by default, zero trust

---

## 🏆 ACHIEVEMENT UNLOCKED

✅ **Specifications Complete** - All architecture documented  
✅ **Configurations Ready** - NixOS config tested and verified  
✅ **Deployment Scripts** - Quick start automation ready  
✅ **Documentation** - 1,389 lines of comprehensive docs  

**Next:** Begin Phase 1 implementation (see KHAOSOS_ROADMAP.md)

---

*"The best time to achieve sovereignty was 10 years ago. The second best time is now."* ⚔️🔥

**Status:** READY FOR EXECUTION | **Codename:** TORUK
