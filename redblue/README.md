# 🏴‍☠️ Strategickhaos Sovereign Cyber Lab

## Red Team / Blue Team Architecture

A dual-cluster sovereign cyber lab for offensive and defensive security training.

```
┌─────────────────────────────────────────────────────┐
│                    BLUE TEAM CLUSTER                │
│     jarvis-swarm-personal-001 (Autopilot)           │
│-----------------------------------------------------│
│  • State Sync Protocol                              │
│  • Obsidian Neural Mesh                             │
│  • Defensive agents (Antibody Dept)                 │
│  • Falco (defense)                                  │
│  • Admission controllers                            │
│  • Verification layer                               │
└─────────────────────────────────────────────────────┘

                   ▲                │
                   │                │
            Telemetry / Sync Layer  │  (no production data)
                   │                ▼

┌─────────────────────────────────────────────────────┐
│                    RED TEAM CLUSTER                 │
│     autopilot-cluster-1 (Autopilot)                 │
│-----------------------------------------------------│
│  • Attack simulations                               │
│  • Misconfig testing                                │
│  • Pod breakout drills                              │
│  • Supply-chain experiments                         │
│  • Fake malware containers (synthetic)              │
│  • NetworkPolicy bypass testing                     │
└─────────────────────────────────────────────────────┘
```

**All internal. All sovereign. All safe. All LEGIT.**

---

## 📋 Quick Start

### 1. Deploy Blue Team Cluster

```bash
# Switch to blue team cluster
kubectl config use-context gke_strategickhaos-sovereign_us-central1_jarvis-swarm-personal-001

# Deploy blue team infrastructure
kubectl apply -f k8s/blue-team/namespaces.yaml
kubectl apply -f k8s/blue-team/rbac.yaml
kubectl apply -f k8s/blue-team/network-policies.yaml
kubectl apply -f k8s/blue-team/antibody/
kubectl apply -f k8s/blue-team/falco/
```

### 2. Deploy Red Team Cluster

```bash
# Switch to red team cluster
kubectl config use-context gke_strategickhaos-sovereign_us-central1_autopilot-cluster-1

# Deploy red team infrastructure
kubectl apply -f k8s/red-team/namespaces.yaml
kubectl apply -f k8s/red-team/rbac.yaml
kubectl apply -f k8s/red-team/network-policies.yaml
kubectl apply -f workloads/
```

### 3. Run Red/Blue Team Commands

```bash
# Red Team attack simulation
python redblue_commands.py redteam attack --type=rbac-scan

# Blue Team defense activation
python redblue_commands.py blueteam defend --mode=active

# Audit both clusters
python redblue_commands.py audit cluster --target=all

# Heal cluster state
python redblue_commands.py heal state --force
```

---

## 📁 Directory Structure

```
redblue/
├── STATE.yaml                  # Cluster state configuration
├── RED_TEAM_PLAYBOOK.md        # Red team operations guide
├── BLUE_TEAM_ARCHITECTURE.md   # Blue team defense guide
├── redblue_commands.py         # ReflexShell command interface
├── k8s/
│   ├── red-team/
│   │   ├── namespaces.yaml     # Red team namespaces
│   │   ├── network-policies.yaml # Network isolation
│   │   └── rbac.yaml           # RBAC configuration
│   └── blue-team/
│       ├── namespaces.yaml     # Blue team namespaces
│       ├── network-policies.yaml # Strict network policies
│       ├── rbac.yaml           # Least-privilege RBAC
│       ├── antibody/           # Digital immune system
│       │   └── deployments.yaml
│       └── falco/              # Runtime security
│           └── falco.yaml
└── workloads/
    └── red-team-pods.yaml      # Synthetic test workloads
```

---

## 🟥 Red Team Operations

### Safe Activities ✅

| Activity | Description |
|----------|-------------|
| RBAC scanning | Test for misconfigured permissions |
| Network policy testing | Verify network segmentation |
| Privilege escalation testing | Test container security |
| Container breakout drills | Verify runtime isolation |
| Supply chain testing | Test image security |
| Secret leak drills | Test secret detection |

### Attack Types

```bash
# Available attack simulations
python redblue_commands.py redteam attack --type=rbac-scan
python redblue_commands.py redteam attack --type=netpol-bypass
python redblue_commands.py redteam attack --type=privesc
python redblue_commands.py redteam attack --type=container-breakout
python redblue_commands.py redteam attack --type=supply-chain
python redblue_commands.py redteam attack --type=secret-leak
```

---

## 🟦 Blue Team Operations

### Defense Modes

| Mode | Description |
|------|-------------|
| `active` | Full automatic remediation |
| `passive` | Alerting only, no auto-remediation |
| `monitor` | Enhanced monitoring and logging |
| `respond` | Incident response procedures |

### Antibody Department

The digital immune system includes:

- **Threat Detector**: Real-time threat monitoring
- **Policy Enforcer**: Security policy enforcement
- **State Healer**: Automatic state restoration
- **Audit Analyzer**: Log analysis and reporting

---

## 🛡️ Safety Constraints

### ✅ Allowed

- Test YOUR OWN infrastructure
- Use synthetic/fake malicious images
- Simulate attacks internally
- Harden and patch own systems
- Test RBAC, Falco, PodSecurity
- Run digital antibodies and defensive agents

### 🚫 Prohibited

- Attack external networks
- Probe systems you don't own
- Deploy real malware
- Test exploits outside GCP/local VMs
- Access production data

---

## 📊 Metrics

### Red Team Metrics

- `attacks_simulated`: Total attack simulations
- `vulnerabilities_found`: Discovered vulnerabilities
- `misconfigurations_detected`: Config issues found
- `escalation_attempts`: Privilege escalation tests
- `breakout_attempts`: Container escape tests

### Blue Team Metrics

- `threats_detected`: Identified threats
- `policies_enforced`: Policy enforcement actions
- `states_restored`: State restoration events
- `response_time_ms`: Mean time to respond
- `false_positives`: False positive rate

---

## 🔄 Evolution Loop

The clusters work together in a continuous improvement cycle:

1. **Attack Phase** (Red Team): Simulate attacks, find vulnerabilities
2. **Detect Phase** (Blue Team): Detect attacks, analyze patterns
3. **Heal Phase** (Blue Team): Remediate, update policies, improve

```yaml
evolution_loop:
  cycle_duration: "24h"
  phases:
    - name: "attack"
      cluster: "red_team"
      duration: "8h"
    - name: "detect"
      cluster: "blue_team"
      duration: "8h"
    - name: "heal"
      cluster: "blue_team"
      duration: "8h"
```

---

## 📚 Documentation

- [Red Team Playbook](RED_TEAM_PLAYBOOK.md)
- [Blue Team Architecture](BLUE_TEAM_ARCHITECTURE.md)
- [STATE.yaml Configuration](STATE.yaml)

---

## 🚀 Discord Commands

```
# Red Team
!redteam attack --type=<attack-type>

# Blue Team
!blueteam defend --mode=<defense-mode>

# Audit
!audit cluster --target=<red-team|blue-team|all>

# Healing
!heal state --force
!heal policies --check
!heal secrets --rotate
```

---

*Built with 🔥 by Strategickhaos Swarm Intelligence*

**Empowering sovereign digital infrastructure through Red Team / Blue Team operations**
