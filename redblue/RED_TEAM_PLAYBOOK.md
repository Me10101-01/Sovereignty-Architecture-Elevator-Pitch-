# 🟥 Red Team Cluster Playbook

**Cluster:** `autopilot-cluster-1`  
**Purpose:** Offensive Security Testing Sandbox  
**Classification:** INTERNAL USE ONLY  
**Version:** 1.0.0

---

## 📋 Overview

The Red Team Cluster is a dedicated sandbox environment for security testing, attack simulations, and vulnerability research. This cluster is **completely isolated** from production workloads and uses only **synthetic data and test scenarios**.

```
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

---

## ✅ Allowed Activities

### 1. RBAC Misconfiguration Scanning
Test for overly permissive RBAC configurations that could lead to privilege escalation.

```bash
# Deploy RBAC scanner
kubectl apply -f redblue/workloads/rbac-scanner.yaml -n attack-simulation

# Run RBAC audit
kubectl exec -it rbac-scanner -n attack-simulation -- /bin/sh -c "rbac-audit scan"
```

### 2. Pod-to-Pod Traffic Analysis
Test network segmentation and pod communication paths.

```bash
# Deploy traffic analyzer
kubectl apply -f redblue/workloads/traffic-analyzer.yaml -n attack-simulation

# Monitor pod traffic
kubectl exec -it traffic-analyzer -n attack-simulation -- /bin/sh -c "tcpdump -i eth0 -n"
```

### 3. Fake Malicious Container Images
Use synthetic "malicious" container images for detection testing.

```bash
# Deploy synthetic malware container (SAFE - for testing only)
kubectl apply -f redblue/workloads/synthetic-malware.yaml -n synthetic-malware

# Verify Falco detection
kubectl logs -f falco -n kube-system | grep "synthetic-malware"
```

### 4. K8s Audit Log Analysis
Test audit logging configurations and event detection.

```bash
# Enable enhanced audit logging
kubectl apply -f redblue/audit/enhanced-audit-policy.yaml

# Stream audit logs
kubectl logs -f kube-apiserver -n kube-system | grep "audit"
```

### 5. Privilege Escalation Prevention Testing
Test for common privilege escalation vectors.

```bash
# Deploy privilege escalation test pod
kubectl apply -f redblue/workloads/privesc-test.yaml -n attack-simulation

# Test for common escalation paths
kubectl exec -it privesc-test -n attack-simulation -- /bin/sh -c "id && whoami && cat /proc/1/status"
```

### 6. NetworkPolicy Lockdown Tests
Test network policy effectiveness and bypass techniques.

```bash
# Deploy network policy test suite
kubectl apply -f redblue/workloads/netpol-test.yaml -n attack-simulation

# Test egress restrictions
kubectl exec -it netpol-test -n attack-simulation -- /bin/sh -c "curl -v http://external-service.example.com"
```

### 7. Container Breakout Detection (Falco)
Test container runtime security detection.

```bash
# Deploy breakout simulation pod
kubectl apply -f redblue/workloads/breakout-sim.yaml -n breakout-lab

# Simulate container escape attempt (SAFE - synthetic)
kubectl exec -it breakout-sim -n breakout-lab -- /bin/sh -c "cat /etc/shadow"
```

### 8. Secret Leak Drills (Synthetic)
Test secret exposure detection with fake secrets.

```bash
# Create synthetic test secret
kubectl create secret generic test-secret \
  --from-literal=api-key='SYNTHETIC-TEST-KEY-12345' \
  -n attack-simulation

# Deploy secret leaker simulation
kubectl apply -f redblue/workloads/secret-leak-sim.yaml -n attack-simulation
```

### 9. Supply Chain Attack Simulation
Test for vulnerable dependencies and images.

```bash
# Deploy supply chain test
kubectl apply -f redblue/workloads/supply-chain-test.yaml -n supply-chain-lab

# Scan for vulnerable images
kubectl exec -it supply-chain-test -n supply-chain-lab -- /bin/sh -c "trivy image --severity HIGH,CRITICAL test-image:latest"
```

---

## 🚫 Prohibited Activities

| Activity | Reason | Enforcement |
|----------|--------|-------------|
| Attack external networks | Legal/ethical violation | NetworkPolicy |
| Probe systems you don't own | Unauthorized access | NetworkPolicy |
| Deploy real malware | Safety hazard | AdmissionController |
| Test exploits outside GCP/local | Scope violation | NetworkPolicy |
| Access production data | Data protection | RBAC |

---

## 📊 Namespaces

| Namespace | Purpose | Security Level |
|-----------|---------|----------------|
| `attack-simulation` | Active attack testing | Experimental |
| `misconfig-lab` | Misconfiguration testing | Experimental |
| `supply-chain-lab` | Supply chain security testing | Experimental |
| `breakout-lab` | Container breakout testing | Experimental |
| `synthetic-malware` | Safe synthetic malware testing | Experimental |

---

## 🔧 Setup Commands

### Initialize Red Team Cluster

```bash
# Switch to red team cluster context
kubectl config use-context gke_strategickhaos-sovereign_us-central1_autopilot-cluster-1

# Create namespaces
kubectl create namespace attack-simulation
kubectl create namespace misconfig-lab
kubectl create namespace supply-chain-lab
kubectl create namespace breakout-lab
kubectl create namespace synthetic-malware

# Apply base security policies
kubectl apply -f redblue/k8s/red-team/

# Deploy Falco for detection testing
kubectl apply -f redblue/k8s/red-team/falco-daemonset.yaml
```

### Deploy Test Workloads

```bash
# Deploy all test workloads
kubectl apply -f redblue/workloads/ -R

# Verify deployments
kubectl get pods --all-namespaces | grep -E "(attack|misconfig|supply|breakout|synthetic)"
```

---

## 📈 Metrics & Reporting

### Key Metrics

- `attacks_simulated`: Total attack simulations run
- `vulnerabilities_found`: Vulnerabilities discovered
- `misconfigurations_detected`: Misconfigs identified
- `escalation_attempts`: Privilege escalation tests
- `breakout_attempts`: Container escape tests

### Generate Report

```bash
# Generate red team activity report
kubectl exec -it redteam-reporter -n attack-simulation -- /bin/sh -c "generate-report --format=json"
```

---

## 🔄 Integration with Blue Team

The Red Team cluster sends telemetry to the Blue Team cluster for:

1. **Detection validation**: Verify Blue Team alerts trigger correctly
2. **Response testing**: Test incident response procedures
3. **Policy tuning**: Refine security policies based on findings

```yaml
# Telemetry sync configuration
sync:
  destination: "telemetry.blue-team.internal:9090"
  events:
    - attack_started
    - vulnerability_found
    - detection_triggered
    - test_completed
```

---

## 📚 ReflexShell Commands

```bash
# Attack commands (Red Team operations)
!redteam attack --type=rbac-scan
!redteam attack --type=netpol-bypass
!redteam attack --type=privesc
!redteam attack --type=container-breakout
!redteam attack --type=supply-chain

# Audit commands
!audit cluster --target=red-team
!audit rbac --namespace=attack-simulation
!audit network --check=isolation
```

---

## ⚠️ Safety Guidelines

1. **Always** use synthetic data and test credentials
2. **Never** connect to external systems or services
3. **Always** log all activities for audit purposes
4. **Never** store real secrets in the red team cluster
5. **Always** coordinate with Blue Team for scheduled tests
6. **Never** attempt to access the Blue Team cluster directly

---

## 📝 Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-01 | Initial playbook release |

---

*Built with 🔥 by Strategickhaos Swarm Intelligence*
