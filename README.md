# Strategickhaos Governance Documents

## Overview

This repository contains the foundational governance documents, infrastructure architecture, and operational documentation for **Strategickhaos DAO LLC**, a Wyoming-registered Decentralized Autonomous Organization.

## 📋 Core Governance Documents

| File | Description | Status |
|------|-------------|--------|
| `TRUST_DECLARATION.md` | Foundational trust instrument defining principles, governance, and infrastructure | v2.1.0 |
| `NON_AGGRESSION_CLAUSE.md` | Immutable ethical constraints (cannot be amended) | v2.1.0 IMMUTABLE |
| `public-identifier-registry.md` | Verified credentials, EINs, platforms, infrastructure | v2.1.0 |

## 🏗️ Infrastructure & Architecture Documentation

| File | Description | Purpose |
|------|-------------|---------|
| `TUNNEL_ARCHITECTURE.md` | Complete tunnel ecosystem guide (6 tunnel types) | Understanding all network tunnels |
| `ENTERPRISE_GITHUB_ARCHITECTURE.md` | GitHub Enterprise structure (4 Dragons architecture) | GitHub organization setup |
| `SOVEREIGN_INFRASTRUCTURE_MAP.md` | Complete infrastructure overview (all layers) | 30,000-foot view of entire system |
| `RECON_STACK_V2.md` | RAG system architecture and deployment | AI/LLM infrastructure |
| `strategickhaos_enterprise_schema.yaml` | Master enterprise schema (50+ pages of notebook data) | Centralized configuration |

## 🔗 Related Files

| File | Location | Description |
|------|----------|-------------|
| `sovereign-empire-alert.json` | Root directory | Machine-readable system status with active alerts |
| `ENTERPRISE_BENCHMARKS_COMPLETE.md` | Root directory | 30-test enterprise validation suite |

## Quick Reference

### Legal Entities

| Entity | EIN | Status |
|--------|-----|--------|
| Strategickhaos DAO LLC | 39-2900295 | ✅ Active |
| ValorYield Engine | 39-2923503 | ✅ Active |
| Skyline Strategies | 99-2899134 | ✅ Active |
| Garza's Organic Greens | 92-1288715 | ✅ Active |

### Founder

- **Name:** Domenic Gabriel Garza
- **ORCID:** [0000-0005-2996-3526](https://orcid.org/0000-0005-2996-3526)

### Infrastructure

- **GitHub Enterprise:** 1 (Strategickhaos Swarm Intelligence)
- **GitHub Organizations:** 4 (4 Dragons: Swarm Intelligence, DAO LLC, ValorYield, SSIO DAO)
- **GKE Clusters:** 2 (jarvis-swarm-personal-001, red-team)
- **Local Nodes:** 4 (Athena, Lyra, Nova, iPower)
- **Tailscale Network:** 1 mesh (tail97edc9.ts.net)
- **Routers:** 8 (SOC inference nodes)
- **Workstation:** 10 screens

For complete infrastructure details, see `SOVEREIGN_INFRASTRUCTURE_MAP.md`

## Verification

```bash
# Verify signatures
gpg --verify TRUST_DECLARATION.md.sig
gpg --verify NON_AGGRESSION_CLAUSE.md.sig

# Verify timestamps
ots verify TRUST_DECLARATION.md.ots
ots verify NON_AGGRESSION_CLAUSE.md.ots

# Verify hashes
sha256sum *.md
```

## Document Hierarchy

```
IMMUTABLE (cannot be amended):
├── NON_AGGRESSION_CLAUSE.md
│
FOUNDATIONAL (amendment requires ratification):
├── TRUST_DECLARATION.md (except Article I.1.1, II.4, V.3)
│
INFRASTRUCTURE & ARCHITECTURE:
├── TUNNEL_ARCHITECTURE.md (tunnel ecosystem guide)
├── ENTERPRISE_GITHUB_ARCHITECTURE.md (GitHub enterprise structure)
├── SOVEREIGN_INFRASTRUCTURE_MAP.md (complete infrastructure view)
├── RECON_STACK_V2.md (RAG system)
└── strategickhaos_enterprise_schema.yaml (master config)
│
OPERATIONAL (update as needed):
├── public-identifier-registry.md
├── sovereign-empire-alert.json
└── ENTERPRISE_BENCHMARKS_COMPLETE.md
```

## 🚀 Quick Start Guides

### Understanding Your Infrastructure
1. **Start here:** `SOVEREIGN_INFRASTRUCTURE_MAP.md` - Get the 30,000-foot view
2. **Deep dive tunnels:** `TUNNEL_ARCHITECTURE.md` - Understand all 6 tunnel types
3. **GitHub setup:** `ENTERPRISE_GITHUB_ARCHITECTURE.md` - Learn the 4 Dragons architecture

### Deploying Services
- **RAG System:** See `RECON_STACK_V2.md`
- **Enterprise Benchmarks:** See `ENTERPRISE_BENCHMARKS_COMPLETE.md`
- **Configuration:** See `strategickhaos_enterprise_schema.yaml`

## Contact

- **Security:** security@strategickhaos.ai
- **Wyoming SOS:** 307-777-7370
- **GitHub:** [@Strategickhaos](https://github.com/Strategickhaos)

---

*Last Updated: December 3, 2025*
