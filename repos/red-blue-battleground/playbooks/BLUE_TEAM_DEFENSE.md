# 🟦 Blue Team Defense Playbook

## IDEA_101 — Defense Architecture for Kubernetes Battleground

This playbook defines the defense-in-depth architecture for the Blue Team cluster in the Red/Blue Kubernetes Battleground.

---

## 📋 Table of Contents

1. [Defense Stack Overview](#defense-stack-overview)
2. [Falco Runtime Security](#falco-runtime-security)
3. [OPA Gatekeeper Policies](#opa-gatekeeper-policies)
4. [Pod Security Admission](#pod-security-admission)
5. [Network Policies](#network-policies)
6. [Service Mesh Security (Istio)](#service-mesh-security-istio)
7. [Antibody Department](#antibody-department)
8. [Incident Response Procedures](#incident-response-procedures)
9. [Compliance & Audit](#compliance--audit)

---

## 🏰 Defense Stack Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    BLUE TEAM DEFENSE LAYERS                  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Layer 7: Application Security                        │   │
│  │ • WAF rules          • Input validation              │   │
│  │ • API rate limiting  • JWT validation                │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Layer 6: Service Mesh (Istio)                        │   │
│  │ • mTLS everywhere    • Authorization policies         │   │
│  │ • Traffic encryption • Service-to-service auth       │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Layer 5: Network Policies                            │   │
│  │ • Default deny       • Explicit allow rules          │   │
│  │ • Egress control     • Namespace isolation           │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Layer 4: Admission Control                           │   │
│  │ • OPA Gatekeeper     • Image policy                  │   │
│  │ • Pod Security Admission • Resource quotas           │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Layer 3: Runtime Security (Falco)                    │   │
│  │ • Syscall monitoring • Behavioral detection          │   │
│  │ • File integrity     • Process tracking              │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Layer 2: Container Security                          │   │
│  │ • Image scanning     • Seccomp profiles              │   │
│  │ • AppArmor           • Capabilities dropping         │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Layer 1: Infrastructure Security                     │   │
│  │ • Node hardening     • Encryption at rest            │   │
│  │ • RBAC               • Audit logging                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🧬 ANTIBODY DEPARTMENT (Cross-Layer)                 │   │
│  │ • Threat detection   • Auto-response                 │   │
│  │ • Immune memory      • Self-healing                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🦅 Falco Runtime Security

Falco provides runtime threat detection at the kernel level.

### Deployment

```bash
# Install Falco using Helm
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm install falco falcosecurity/falco \
  --namespace falco-system \
  --create-namespace \
  --set tty=true \
  --set falcosidekick.enabled=true \
  --set falcosidekick.config.discord.webhookurl="${DISCORD_WEBHOOK}"
```

### Critical Rules

#### DEF-001: Privilege Escalation Detection

```yaml
- rule: Detect Privilege Escalation
  desc: Detect privilege escalation attempts
  condition: >
    spawned_process and
    proc.name in (sudo, su, doas) and
    container and
    not proc.pname in (cron, crond)
  output: >
    Privilege escalation detected
    (user=%user.name command=%proc.cmdline container=%container.id
     image=%container.image.repository)
  priority: CRITICAL
  tags: [privilege_escalation, mitre_T1548]
```

#### DEF-002: Container Escape Detection

```yaml
- rule: Container Escape Attempt
  desc: Detect container escape via nsenter or chroot
  condition: >
    spawned_process and
    proc.name in (nsenter, chroot) and
    container
  output: >
    Container escape attempt
    (user=%user.name command=%proc.cmdline container=%container.id)
  priority: CRITICAL
  tags: [container_escape, mitre_T1611]
```

#### DEF-003: Crypto Miner Detection

```yaml
- rule: Crypto Miner Process
  desc: Detect cryptocurrency mining processes
  condition: >
    spawned_process and
    (
      proc.name in (xmrig, minerd, cpuminer, cgminer, bfgminer) or
      proc.cmdline contains "stratum+tcp" or
      proc.cmdline contains "stratum+ssl" or
      proc.cmdline contains "pool.minergate"
    )
  output: >
    Crypto miner detected
    (process=%proc.name command=%proc.cmdline container=%container.id)
  priority: HIGH
  tags: [crypto_mining, mitre_T1496]
```

#### DEF-004: Reverse Shell Detection

```yaml
- rule: Reverse Shell
  desc: Detect reverse shell connections
  condition: >
    spawned_process and
    ((proc.name = bash and proc.args contains "-i") or
     (proc.name = nc and (proc.args contains "-e" or proc.args contains "-c")) or
     (proc.name = python and proc.cmdline contains "socket") or
     (proc.name = perl and proc.cmdline contains "socket"))
  output: >
    Reverse shell detected
    (process=%proc.name command=%proc.cmdline connection=%fd.name)
  priority: CRITICAL
  tags: [reverse_shell, mitre_T1059]
```

#### DEF-005: ServiceAccount Token Access

```yaml
- rule: K8s ServiceAccount Token Access
  desc: Detect access to ServiceAccount tokens
  condition: >
    open_read and
    fd.name startswith /var/run/secrets/kubernetes.io and
    not proc.name in (kubelet, containerd)
  output: >
    ServiceAccount token accessed
    (file=%fd.name process=%proc.name container=%container.id)
  priority: HIGH
  tags: [credential_access, mitre_T1528]
```

### All Falco Rules

| Rule ID | Name | Priority | MITRE ATT&CK |
|---------|------|----------|--------------|
| DEF-001 | Privilege Escalation | CRITICAL | T1548 |
| DEF-002 | Container Escape | CRITICAL | T1611 |
| DEF-003 | Crypto Miner | HIGH | T1496 |
| DEF-004 | Reverse Shell | CRITICAL | T1059 |
| DEF-005 | SA Token Access | HIGH | T1528 |
| DEF-006 | HostPath Mount | HIGH | T1611 |
| DEF-007 | Docker Socket | CRITICAL | T1611 |
| DEF-008 | Suspicious Binary | MEDIUM | T1036 |
| DEF-009 | Network Anomaly | MEDIUM | T1071 |
| DEF-010 | File Integrity | HIGH | T1565 |

---

## 🚧 OPA Gatekeeper Policies

Open Policy Agent provides admission control at the API server level.

### Deployment

```bash
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.14/deploy/gatekeeper.yaml
```

### Critical Policies

#### POL-001: Block Privileged Containers

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sPSPPrivilegedContainer
metadata:
  name: psp-privileged-container
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    excludedNamespaces:
      - kube-system
      - gatekeeper-system
  parameters:
    exemptImages:
      - "gcr.io/google-containers/*"
```

#### POL-002: Require Image Digest

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sImageDigests
metadata:
  name: container-image-must-have-digest
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    namespaces:
      - production
      - staging
```

#### POL-003: Allowed Registries Only

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sAllowedRepos
metadata:
  name: repo-is-gcr
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
  parameters:
    repos:
      - "gcr.io/strategickhaos/"
      - "us-docker.pkg.dev/strategickhaos/"
      - "registry.k8s.io/"
```

#### POL-004: Block HostNetwork

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sPSPHostNetworkingPorts
metadata:
  name: psp-host-network
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    excludedNamespaces:
      - kube-system
      - istio-system
  parameters:
    hostNetwork: false
```

#### POL-005: Require Resource Limits

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sContainerLimits
metadata:
  name: container-must-have-limits
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
  parameters:
    cpu: "2"
    memory: "2Gi"
```

### All OPA Policies

| Policy ID | Name | Enforcement | Scope |
|-----------|------|-------------|-------|
| POL-001 | No Privileged | deny | all except kube-system |
| POL-002 | Image Digest | deny | prod/staging |
| POL-003 | Allowed Registries | deny | all |
| POL-004 | No HostNetwork | deny | all except kube-system |
| POL-005 | Resource Limits | deny | all |
| POL-006 | No HostPID | deny | all |
| POL-007 | No HostPath | deny | all |
| POL-008 | Read-Only Root | warn | all |
| POL-009 | Drop Capabilities | deny | all |
| POL-010 | Non-Root User | deny | prod |

---

## 🛡️ Pod Security Admission

Pod Security Admission (PSA) enforces security standards at the namespace level.

### Configuration

```yaml
# Namespace labels for PSA enforcement
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: v1.28
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### Security Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| **privileged** | No restrictions | kube-system only |
| **baseline** | Minimal restrictions | Development |
| **restricted** | Strict security | Production |

### Enforcement Matrix

| Namespace | Enforce | Audit | Warn |
|-----------|---------|-------|------|
| kube-system | privileged | - | - |
| production | restricted | restricted | restricted |
| staging | baseline | restricted | restricted |
| development | baseline | baseline | restricted |
| attack-sandbox | privileged | - | - |

---

## 🔒 Network Policies

Default-deny with explicit allow rules.

### DEF-NET-001: Default Deny All

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

### DEF-NET-002: Allow DNS

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
```

### DEF-NET-003: Block Metadata Service

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-metadata
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
            except:
              - 169.254.169.254/32  # Block GCP/AWS metadata
              - 100.100.100.200/32  # Block Azure IMDS
```

---

## 🕸️ Service Mesh Security (Istio)

Istio provides mTLS, authorization policies, and traffic encryption.

### mTLS Enforcement

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
```

### Authorization Policy

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: deny-all
  namespace: production
spec:
  {}  # Deny all by default
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  selector:
    matchLabels:
      app: backend
  action: ALLOW
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/production/sa/frontend"]
      to:
        - operation:
            methods: ["GET", "POST"]
            paths: ["/api/*"]
```

---

## 🧬 Antibody Department

Self-healing system that monitors, detects, and responds to threats.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ANTIBODY DEPARTMENT                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌───────────────┐     ┌───────────────┐     ┌──────────────┐ │
│   │   Detectors   │────▶│   Classifier  │────▶│  Responders  │ │
│   └───────────────┘     └───────────────┘     └──────────────┘ │
│          │                     │                     │         │
│          │                     │                     │         │
│          ▼                     ▼                     ▼         │
│   ┌───────────────────────────────────────────────────────────┐│
│   │                     IMMUNE MEMORY                         ││
│   │  • Threat patterns    • Response history                  ││
│   │  • Attack signatures  • Recovery procedures               ││
│   └───────────────────────────────────────────────────────────┘│
│          │                                                      │
│          ▼                                                      │
│   ┌───────────────────────────────────────────────────────────┐│
│   │                    AUDIT TRAIL                            ││
│   │  • Cryptographic signing  • Immutable log                 ││
│   └───────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Threat Response Matrix

| Threat Type | Severity | Auto-Response | Manual Required |
|-------------|----------|---------------|-----------------|
| Privilege Escalation | CRITICAL | Kill pod, Alert | Review RBAC |
| Crypto Miner | HIGH | Quarantine | Image analysis |
| Reverse Shell | CRITICAL | Kill, Blacklist | Incident report |
| RBAC Bypass | HIGH | Quarantine | RBAC audit |
| Supply Chain | CRITICAL | Block, Alert | Pipeline review |
| Network Violation | MEDIUM | Log, Alert | Policy review |

### Response Actions

1. **Kill**: Immediately terminate the pod
2. **Quarantine**: Move to isolated namespace, block network
3. **Blacklist**: Add image hash to deny list
4. **Alert**: Send notification to security team
5. **Audit**: Log detailed forensic information
6. **Isolate Node**: Cordon and drain affected node

---

## 🚨 Incident Response Procedures

### IR-001: Detection

```bash
# Check Falco alerts
kubectl logs -n falco-system -l app=falco --tail=100

# Check OPA violations
kubectl get constrainttemplatepodstatuses.status.gatekeeper.sh -A

# Check Antibody alerts
!blueteam threats
```

### IR-002: Containment

```bash
# Quarantine suspicious pod
!blueteam quarantine <namespace>/<pod-name>

# Cordon affected node
kubectl cordon <node-name>

# Block network access
kubectl apply -f emergency-network-deny.yaml
```

### IR-003: Eradication

```bash
# Kill malicious pods
kubectl delete pod <pod-name> -n <namespace> --force

# Remove persistence mechanisms
kubectl delete cronjob,daemonset -l suspicious=true -A

# Blacklist malicious image
!antibody blacklist <image-hash>
```

### IR-004: Recovery

```bash
# Restore desired state
!heal state

# Uncordon nodes
kubectl uncordon <node-name>

# Verify security posture
!blueteam compliance
```

### IR-005: Post-Incident

```bash
# Generate incident report
!battleground incident-report

# Update immune memory
!sync rules

# Review and update policies
!blueteam policy-review
```

---

## 📋 Compliance & Audit

### Compliance Checks

```bash
# Run full compliance scan
!blueteam compliance

# Check specific standard
!blueteam compliance cis-benchmark
!blueteam compliance nsa-cisa
```

### Audit Trail

All security events are logged to:

1. **CloudWatch Logs** - AWS/GCP native logging
2. **Loki** - Centralized log aggregation
3. **Antibody Audit** - Cryptographically signed events

### Retention Policy

| Log Type | Retention | Storage |
|----------|-----------|---------|
| Security Events | 365 days | Cold storage |
| Audit Logs | 730 days | Cold storage |
| Incident Reports | Permanent | Encrypted archive |
| Compliance Scans | 90 days | Hot storage |

---

## 📊 Defense Metrics

### Key Performance Indicators

| Metric | Target | Description |
|--------|--------|-------------|
| MTTD | < 30s | Mean Time to Detect |
| MTTR | < 5m | Mean Time to Respond |
| Detection Rate | > 95% | Threats detected / Total threats |
| False Positive Rate | < 5% | False alerts / Total alerts |
| Compliance Score | > 90% | Passing checks / Total checks |

### Prometheus Metrics

```yaml
# Defense metrics
blueteam_threats_detected_total{category, severity}
blueteam_threats_responded_total{action}
blueteam_mttd_seconds{category}
blueteam_mttr_seconds{category}
blueteam_compliance_score_percent{standard}
blueteam_policy_violations_total{policy}
```

---

*Blue Team Defense Playbook — Strategickhaos IDEA_101*
