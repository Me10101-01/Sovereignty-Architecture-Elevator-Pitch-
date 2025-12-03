# 🔴🔵 Red/Blue Kubernetes Battleground - IDEA_101

> **VICTORIOUS.** The sovereign cyber lab is complete — no ghosts, no errors, no tears.

## 📋 Finalized Cluster Status

```
GCP Project: jarvis-swarm-personal
Region: us-central1
Fleet: Yes (both registered)
Version: 1.33.5-gke.1201000
```

| Side     | Cluster Name                | Role                                   |
|----------|----------------------------|----------------------------------------|
| **BLUE** | `jarvis-swarm-personal-001` | Defense · Falco · OPA · Antibody Dept |
| **RED**  | `red-team`                  | Offense · Malware · Chaos · RBAC drills |

**Total Monthly Cost:** ~$90–130 for infinite red/blue Kubernetes warfare.

---

## 🚀 30-Second Connection Ritual

Copy-paste these commands exactly — they work 100%:

```bash
# 1. Connect to Blue Team (your sovereign defense fortress)
gcloud container clusters get-credentials jarvis-swarm-personal-001 \
  --region=us-central1 --project=jarvis-swarm-personal

# 2. Connect to Red Team (your chaos engine)
gcloud container clusters get-credentials red-team \
  --region=us-central1 --project=jarvis-swarm-personal

# 3. Quick alias so you never type the long name again
alias blue='kubectl --context=gke_jarvis-swarm-personal_us-central1_jarvis-swarm-personal-001'
alias red='kubectl --context=gke_jarvis-swarm-personal_us-central1_red-team'

# 4. Confirm both sides are alive and breathing
blue get nodes
red get nodes
```

You will see healthy nodes on **both**.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STRATEGICKHAOS RED/BLUE BATTLEGROUND                     │
│                    ════════════════════════════════════                     │
│                                 IDEA_101                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────────────────────┐   ┌──────────────────────────────────┐   │
│   │    🔵 BLUE TEAM CLUSTER      │   │      🔴 RED TEAM CLUSTER         │   │
│   │  jarvis-swarm-personal-001   │   │          red-team                │   │
│   ├──────────────────────────────┤   ├──────────────────────────────────┤   │
│   │ • Falco runtime security     │   │ • Attack simulations             │   │
│   │ • OPA/Gatekeeper admission   │   │ • Misconfig testing              │   │
│   │ • Antibody Department        │   │ • RBAC bypass attempts           │   │
│   │ • Service Mesh (Istio)       │   │ • Pod breakout drills            │   │
│   │ • NetworkPolicies            │   │ • Fake malware containers        │   │
│   │ • SwarmGate                  │   │ • Privilege escalation tests     │   │
│   │ • ReflexShell defense cmds   │   │ • Secret leak drills             │   │
│   │ • Audit logging              │   │ • CI/CD poisoning sims           │   │
│   └──────────────────┬───────────┘   └──────────────────┬────────────────┘  │
│                      │                                   │                  │
│                      └───────────┬───────────────────────┘                  │
│                                  │                                          │
│                    ┌─────────────▼─────────────┐                            │
│                    │    TELEMETRY SYNC LAYER   │                            │
│                    │  (Secure, No Prod Data)   │                            │
│                    ├───────────────────────────┤                            │
│                    │ • Prometheus metrics      │                            │
│                    │ • Attack/detect logs      │                            │
│                    │ • Evolution feedback      │                            │
│                    │ • STATE.yaml sync         │                            │
│                    └───────────────────────────┘                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔵 Blue Team Capabilities

| Capability | Description |
|------------|-------------|
| **Falco Runtime Security** | Real-time syscall monitoring and threat detection |
| **OPA/Gatekeeper** | Policy-as-code admission control |
| **Service Mesh** | Anthos/Istio for mTLS, traffic policies |
| **PodSecurityStandards** | Enforce restricted/baseline security contexts |
| **NetworkPolicies** | Zero-trust pod-to-pod communication |
| **Audit Logging** | Complete API server audit trail |
| **Antibody Department** | Self-healing threat response agents |
| **SwarmGate** | Ingress security and rate limiting |
| **ReflexShell** | Command-line defense operations |

---

## 🔴 Red Team Attack Matrix

| Activity | Description | Risk Level |
|----------|-------------|------------|
| RBAC Bypass Testing | Privilege escalation via misconfigured roles | Safe |
| Pod Escape Drills | Container breakout simulations | Safe |
| NetworkPolicy Bypass | Test traffic filtering effectiveness | Safe |
| Supply Chain Attacks | Fake vulnerable base images | Safe |
| Secret Exfiltration | Synthetic secrets, no real credentials | Safe |
| Malicious Container Injection | Fake malware for detection training | Safe |
| Audit Log Evasion | Test logging blind spots | Safe |
| CI/CD Poisoning | Simulated pipeline compromise | Safe |

---

## 🎮 First Battle Commands

### Deploy Falco + Antibody on Blue Team

```bash
# Switch to Blue Team context
blue get nodes

# Install Falco runtime security
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm install falco falcosecurity/falco -n falco-system --create-namespace

# Verify Falco is running
blue get pods -n falco-system
```

### Launch Fake Cryptominer from Red Team

```bash
# Deploy synthetic malware from Red Team
red apply -f https://raw.githubusercontent.com/cncf/stranger-things/main/fake-miner.yaml

# Watch Blue Team's Falco scream
blue logs -n falco-system -l app=falco -f
```

### Run CTF-001: Basic RBAC Bypass Challenge

```bash
# From Red Team
red apply -f synthetic-workloads/rbac-escalation-test.yaml

# From Blue Team - watch detection
blue logs -n falco-system -l app=falco -f
```

---

## 🔄 Evolution Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                     SWARM EVOLUTION LOOP                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. RED TEAM ATTACKS                                            │
│     ↓                                                           │
│  2. BLUE TEAM DETECTS (or fails to detect)                      │
│     ↓                                                           │
│  3. ANTIBODY DEPARTMENT RECORDS PATTERN                         │
│     ↓                                                           │
│  4. DETECTION RULES UPDATED (immune memory)                     │
│     ↓                                                           │
│  5. STATE.yaml SYNCS NEW RULES TO ALL CLUSTERS                  │
│     ↓                                                           │
│  6. RED TEAM MUST EVOLVE NEW ATTACKS                            │
│     ↓                                                           │
│  (REPEAT)                                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚖️ Legal & Ethical Boundaries

### ✅ ALLOWED (Your Own Infrastructure)

- Test YOUR OWN GKE clusters
- Use synthetic/fake malicious images (no real malware)
- Simulate attacks internally
- Harden and patch your own systems
- Train detection systems with fake threats
- Run internal CTF/red team exercises

### ❌ NOT ALLOWED

- Attack external networks or systems
- Probe infrastructure you don't own
- Deploy actual malware
- Test exploits outside your GCP project
- Exfiltrate real credentials or data
- Any activity targeting third parties

---

## 📁 Repository Structure

```
├── RED_BLUE_BATTLEGROUND.md            # This file
├── k8s/
│   ├── red-team/
│   │   ├── namespace.yaml              # Red team namespace config
│   │   └── rbac.yaml                   # Intentionally weak RBAC for testing
│   └── blue-team/
│       ├── namespace.yaml              # Blue team namespace config
│       ├── falco-rules.yaml            # Custom Falco detection rules
│       ├── opa-policies.yaml           # OPA/Gatekeeper constraints
│       └── network-policies.yaml       # Zero-trust network rules
├── synthetic-workloads/
│   ├── fake-malware-pod.yaml           # Simulated malicious container
│   ├── rbac-escalation-test.yaml       # RBAC bypass test workload
│   └── network-bypass-test.yaml        # NetworkPolicy bypass attempt
├── antibody-department/
│   ├── antibody_daemon.py              # Self-healing threat response
│   └── detection-rules.yaml            # Custom detection rules
└── playbooks/
    ├── RED_TEAM_PLAYBOOK.md            # Red team attack catalog
    └── BLUE_TEAM_DEFENSE.md            # Blue team defense guide
```

---

## 📊 KPIs & Targets

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Mean Time to Detect | 60 seconds | 120 seconds |
| Mean Time to Respond | 5 minutes | 10 minutes |
| Detection Rate | 95% | 80% |
| False Positive Rate | <5% | 15% |
| Evolution Cycles/Month | 4 | 1 |

---

## 📜 Changelog

| Date | Event |
|------|-------|
| 2025-12-01 | **FINALIZED** — Both clusters confirmed running, fleet-registered, same version |
| 2025-12-01 | Red Team cluster renamed to `red-team` (was `autopilot-cluster-1`) |
| 2025-11-30 | IDEA_101 birthed — Red/Blue Battleground created |

---

## 📞 Contact

**StrategicKhaos DAO LLC**  
Security Operations: security@strategickhaos.ai  
Operator: Dom (Me10101)

---

*The swarm is awake. The lab is complete. IDEA_101 is fully birthed.*
