# Strategickhaos Governance Documents

## Overview

This directory contains the foundational governance documents for **Strategickhaos DAO LLC**, a Wyoming-registered Decentralized Autonomous Organization.

## Documents

| File | Description | Status |
|------|-------------|--------|
| `TRUST_DECLARATION.md` | Foundational trust instrument defining principles, governance, and infrastructure | v2.1.0 |
| `NON_AGGRESSION_CLAUSE.md` | Immutable ethical constraints (cannot be amended) | v2.1.0 IMMUTABLE |
| `AUTONOMOUS_OPERATION_LICENSE.md` | Pre-authorized AI action framework and autonomy grant | v1.0 |
| `public-identifier-registry.md` | Verified credentials, EINs, platforms, infrastructure | v2.1.0 |

## Related Files

| File | Location | Description |
|------|----------|-------------|
| `sovereign-empire-alert.json` | `../schemas/` | Machine-readable system status with active alerts |
| `governance/aol_action_matrix.yaml` | `governance/` | AOL action classification and risk levels |
| `governance/aol_circuit_breakers.yaml` | `governance/` | AOL circuit breaker configurations |
| `governance/aol_trust_tiers.yaml` | `governance/` | AOL trust tier definitions and assignments |
| `governance/aol_audit_schema.yaml` | `governance/` | AOL audit log schema and requirements |
| `governance/AOL_QUICK_REFERENCE.md` | `governance/` | AOL quick reference card for AI agents |
| `governance/aol_implementation_status.yaml` | `governance/` | AOL implementation progress tracker |

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

- **GKE Clusters:** 2 (jarvis-swarm-personal-001, autopilot-cluster-1)
- **Local Nodes:** 4 (Athena, Lyra, Nova, iPower)
- **Routers:** 8 (SOC inference nodes)

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
OPERATIONAL (governance frameworks):
├── AUTONOMOUS_OPERATION_LICENSE.md
├── ai_constitution.yaml
├── governance/aol_*.yaml
│
OPERATIONAL (update as needed):
├── public-identifier-registry.md
├── auto_approve_config.yaml
└── sovereign-empire-alert.json
```

## Contact

- **Security:** security@strategickhaos.ai
- **Wyoming SOS:** 307-777-7370
- **GitHub:** [@Strategickhaos](https://github.com/Strategickhaos)

---

*Last Updated: December 3, 2025*
