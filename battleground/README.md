# 🟥🟦 IDEA_101: Red/Blue Kubernetes Battleground

> **Dual-Cluster Sovereign Cyber Lab for StrategicKhaos DAO LLC**

A legitimate, internal security research and training infrastructure using two GKE Autopilot clusters — one for offensive simulations (Red Team), one for defensive operations (Blue Team).

---

## 🎯 Mission

Build a **risk-free, sovereign security evolution loop** where:
- Red Team attacks synthetic targets to discover weaknesses
- Blue Team defends, monitors, and hardens infrastructure
- Both teams learn and evolve through continuous engagement
- All activities are **internal**, **controlled**, and **compliant**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STRATEGICKHAOS CYBER LAB                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌───────────────────────────────────┐   ┌───────────────────────────────┐ │
│   │       🟦 BLUE TEAM CLUSTER        │   │       🟥 RED TEAM CLUSTER     │ │
│   │     jarvis-swarm-personal-001     │   │      autopilot-cluster-1      │ │
│   │            (DEFENDER)             │   │           (ATTACKER)          │ │
│   ├───────────────────────────────────┤   ├───────────────────────────────┤ │
│   │ • State Sync Protocol             │   │ • Attack simulations          │ │
│   │ • Obsidian Neural Mesh            │   │ • Misconfig testing           │ │
│   │ • Antibody Department             │   │ • RBAC bypass attempts        │ │
│   │ • Falco (threat detection)        │   │ • Pod breakout drills         │ │
│   │ • OPA admission controllers       │   │ • Supply-chain experiments    │ │
│   │ • Service Mesh (Anthos/Istio)     │   │ • NetworkPolicy bypass tests  │ │
│   │ • SwarmGate                       │   │ • Fake malware containers     │ │
│   │ • ReflexShell (defense cmds)      │   │ • Privilege escalation tests  │ │
│   │ • Audit logging                   │   │ • Secret leak drills          │ │
│   │ • Integrity verification          │   │ • CI/CD poisoning sims        │ │
│   └──────────────────┬────────────────┘   └──────────────────┬────────────┘ │
│                      │                                       │              │
│                      └───────────┬───────────────────────────┘              │
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
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔴 Red Team Cluster: `autopilot-cluster-1`

**Purpose:** A sandbox for offensive security research and attack simulations.

### Allowed Activities

| Activity | Description | Risk Level |
|----------|-------------|------------|
| RBAC Bypass Testing | Attempt privilege escalation via misconfigured roles | Safe |
| Pod Escape Drills | Container breakout simulations | Safe |
| NetworkPolicy Bypass | Test traffic filtering effectiveness | Safe |
| Supply Chain Attacks | Fake vulnerable base images | Safe |
| Secret Exfiltration | Synthetic secrets, no real credentials | Safe |
| Malicious Container Injection | Fake malware for detection training | Safe |
| Audit Log Evasion | Test logging blind spots | Safe |
| CI/CD Poisoning | Simulated pipeline compromise | Safe |

### Why Autopilot is Perfect for Red Team

- Nodes are **managed** — you can't destroy the underlying infrastructure
- Workloads are **isolated** — attack experiments don't affect production
- **Cost-efficient** — scales to zero when not in use
- **Same architecture** as Blue Team — realistic attack surface

---

## 🔵 Blue Team Cluster: `jarvis-swarm-personal-001`

**Purpose:** Production-style defensive infrastructure with full governance.

### Capabilities

| Capability | Description |
|------------|-------------|
| Falco Runtime Security | Real-time syscall monitoring and threat detection |
| OPA/Gatekeeper | Policy-as-code admission control |
| Service Mesh | Anthos/Istio for mTLS, traffic policies |
| PodSecurityStandards | Enforce restricted/baseline security contexts |
| NetworkPolicies | Zero-trust pod-to-pod communication |
| Audit Logging | Complete API server audit trail |
| Antibody Department | Self-healing threat response agents |
| SwarmGate | Ingress security and rate limiting |
| ReflexShell | Command-line defense operations |

---

## 📁 Repository Structure

```
repos/red-blue-battleground/
├── README.md                          # This file
├── STATE-redblue.yaml                 # Red/Blue state sync extension
├── playbooks/
│   ├── RED_TEAM_PLAYBOOK.md          # Complete red team attack catalog
│   └── BLUE_TEAM_DEFENSE.md          # Complete blue team defense guide
├── synthetic-workloads/
│   ├── fake-malware-pod.yaml         # Simulated malicious container
│   ├── rbac-escalation-test.yaml     # RBAC bypass test workload
│   ├── secret-leak-drill.yaml        # Synthetic secret exfiltration
│   ├── network-bypass-test.yaml      # NetworkPolicy bypass attempt
│   └── supply-chain-vuln.yaml        # Fake vulnerable image
├── antibody-department/
│   ├── README.md                      # Antibody Department overview
│   ├── antibody-daemon.py            # Self-healing threat response
│   ├── detection-rules.yaml          # Falco/custom detection rules
│   └── immune-memory.yaml            # Learned threat patterns
├── reflexshell/
│   ├── redteam_commands.py           # !redteam attack commands
│   ├── blueteam_commands.py          # !blueteam defend commands
│   └── battleground_commands.py      # !audit, !heal, !sync commands
└── k8s/
    ├── red-team/
    │   ├── namespace.yaml            # Red team namespace config
    │   └── rbac.yaml                 # Intentionally weak RBAC
    └── blue-team/
        ├── namespace.yaml            # Blue team namespace config
        ├── falco-rules.yaml          # Custom Falco rules
        ├── opa-policies.yaml         # OPA/Gatekeeper constraints
        └── network-policies.yaml     # Zero-trust network rules
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

## 🚀 Quick Start

### Prerequisites

```bash
# Authenticate to GCP
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Get cluster credentials
gcloud container clusters get-credentials jarvis-swarm-personal-001 --zone us-central1
gcloud container clusters get-credentials autopilot-cluster-1 --zone us-central1
```

### Deploy Blue Team Defenses

```bash
# Apply Falco
helm install falco falcosecurity/falco -n falco-system --create-namespace \
  -f k8s/blue-team/falco-rules.yaml

# Apply OPA/Gatekeeper
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.14/deploy/gatekeeper.yaml
kubectl apply -f k8s/blue-team/opa-policies.yaml

# Apply NetworkPolicies
kubectl apply -f k8s/blue-team/network-policies.yaml
```

### Run Red Team Exercise

```bash
# Switch to red team cluster
kubectl config use-context autopilot-cluster-1

# Deploy synthetic attack workload
kubectl apply -f synthetic-workloads/rbac-escalation-test.yaml

# Monitor from blue team perspective
kubectl config use-context jarvis-swarm-personal-001
kubectl logs -n falco-system -l app=falco -f
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

## 📊 Telemetry & Metrics

| Metric | Source | Purpose |
|--------|--------|---------|
| Attack attempts | Red Team logs | Track simulation coverage |
| Detection rate | Falco alerts | Measure defense effectiveness |
| MTTD (Mean Time to Detect) | Blue Team metrics | Optimize response time |
| False positive rate | Falco/OPA logs | Tune detection rules |
| Policy violations | OPA audit | Track compliance drift |
| Evolution cycles | STATE.yaml commits | Measure improvement velocity |

---

## 🛠️ Integration Points

- **IDEA_100 (CPA Sentinel):** Receives security alerts from both clusters
- **AI Board:** Approves major attack scenarios and defense changes
- **NATS:** Cross-cluster event messaging
- **Qdrant:** Vector storage for attack pattern embeddings
- **STATE.yaml:** Unified state management across Red/Blue

---

## 📜 Changelog

| Date | Event |
|------|-------|
| 2025-11-30 | IDEA_101 birthed — Red/Blue Battleground created |
| 2025-11-30 | GCP infrastructure identified: jarvis-swarm-personal-001 (Blue), autopilot-cluster-1 (Red) |

---

## 📞 Contact

**StrategicKhaos DAO LLC**  
Security Operations: security@strategickhaos.ai  
Operator: Dom (Me10101)

---

*"Your own infrastructure, your own nodes, your own experimental environment, and non-malicious synthetic tests — completely within security best practices."*
