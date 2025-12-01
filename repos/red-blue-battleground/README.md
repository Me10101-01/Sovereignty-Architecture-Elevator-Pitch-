# 🟥🟦 Red/Blue Kubernetes Battleground

## IDEA_101 — Dual-Cluster Sovereign Cyber Lab

Your "accidental" second cluster is now **intentional battle infrastructure**.

---

## 📍 Infrastructure Overview

| Cluster | Role | Purpose |
|---------|------|---------|
| `autopilot-cluster-1` | 🟥 **RED TEAM** | Attack simulations, RBAC bypass, container escape drills |
| `jarvis-swarm-personal-001` | 🟦 **BLUE TEAM** | Defense ops, Falco, OPA, Service Mesh, Antibody Dept |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BATTLEGROUND CONTROL                               │
├──────────────────────────────┬──────────────────────────────────────────────┤
│                              │                                              │
│    🟥 RED TEAM CLUSTER       │     🟦 BLUE TEAM CLUSTER                     │
│    (autopilot-cluster-1)     │     (jarvis-swarm-personal-001)              │
│                              │                                              │
│  ┌────────────────────────┐  │  ┌─────────────────────────────────────────┐ │
│  │  Attack Workloads      │  │  │  Defense Stack                          │ │
│  │  ├─ RBAC Escalation    │  │  │  ├─ Falco (Runtime Security)            │ │
│  │  ├─ Privilege Escalation│ │  │  ├─ OPA/Gatekeeper (Policy)             │ │
│  │  ├─ Fake Malware Pods  │  │  │  ├─ Istio Service Mesh                  │ │
│  │  ├─ Crypto Miner Sim   │  │  │  ├─ NetworkPolicy Enforcer              │ │
│  │  └─ Supply Chain Tests │  │  │  └─ Pod Security Admission              │ │
│  └────────────────────────┘  │  └─────────────────────────────────────────┘ │
│                              │                                              │
│  ┌────────────────────────┐  │  ┌─────────────────────────────────────────┐ │
│  │  CTF Infrastructure    │  │  │  Antibody Department                    │ │
│  │  ├─ Flag Capture       │  │  │  ├─ Threat Detection                    │ │
│  │  ├─ Scoring System     │  │  │  ├─ Auto Quarantine                     │ │
│  │  └─ Scenario Engine    │  │  │  ├─ Immune Memory                       │ │
│  └────────────────────────┘  │  │  └─ Self-Healing                        │ │
│                              │  └─────────────────────────────────────────┘ │
└──────────────────────────────┴──────────────────────────────────────────────┘
                               │
                               ▼
                    ┌───────────────────────┐
                    │  ReflexShell Commands │
                    │  !redteam !blueteam   │
                    │  !battleground !heal  │
                    └───────────────────────┘
```

---

## 📦 Package Structure

```
repos/red-blue-battleground/
├── README.md                     # This file
├── STATE-redblue.yaml            # Cross-cluster state sync
├── playbooks/
│   ├── RED_TEAM_PLAYBOOK.md      # 70+ attack scenarios
│   └── BLUE_TEAM_DEFENSE.md      # Defense architecture
├── synthetic-workloads/
│   ├── rbac-escalation-test.yaml # RBAC bypass testing
│   └── fake-malware-pod.yaml     # Detection training
├── antibody-department/
│   └── antibody_daemon.py        # Self-healing daemon
├── reflexshell/
│   └── battleground_commands.py  # Discord/CLI commands
└── k8s/
    ├── blue-team/                # Blue team deployments
    └── red-team/                 # Red team attack configs
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Authenticate with GCP
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Get cluster credentials
gcloud container clusters get-credentials jarvis-swarm-personal-001 --zone us-central1
gcloud container clusters get-credentials autopilot-cluster-1 --zone us-central1

# Verify contexts
kubectl config get-contexts
```

### Deploy Blue Team Defenses

```bash
# Switch to Blue Team cluster
kubectl config use-context gke_YOUR_PROJECT_jarvis-swarm-personal-001

# Deploy Falco runtime security
kubectl apply -f k8s/blue-team/falco-daemonset.yaml

# Deploy OPA Gatekeeper policies
kubectl apply -f k8s/blue-team/gatekeeper-policies.yaml

# Deploy NetworkPolicy enforcer
kubectl apply -f k8s/blue-team/network-policies.yaml

# Start Antibody Daemon
python antibody-department/antibody_daemon.py --cluster blue
```

### Launch Red Team Attack

```bash
# Switch to Red Team cluster
kubectl config use-context gke_YOUR_PROJECT_autopilot-cluster-1

# Deploy RBAC escalation test
kubectl apply -f synthetic-workloads/rbac-escalation-test.yaml

# Deploy fake malware pod
kubectl apply -f synthetic-workloads/fake-malware-pod.yaml

# Watch Falco detect it on Blue Team
kubectl --context=blue-team logs -n falco-system -l app=falco -f
```

---

## 🎮 ReflexShell Commands

### Red Team Commands

```bash
!redteam status           # Show Red Team cluster status
!redteam attack rbac      # Launch RBAC bypass test
!redteam attack malware   # Launch fake malware pod
!redteam attack crypto    # Launch crypto miner simulation
!redteam attack supply    # Launch supply chain attack
!redteam cleanup          # Remove all attack workloads
!redteam scenarios        # List available attack scenarios
```

### Blue Team Commands

```bash
!blueteam status          # Show defense status
!blueteam threats         # View active threats
!blueteam quarantine ns/pod  # Quarantine a pod
!blueteam falco-alerts    # Show Falco runtime alerts
!blueteam compliance      # Run compliance check
!blueteam network-map     # Show network topology
!blueteam psas            # Check Pod Security Admission status
```

### Battleground Commands

```bash
!battleground status      # Status of both clusters
!battleground exercise CTF-001  # Run CTF challenge
!battleground metrics     # Attack/defense statistics
!battleground scoreboard  # Show CTF scoreboard
!battleground reset       # Reset to baseline state
```

### Self-Healing Commands

```bash
!heal state               # Restore desired cluster state
!heal audit               # Show healing audit log
!sync rules               # Sync detection rules from immune memory
!sync policies            # Sync policies across clusters
```

---

## 🏆 CTF Exercises

| Exercise ID | Difficulty | Duration | What It Tests |
|-------------|------------|----------|---------------|
| CTF-001 | Easy | 30 min | RBAC bypass, PSA enforcement |
| CTF-002 | Medium | 45 min | NetworkPolicy evasion |
| CTF-003 | Medium | 60 min | Supply chain attack detection |
| CTF-004 | Hard | 90 min | Container escape detection |
| DRILL-001 | Hard | 120 min | Full incident response simulation |
| DRILL-002 | Expert | 180 min | APT simulation with persistence |

### Running a CTF Exercise

```bash
# Start CTF-001
!battleground exercise CTF-001

# Check your progress
!battleground progress CTF-001

# Submit a flag
!battleground flag CTF-001 FLAG{captured_rbac_token}

# End exercise
!battleground end CTF-001
```

---

## 🧬 Antibody Department

The self-healing daemon that monitors, detects, and responds to threats automatically.

### Capabilities

- **Threat Detection**: Falco, OPA, custom alert rules
- **Classification**: Categorize threats by type and severity
- **Auto-Response**: Kill, quarantine, blacklist, alert
- **Immune Memory**: Learn patterns for future detection
- **Audit Trail**: Cryptographic logging of all actions

### Threat Categories

| Category | Severity | Auto-Response |
|----------|----------|---------------|
| Privilege Escalation | CRITICAL | Kill + Alert |
| Crypto Miner | HIGH | Quarantine |
| Reverse Shell | CRITICAL | Kill + Blacklist |
| RBAC Bypass | HIGH | Quarantine + Alert |
| NetworkPolicy Violation | MEDIUM | Log + Alert |
| Suspicious Binary Exec | MEDIUM | Alert |
| Supply Chain Attack | CRITICAL | Kill + Blacklist + Alert |

---

## 📊 Metrics & Monitoring

### Prometheus Metrics

```yaml
# Red Team metrics
redteam_attacks_launched_total{type="rbac"}
redteam_attacks_successful_total{type="rbac"}
redteam_cleanup_operations_total

# Blue Team metrics  
blueteam_threats_detected_total{category="privilege_escalation"}
blueteam_threats_quarantined_total
blueteam_compliance_score_percent

# Battleground metrics
battleground_ctf_exercises_completed_total
battleground_mean_detection_time_seconds
battleground_mean_response_time_seconds
```

### Grafana Dashboards

1. **Battleground Overview**: Both clusters at a glance
2. **Red Team Attack Dashboard**: Attack success rates
3. **Blue Team Defense Dashboard**: Detection metrics
4. **CTF Scoreboard**: Live exercise tracking

---

## 🔐 Security Considerations

### Isolation

- Clusters are network-isolated by default
- Cross-cluster communication via secure channels only
- Attack workloads run in isolated namespaces

### Cleanup

```bash
# Always cleanup after exercises
!redteam cleanup
!battleground reset

# Verify cleanup
kubectl get pods --all-namespaces | grep -E "(attack|malware|escalation)"
```

### Audit

All actions are logged to:
- CloudWatch Logs
- Loki (centralized logging)
- Antibody audit trail (cryptographically signed)

---

## 📚 Related Documentation

- [RED_TEAM_PLAYBOOK.md](playbooks/RED_TEAM_PLAYBOOK.md) — Attack scenarios
- [BLUE_TEAM_DEFENSE.md](playbooks/BLUE_TEAM_DEFENSE.md) — Defense architecture
- [Antibody Daemon](antibody-department/antibody_daemon.py) — Self-healing code

---

## 🏛️ Part of Strategickhaos Sovereignty Architecture

| IDEA | Status | Type |
|------|--------|------|
| IDEA_001 | `board_approved_conditional` | Contextual Memory |
| IDEA_026 | `prototype_ready` | Code-to-Diagram |
| IDEA_100 | `prototype_ready` | CPA Sentinel |
| **IDEA_101** | `prototype_ready` | Red/Blue Battleground ✨ |

---

*Strategickhaos DAO LLC — Sovereign Cyber Operations*
