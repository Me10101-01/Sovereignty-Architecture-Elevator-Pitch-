# GKE Cluster Management Runbook

> **Project**: `jarvis-swarm-personal`  
> **Region**: `us-central1`  
> **Architecture**: Red Team / Blue Team Battleground

---

## 🏗️ Cluster Architecture

| Cluster Name | Role | Purpose | Status |
|--------------|------|---------|--------|
| `jarvis` | Blue Team / Defense | Core infrastructure, defensive operations | Primary |
| `red-team` | Red Team / Offense | Attack simulations, chaos engineering | Secondary |

---

## 📋 Prerequisites

```bash
# Authenticate with GCP
gcloud auth login

# Set project
gcloud config set project jarvis-swarm-personal

# Verify access
gcloud container clusters list --project=jarvis-swarm-personal
```

---

## Block 1: Rename Main Cluster to `jarvis`

> **Note**: GKE does not support direct cluster renaming. The `--name` flag in `gcloud container clusters update` is not valid for renaming. To "rename" a cluster, you must create a new cluster with the desired name and migrate workloads.

### Option A: Update Cluster Configuration (if cluster exists)

```bash
# Update cluster settings (not renaming - update labels/config)
gcloud container clusters update jarvis-swarm-personal-001 \
  --region=us-central1 \
  --project=jarvis-swarm-personal \
  --update-labels=role=blue-team,name=jarvis
```

### Option B: Create New Cluster with Desired Name (Recommended)

```bash
# Create new autopilot cluster named 'jarvis'
gcloud container clusters create-auto jarvis \
  --region=us-central1 \
  --project=jarvis-swarm-personal \
  --release-channel=regular \
  --quiet

# Register cluster with fleet (after creation)
gcloud container fleet memberships register jarvis \
  --gke-cluster=us-central1/jarvis \
  --project=jarvis-swarm-personal
```

### Configure kubectl Context

```bash
# Get credentials for the cluster
gcloud container clusters get-credentials jarvis \
  --region=us-central1 \
  --project=jarvis-swarm-personal

# Verify nodes are ready
kubectl get nodes

# Verify cluster context
kubectl config current-context
```

**Expected Output**: Cluster `jarvis` is now your blue-team fortress with Ready nodes.

---

## Block 2: Create Red-Team Cluster (Autopilot)

> **Important**: Autopilot clusters automatically handle node management, auto-repair, and auto-upgrade. The `--enable-autorepair` flag is not needed.

```bash
# Create red-team autopilot cluster
gcloud container clusters create-auto red-team \
  --region=us-central1 \
  --project=jarvis-swarm-personal \
  --release-channel=regular \
  --quiet

# Register cluster with fleet (after creation)
gcloud container fleet memberships register red-team \
  --gke-cluster=us-central1/red-team \
  --project=jarvis-swarm-personal
```

**Duration**: 4-6 minutes for cluster creation.

### Configure kubectl for Red-Team

```bash
# Get credentials for red-team cluster
gcloud container clusters get-credentials red-team \
  --region=us-central1 \
  --project=jarvis-swarm-personal

# Verify nodes (may show 0 initially - Autopilot scales on demand)
kubectl get nodes

# Check cluster context name
kubectl config get-contexts
```

**Note**: Autopilot clusters idle down to save costs. Nodes will scale up when you deploy workloads.

---

## Block 3: Enable Fleet Service Mesh

> **Important**: The `--no-async` flag is not required. The command runs asynchronously by default.

```bash
# Enable fleet service mesh for cross-cluster communication
gcloud container fleet mesh enable \
  --project=jarvis-swarm-personal
```

**Duration**: 1-2 minutes for mesh initialization.

### Verify Fleet Mesh Status

```bash
# Describe mesh configuration
gcloud container fleet mesh describe \
  --project=jarvis-swarm-personal

# List fleet memberships
gcloud container fleet memberships list \
  --project=jarvis-swarm-personal
```

**Purpose**: Fleet mesh enables cross-cluster communication for red/blue team exercises. Pods in `red-team` can "attack" services in `jarvis` via Istio/Linkerd service mesh.

---

## 🔍 Cluster Status Commands

### List All Clusters

```bash
gcloud container clusters list \
  --project=jarvis-swarm-personal
```

### Describe Specific Cluster

```bash
# Blue team cluster
gcloud container clusters describe jarvis \
  --region=us-central1 \
  --project=jarvis-swarm-personal

# Red team cluster
gcloud container clusters describe red-team \
  --region=us-central1 \
  --project=jarvis-swarm-personal
```

### Switch kubectl Context

```bash
# Switch to jarvis (blue team)
kubectl config use-context gke_jarvis-swarm-personal_us-central1_jarvis

# Switch to red-team
kubectl config use-context gke_jarvis-swarm-personal_us-central1_red-team
```

---

## 💰 Cost Estimation

| Cluster | Role | Estimated Cost/Month |
|---------|------|---------------------|
| `jarvis` | Blue Team / Defense | ~$45-65 |
| `red-team` | Red Team / Offense | ~$45-65 |
| **Total** | | **~$90-130** |

> **Note**: Autopilot clusters scale down when idle, optimizing costs automatically.

---

## 🛡️ Red/Blue Team Payloads

### Red Team Attack Scenarios

Deploy from `red-team` cluster context:

```bash
# Switch to red-team context
kubectl config use-context gke_jarvis-swarm-personal_us-central1_red-team

# Deploy attack workloads
kubectl apply -f synthetic-workloads/fake-malware-pod.yaml
kubectl apply -f synthetic-workloads/rbac-escalation-test.yaml
```

### Blue Team Defense

Switch to `jarvis` cluster and monitor:

```bash
# Switch to blue-team context
kubectl config use-context gke_jarvis-swarm-personal_us-central1_jarvis

# Monitor for suspicious activity
kubectl get pods --all-namespaces -w
kubectl get events --all-namespaces
```

---

## 🔧 Troubleshooting

### Cluster Not Found (404 Error)

If you receive a 404 error for a cluster like `autopilot-cluster-1`:

```bash
# List all clusters to verify names
gcloud container clusters list --project=jarvis-swarm-personal

# The cluster may not exist or was never created
# Check if it's a naming mismatch from earlier operations
```

### Fleet Mesh Enable Fails

```bash
# Check if Fleet API is enabled
gcloud services enable container.googleapis.com --project=jarvis-swarm-personal
gcloud services enable gkehub.googleapis.com --project=jarvis-swarm-personal
gcloud services enable mesh.googleapis.com --project=jarvis-swarm-personal

# Retry mesh enable
gcloud container fleet mesh enable --project=jarvis-swarm-personal
```

### kubectl Connection Issues

```bash
# Re-authenticate
gcloud auth login

# Refresh cluster credentials
gcloud container clusters get-credentials jarvis \
  --region=us-central1 \
  --project=jarvis-swarm-personal
```

---

## 📚 References

- [GKE Autopilot Documentation](https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview)
- [Fleet Management](https://cloud.google.com/anthos/fleet-management/docs)
- [Service Mesh](https://cloud.google.com/service-mesh/docs)

---

> **Last Updated**: 2025-12-01  
> **Maintainer**: Strategickhaos Swarm Intelligence
