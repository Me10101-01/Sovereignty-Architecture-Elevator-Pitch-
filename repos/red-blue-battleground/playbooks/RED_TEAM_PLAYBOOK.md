# 🟥 Red Team Playbook

## IDEA_101 — Attack Scenarios for Kubernetes Battleground

This playbook contains 70+ attack scenarios for testing defensive capabilities in the Red/Blue Kubernetes Battleground.

---

## 📋 Table of Contents

1. [RBAC & Authentication Attacks](#rbac--authentication-attacks)
2. [Container Escape Techniques](#container-escape-techniques)
3. [Privilege Escalation](#privilege-escalation)
4. [Network Attacks](#network-attacks)
5. [Supply Chain Attacks](#supply-chain-attacks)
6. [Persistence Techniques](#persistence-techniques)
7. [Evasion Techniques](#evasion-techniques)
8. [Credential Access](#credential-access)
9. [Lateral Movement](#lateral-movement)
10. [Impact Scenarios](#impact-scenarios)

---

## 🔐 RBAC & Authentication Attacks

### ATK-001: ServiceAccount Token Theft
**Difficulty**: Easy | **TTD Target**: 30s

```yaml
# Description: Steal service account tokens from mounted volumes
# Detection: Falco rule - K8s ServiceAccount token access
# MITRE: T1528 - Steal Application Access Token

# Attack Steps:
# 1. Deploy pod with default SA
# 2. Read token from /var/run/secrets/kubernetes.io/serviceaccount/token
# 3. Use token to query API server
```

**Commands**:
```bash
# Deploy attacker pod
kubectl apply -f synthetic-workloads/rbac-escalation-test.yaml

# Inside pod, steal token
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
curl -H "Authorization: Bearer $TOKEN" https://kubernetes.default.svc/api/v1/namespaces
```

---

### ATK-002: Anonymous Authentication Abuse
**Difficulty**: Easy | **TTD Target**: 15s

```yaml
# Description: Check for anonymous authentication enabled
# Detection: API audit logs, OPA policy
# MITRE: T1078.004 - Valid Accounts: Cloud Accounts
```

**Commands**:
```bash
# Check if anonymous auth is enabled
curl -k https://<api-server>:6443/api/v1/namespaces --insecure
```

---

### ATK-003: Cluster Admin Role Binding
**Difficulty**: Medium | **TTD Target**: 5s

```yaml
# Description: Create cluster-admin binding to gain full access
# Detection: OPA policy, audit logs
# MITRE: T1098 - Account Manipulation
```

---

### ATK-004: Impersonation Attack
**Difficulty**: Medium | **TTD Target**: 10s

```yaml
# Description: Impersonate privileged users/groups
# Detection: API audit logs, Falco
# MITRE: T1134.001 - Token Impersonation/Theft
```

**Commands**:
```bash
kubectl --as=system:admin get secrets -A
kubectl --as-group=system:masters get pods -A
```

---

### ATK-005: Certificate Signing Request Abuse
**Difficulty**: Hard | **TTD Target**: 60s

```yaml
# Description: Create CSR to generate valid client certs
# Detection: CSR admission review, audit logs
# MITRE: T1552.004 - Private Keys
```

---

### ATK-006: OIDC Token Manipulation
**Difficulty**: Hard | **TTD Target**: 45s

```yaml
# Description: Forge or replay OIDC tokens
# Detection: Token validation failures
# MITRE: T1550.001 - Application Access Token
```

---

### ATK-007: Bootstrap Token Theft
**Difficulty**: Medium | **TTD Target**: 20s

```yaml
# Description: Steal bootstrap tokens for cluster-admin access
# Detection: Secret access audit, Falco
# MITRE: T1528 - Steal Application Access Token
```

---

## 🐋 Container Escape Techniques

### ATK-010: Privileged Container Escape
**Difficulty**: Medium | **TTD Target**: 15s

```yaml
# Description: Escape from privileged container to host
# Detection: PSA violation, Falco privileged container rule
# MITRE: T1611 - Escape to Host
```

**Attack Pod**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: privileged-escape
spec:
  containers:
  - name: attacker
    image: alpine
    securityContext:
      privileged: true
    command: ["nsenter", "--target", "1", "--mount", "--uts", "--ipc", "--net", "--pid", "--", "bash"]
```

---

### ATK-011: HostPID Namespace Escape
**Difficulty**: Medium | **TTD Target**: 20s

```yaml
# Description: Access host processes via hostPID
# Detection: PSA, Falco
# MITRE: T1611 - Escape to Host
```

---

### ATK-012: HostNetwork Abuse
**Difficulty**: Easy | **TTD Target**: 10s

```yaml
# Description: Access host network stack
# Detection: PSA, NetworkPolicy bypass detection
# MITRE: T1611 - Escape to Host
```

---

### ATK-013: HostPath Volume Mount
**Difficulty**: Easy | **TTD Target**: 5s

```yaml
# Description: Mount sensitive host paths
# Detection: PSA, OPA, Falco
# MITRE: T1611 - Escape to Host
```

**Attack Pod**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hostpath-attack
spec:
  containers:
  - name: attacker
    image: alpine
    volumeMounts:
    - name: host-root
      mountPath: /host
  volumes:
  - name: host-root
    hostPath:
      path: /
```

---

### ATK-014: Docker Socket Mount
**Difficulty**: Medium | **TTD Target**: 5s

```yaml
# Description: Mount docker socket for container control
# Detection: OPA, Falco
# MITRE: T1611 - Escape to Host
```

---

### ATK-015: CGroup Escape (CVE-2022-0492)
**Difficulty**: Hard | **TTD Target**: 30s

```yaml
# Description: Exploit cgroup release_agent
# Detection: Falco, kernel audit
# MITRE: T1611 - Escape to Host
```

---

### ATK-016: Kernel Exploit (Dirty Pipe)
**Difficulty**: Expert | **TTD Target**: 60s

```yaml
# Description: CVE-2022-0847 kernel exploit
# Detection: Falco, SECCOMP violations
# MITRE: T1068 - Exploitation for Privilege Escalation
```

---

## ⬆️ Privilege Escalation

### ATK-020: CAP_SYS_ADMIN Abuse
**Difficulty**: Medium | **TTD Target**: 15s

```yaml
# Description: Abuse SYS_ADMIN capability
# Detection: PSA, Falco capability check
# MITRE: T1548 - Abuse Elevation Control Mechanism
```

---

### ATK-021: CAP_NET_ADMIN Network Takeover
**Difficulty**: Medium | **TTD Target**: 20s

```yaml
# Description: Manipulate network with NET_ADMIN
# Detection: Falco, network monitoring
# MITRE: T1557 - Adversary-in-the-Middle
```

---

### ATK-022: AllowPrivilegeEscalation Abuse
**Difficulty**: Easy | **TTD Target**: 10s

```yaml
# Description: Setuid binary execution
# Detection: PSA, Falco
# MITRE: T1548.001 - Setuid and Setgid
```

---

### ATK-023: RunAsRoot Container
**Difficulty**: Easy | **TTD Target**: 5s

```yaml
# Description: Run container as UID 0
# Detection: PSA, OPA
# MITRE: T1548 - Abuse Elevation Control Mechanism
```

---

### ATK-024: Writable /proc/sys Mount
**Difficulty**: Hard | **TTD Target**: 30s

```yaml
# Description: Write to kernel parameters
# Detection: Falco, kernel audit
# MITRE: T1611 - Escape to Host
```

---

## 🌐 Network Attacks

### ATK-030: NetworkPolicy Bypass
**Difficulty**: Medium | **TTD Target**: 20s

```yaml
# Description: Find gaps in NetworkPolicy coverage
# Detection: CNI logging, Falco
# MITRE: T1562.001 - Impair Defenses
```

---

### ATK-031: DNS Exfiltration
**Difficulty**: Medium | **TTD Target**: 45s

```yaml
# Description: Exfiltrate data via DNS queries
# Detection: DNS query logging, anomaly detection
# MITRE: T1048.003 - Exfiltration Over Alternative Protocol
```

---

### ATK-032: Service Mesh Bypass
**Difficulty**: Hard | **TTD Target**: 60s

```yaml
# Description: Bypass Istio sidecar
# Detection: Istio access logs, missing mTLS
# MITRE: T1562.001 - Impair Defenses
```

---

### ATK-033: Pod-to-Pod Direct Access
**Difficulty**: Easy | **TTD Target**: 30s

```yaml
# Description: Direct pod IP communication bypassing services
# Detection: NetworkPolicy, Cilium
# MITRE: T1571 - Non-Standard Port
```

---

### ATK-034: Metadata Service Access
**Difficulty**: Easy | **TTD Target**: 15s

```yaml
# Description: Access cloud metadata service
# Detection: NetworkPolicy, Falco
# MITRE: T1552.005 - Cloud Instance Metadata API
```

**Commands**:
```bash
# GCP metadata
curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
```

---

### ATK-035: MITM via ARP Spoofing
**Difficulty**: Hard | **TTD Target**: 30s

```yaml
# Description: ARP spoofing within pod network
# Detection: ARP monitoring, Falco
# MITRE: T1557.002 - ARP Cache Poisoning
```

---

## 📦 Supply Chain Attacks

### ATK-040: Malicious Base Image
**Difficulty**: Medium | **TTD Target**: 5s (at admission)

```yaml
# Description: Deploy pod with untrusted base image
# Detection: OPA image policy, Trivy
# MITRE: T1195.002 - Compromise Software Supply Chain
```

---

### ATK-041: Image Tag Mutability Attack
**Difficulty**: Medium | **TTD Target**: N/A (preventive)

```yaml
# Description: Exploit mutable image tags
# Detection: OPA digest policy
# MITRE: T1195.002 - Compromise Software Supply Chain
```

---

### ATK-042: Typosquatting Registry
**Difficulty**: Easy | **TTD Target**: 5s

```yaml
# Description: Pull from typosquatted registry
# Detection: OPA registry allowlist
# MITRE: T1195.002 - Compromise Software Supply Chain
```

---

### ATK-043: Malicious Helm Chart
**Difficulty**: Medium | **TTD Target**: N/A (preventive)

```yaml
# Description: Deploy compromised Helm chart
# Detection: Chart signing verification
# MITRE: T1195.002 - Compromise Software Supply Chain
```

---

### ATK-044: Dependency Confusion
**Difficulty**: Hard | **TTD Target**: N/A (CI/CD)

```yaml
# Description: Internal package name collision
# Detection: SBOM analysis, package audit
# MITRE: T1195.001 - Compromise Software Dependencies
```

---

### ATK-045: Malicious Operator
**Difficulty**: Expert | **TTD Target**: 30s

```yaml
# Description: Deploy backdoored operator
# Detection: Operator allowlist, behavior analysis
# MITRE: T1195.002 - Compromise Software Supply Chain
```

---

## 🏠 Persistence Techniques

### ATK-050: Cronjob Backdoor
**Difficulty**: Medium | **TTD Target**: 60s

```yaml
# Description: Create malicious cronjob for persistence
# Detection: Falco, OPA cronjob policy
# MITRE: T1053.003 - Scheduled Task/Job
```

---

### ATK-051: DaemonSet Persistence
**Difficulty**: Medium | **TTD Target**: 30s

```yaml
# Description: Deploy DaemonSet for node-level access
# Detection: DaemonSet admission, Falco
# MITRE: T1053.007 - Container Orchestration Job
```

---

### ATK-052: Mutating Webhook Backdoor
**Difficulty**: Expert | **TTD Target**: 15s

```yaml
# Description: Install malicious mutating admission webhook
# Detection: Webhook audit, OPA
# MITRE: T1574 - Hijack Execution Flow
```

---

### ATK-053: Static Pod Injection
**Difficulty**: Hard | **TTD Target**: 30s (requires host access)

```yaml
# Description: Add static pod manifest to kubelet
# Detection: File integrity monitoring, Falco
# MITRE: T1053.007 - Container Orchestration Job
```

---

### ATK-054: Node Annotation Abuse
**Difficulty**: Medium | **TTD Target**: 60s

```yaml
# Description: Modify node annotations for privilege
# Detection: API audit, RBAC restrictions
# MITRE: T1098 - Account Manipulation
```

---

## 🥷 Evasion Techniques

### ATK-060: Pod Security Bypass
**Difficulty**: Medium | **TTD Target**: 5s

```yaml
# Description: Bypass PSA via namespace labels
# Detection: Label audit, OPA backup policies
# MITRE: T1562.001 - Impair Defenses
```

---

### ATK-061: OPA Policy Bypass
**Difficulty**: Hard | **TTD Target**: Variable

```yaml
# Description: Find gaps in OPA policies
# Detection: Policy coverage analysis
# MITRE: T1562.001 - Impair Defenses
```

---

### ATK-062: Log Evasion
**Difficulty**: Medium | **TTD Target**: N/A

```yaml
# Description: Disable or manipulate logging
# Detection: Log gap detection, Falco
# MITRE: T1562.002 - Disable Windows Event Logging
```

---

### ATK-063: Falco Rule Evasion
**Difficulty**: Hard | **TTD Target**: Variable

```yaml
# Description: Craft payloads to evade Falco rules
# Detection: Behavioral analysis, ML detection
# MITRE: T1562.001 - Impair Defenses
```

---

### ATK-064: Ephemeral Container Abuse
**Difficulty**: Medium | **TTD Target**: 20s

```yaml
# Description: Use debug containers for stealth
# Detection: Ephemeral container audit
# MITRE: T1610 - Deploy Container
```

---

## 🔑 Credential Access

### ATK-070: Secret Enumeration
**Difficulty**: Easy | **TTD Target**: 10s

```yaml
# Description: List and read Kubernetes secrets
# Detection: API audit, RBAC
# MITRE: T1552.007 - Container API
```

---

### ATK-071: ConfigMap Credential Theft
**Difficulty**: Easy | **TTD Target**: 15s

```yaml
# Description: Extract credentials from ConfigMaps
# Detection: ConfigMap access audit
# MITRE: T1552 - Unsecured Credentials
```

---

### ATK-072: Environment Variable Harvesting
**Difficulty**: Easy | **TTD Target**: 20s

```yaml
# Description: Read secrets from env vars
# Detection: Falco process monitoring
# MITRE: T1552 - Unsecured Credentials
```

---

### ATK-073: Cloud Provider Credential Theft
**Difficulty**: Medium | **TTD Target**: 15s

```yaml
# Description: Steal GCP/AWS credentials from metadata
# Detection: NetworkPolicy, Falco
# MITRE: T1552.005 - Cloud Instance Metadata API
```

---

### ATK-074: Vault Secret Extraction
**Difficulty**: Hard | **TTD Target**: 30s

```yaml
# Description: Access HashiCorp Vault secrets
# Detection: Vault audit logs
# MITRE: T1555 - Credentials from Password Stores
```

---

## ↔️ Lateral Movement

### ATK-080: Cross-Namespace Access
**Difficulty**: Medium | **TTD Target**: 30s

```yaml
# Description: Access resources in other namespaces
# Detection: RBAC audit, NetworkPolicy
# MITRE: T1570 - Lateral Tool Transfer
```

---

### ATK-081: Node Compromise via Kubelet
**Difficulty**: Hard | **TTD Target**: 45s

```yaml
# Description: Access kubelet API from pod
# Detection: NetworkPolicy, Falco
# MITRE: T1053.007 - Container Orchestration Job
```

---

### ATK-082: etcd Direct Access
**Difficulty**: Expert | **TTD Target**: 10s

```yaml
# Description: Direct etcd cluster access
# Detection: Network monitoring, mTLS enforcement
# MITRE: T1552.007 - Container API
```

---

### ATK-083: Service Account Pivot
**Difficulty**: Medium | **TTD Target**: 30s

```yaml
# Description: Pivot using stolen service account
# Detection: Token usage audit
# MITRE: T1550.001 - Application Access Token
```

---

## 💥 Impact Scenarios

### ATK-090: Resource Exhaustion (DoS)
**Difficulty**: Easy | **TTD Target**: 60s

```yaml
# Description: Consume cluster resources
# Detection: Resource quotas, monitoring
# MITRE: T1499.003 - Application Exhaustion Flood
```

---

### ATK-091: Crypto Mining Deployment
**Difficulty**: Easy | **TTD Target**: 60s

```yaml
# Description: Deploy cryptocurrency miner
# Detection: Falco, resource monitoring
# MITRE: T1496 - Resource Hijacking
```

---

### ATK-092: Data Destruction
**Difficulty**: Medium | **TTD Target**: 15s

```yaml
# Description: Delete PVCs and critical data
# Detection: Audit logs, RBAC
# MITRE: T1485 - Data Destruction
```

---

### ATK-093: Ransom Note Deployment
**Difficulty**: Easy | **TTD Target**: 30s

```yaml
# Description: Deploy ransom note ConfigMap
# Detection: ConfigMap creation audit
# MITRE: T1491 - Defacement
```

---

### ATK-094: Cluster State Corruption
**Difficulty**: Expert | **TTD Target**: Variable

```yaml
# Description: Corrupt critical cluster resources
# Detection: State drift detection, backup comparison
# MITRE: T1485 - Data Destruction
```

---

## 📊 Attack Success Metrics

| Category | Total Scenarios | Easy | Medium | Hard | Expert |
|----------|-----------------|------|--------|------|--------|
| RBAC | 7 | 2 | 3 | 2 | 0 |
| Container Escape | 7 | 2 | 3 | 1 | 1 |
| Privilege Escalation | 5 | 2 | 2 | 1 | 0 |
| Network | 6 | 2 | 2 | 2 | 0 |
| Supply Chain | 6 | 1 | 3 | 1 | 1 |
| Persistence | 5 | 0 | 3 | 1 | 1 |
| Evasion | 5 | 0 | 3 | 2 | 0 |
| Credential Access | 5 | 3 | 1 | 1 | 0 |
| Lateral Movement | 4 | 0 | 2 | 1 | 1 |
| Impact | 5 | 2 | 1 | 0 | 2 |
| **TOTAL** | **55** | **14** | **23** | **12** | **6** |

---

## 🎯 Recommended Exercise Order

1. **Week 1**: RBAC & Authentication (ATK-001 to ATK-007)
2. **Week 2**: Container Escape (ATK-010 to ATK-016)
3. **Week 3**: Network Attacks (ATK-030 to ATK-035)
4. **Week 4**: Supply Chain (ATK-040 to ATK-045)
5. **Week 5**: Combined Scenarios (CTF Exercises)
6. **Week 6**: Full Incident Response (DRILL-001)

---

*Red Team Playbook — Strategickhaos IDEA_101*
