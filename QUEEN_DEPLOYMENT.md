# 👑 Queen Deployment Guide

**Deploy Queen to GKE in 60 Seconds**

Queen is the StrategicKhaos Swarm Intelligence Control Plane that connects:
- GitHub Apps & Webhooks
- Academic signals (via Zapier)
- OAuth authentication
- Health monitoring

## 📊 Architecture

```
queen.strategickhaos.ai
        │
        ▼ (DNS A record)
┌─────────────────────────────────────────┐
│  GKE: jarvis-swarm-personal-001         │
│  LoadBalancer IP: [ASSIGNED]            │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  queen-system namespace          │   │
│  │  ├── queen (2 replicas)          │   │
│  │  ├── /health                     │   │
│  │  ├── /signals/academic           │   │
│  │  ├── /webhooks/github            │   │
│  │  └── /oauth/callback             │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│  GitHub App (ID: 1884781)               │
│  Installation: 97868480                 │
│  Webhooks → queen.strategickhaos.ai     │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│  Zapier                                 │
│  POST → /signals/academic               │
└─────────────────────────────────────────┘
```

## ⚡ Quick Deploy

### Prerequisites

- [gcloud CLI](https://cloud.google.com/sdk/docs/install) installed and authenticated
- [kubectl](https://kubernetes.io/docs/tasks/tools/) installed
- Access to `jarvis-swarm-personal-001` GKE cluster

### Deploy in 60 Seconds

```bash
# 1. Clone the repository (if not already)
git clone https://github.com/strategickhaos-swarm-intelligence/Sovereignty-Architecture-Elevator-Pitch-.git
cd Sovereignty-Architecture-Elevator-Pitch-

# 2. Deploy!
./deploy-to-gke.sh
```

The script will:
1. ✅ Get GKE credentials for `jarvis-swarm-personal-001`
2. ✅ Create `queen-system` namespace
3. ✅ Deploy Queen with 2 replicas
4. ✅ Create LoadBalancer (gets public IP)
5. ✅ Show you the IP to point DNS at

### Script Options

```bash
./deploy-to-gke.sh              # Deploy Queen
./deploy-to-gke.sh --status     # Check deployment status
./deploy-to-gke.sh --dry-run    # Preview without applying
./deploy-to-gke.sh --delete     # Remove deployment
```

## 🌐 DNS Configuration

After deployment, you'll receive a LoadBalancer IP. Configure your DNS:

### Cloudflare

```
Type: A
Name: queen
Content: [LOADBALANCER_IP]
Proxy: Off (initially, enable after testing)
```

### Route53 / Other DNS

```
Type: A
Name: queen.strategickhaos.ai
Value: [LOADBALANCER_IP]
TTL: 300
```

## 🔗 GitHub App Configuration

After DNS is working, update your GitHub App:

1. Go to: https://github.com/organizations/strategickhaos-swarm-intelligence/settings/apps/estrategi-khaos-queen-app

2. Set **Webhook URL**:
   ```
   https://queen.strategickhaos.ai/webhooks/github
   ```

3. Set **Callback URL**:
   ```
   https://queen.strategickhaos.ai/oauth/callback
   ```

4. Save changes

## 📁 File Structure

```
bootstrap/k8s/queen/
├── namespace.yaml     # queen-system namespace
├── configmap.yaml     # GitHub App configuration
├── secrets.yaml       # Secrets (fill in before deploy)
├── deployment.yaml    # Queen deployment + embedded code
├── service.yaml       # LoadBalancer service
└── ingress.yaml       # Ingress for queen.strategickhaos.ai

src/queen/
└── queen.cjs          # Queen source code (reference)

deploy-to-gke.sh       # One-shot deployment script
```

## 🔐 Secrets Configuration

Before deploying to production, update `bootstrap/k8s/queen/secrets.yaml` with real values:

```yaml
stringData:
  # GitHub App Private Key
  GITHUB_APP_PRIVATE_KEY: |
    -----BEGIN RSA PRIVATE KEY-----
    [Your actual private key from GitHub App settings]
    -----END RSA PRIVATE KEY-----
  
  # GitHub Webhook Secret
  GITHUB_WEBHOOK_SECRET: "your-actual-webhook-secret"
  
  # OAuth Client Secret
  GITHUB_CLIENT_SECRET: "your-actual-client-secret"
  
  # Discord Bot Token
  DISCORD_BOT_TOKEN: "your-discord-bot-token"
```

⚠️ **Never commit real secrets to git!** Use Kubernetes secrets management or Vault.

## 🔍 Useful Commands

```bash
# View Queen logs
kubectl logs -f deployment/queen -n queen-system

# Check pod status
kubectl get pods -n queen-system

# Get LoadBalancer IP
kubectl get svc queen -n queen-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Port forward for local testing
kubectl port-forward svc/queen 3000:80 -n queen-system

# Restart deployment
kubectl rollout restart deployment/queen -n queen-system

# View all resources
kubectl get all -n queen-system
```

## 🧪 Testing

### Health Check

```bash
# After DNS is configured
curl https://queen.strategickhaos.ai/health

# Via LoadBalancer IP
curl http://[LOADBALANCER_IP]/health

# Via port-forward
kubectl port-forward svc/queen 3000:80 -n queen-system &
curl http://localhost:3000/health
```

### Expected Response

```json
{
  "status": "healthy",
  "service": "queen",
  "timestamp": "2025-01-01T00:00:00.000Z",
  "version": "1.0.0",
  "github": {
    "appId": "1884781",
    "installationId": "97868480"
  }
}
```

### Test Webhook

```bash
curl -X POST https://queen.strategickhaos.ai/webhooks/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: ping" \
  -d '{"zen": "test"}'
```

### Test Signal

```bash
curl -X POST https://queen.strategickhaos.ai/signals/academic \
  -H "Content-Type: application/json" \
  -d '{"type": "test", "source": "manual"}'
```

## 🔧 Troubleshooting

### Pods not starting

```bash
kubectl describe pod -l app.kubernetes.io/name=queen -n queen-system
kubectl logs -l app.kubernetes.io/name=queen -n queen-system --previous
```

### LoadBalancer IP not assigned

```bash
# Check service status
kubectl describe svc queen -n queen-system

# May take 1-2 minutes on GKE
# If stuck, check GCP quotas or firewall rules
```

### Webhook signature errors

1. Ensure `GITHUB_WEBHOOK_SECRET` matches the secret in GitHub App settings
2. Check that the secret is properly base64 encoded (if using `data` instead of `stringData`)

### Connection refused

1. Verify pods are running: `kubectl get pods -n queen-system`
2. Check DNS resolution: `nslookup queen.strategickhaos.ai`
3. Verify firewall rules allow traffic to LoadBalancer IP

## 📈 Monitoring

Queen exposes Prometheus metrics at `/metrics`:

```bash
curl http://[LOADBALANCER_IP]/metrics
```

Configure Prometheus to scrape:

```yaml
- job_name: 'queen'
  static_configs:
    - targets: ['queen.queen-system.svc.cluster.local:80']
```

## 🚀 Next Steps

After Queen is deployed:

1. **Verify health**: `curl https://queen.strategickhaos.ai/health`
2. **Configure GitHub App** with the new webhook URL
3. **Set up Zapier** to POST to `/signals/academic`
4. **Enable TLS** via cert-manager and the ingress
5. **Configure monitoring** with Prometheus/Grafana

---

**Built with 🔥 by the StrategicKhaos Swarm Intelligence collective**

*"Everything points to queen.strategickhaos.ai — and now something lives there."*
