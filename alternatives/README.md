# Self-Hosted Alternatives

This directory documents self-hosted alternatives for all critical vendor dependencies, in alignment with the **Zero Vendor Lock-in Principals** (ZVLI-2025-001).

## Purpose

Maintain operational sovereignty by ensuring every vendor dependency has a viable self-hosted alternative that can be activated within 24 hours.

## Directory Structure

```
alternatives/
├── README.md (this file)
├── self_hosted/
│   ├── gitea_setup.md
│   ├── keycloak_config.md
│   ├── matrix_element_deployment.md
│   ├── ollama_llm_stack.md
│   ├── prometheus_grafana_monitoring.md
│   └── local_kubernetes.md
├── vendor_comparison/
│   ├── code_hosting.md
│   ├── identity_providers.md
│   ├── llm_services.md
│   └── cloud_providers.md
└── migration_guides/
    ├── github_to_gitea.md
    ├── oauth_to_keycloak.md
    ├── discord_to_matrix.md
    └── openai_to_ollama.md
```

## Self-Hosted Alternatives Status

| Vendor Service | Self-Hosted Alternative | Status | Operational Nodes |
|----------------|------------------------|--------|-------------------|
| GitHub | Gitea | ✅ Operational | 2 instances |
| Google OAuth | Keycloak | ✅ Ready | 1 instance |
| Discord | Matrix/Element | ✅ Operational | 1 server |
| OpenAI | Ollama + Qwen | ✅ Operational | 4 nodes + 8 routers |
| GCP | Local K8s | ✅ Operational | 4-node cluster |
| Datadog | Prometheus/Grafana | ✅ Operational | Integrated |
| MongoDB Atlas | Self-hosted MongoDB | ✅ Operational | Container |
| Stripe | Thread Bank BaaS | 🔄 Integration | API configured |

**Legend:**
- ✅ Operational: Tested and production-ready
- 🔄 Integration: Configured but not fully tested
- ⏳ Planned: Documentation exists, implementation pending

## Infrastructure Overview

### Local Compute Nodes
- **Athena** - Primary local K8s node
- **Lyra** - Secondary K8s node
- **Nova** - Tertiary K8s node
- **iPower** - Backup node

### Router SOC Inference
- 8 routers running Ollama for distributed LLM inference
- Failover LLM capability independent of cloud providers

### Network Architecture
- Multi-path routing for redundancy
- VPN mesh for secure inter-node communication
- Satellite backup (Starshield/LoRa) for emergency

## Quick Start Guides

### Activate Gitea (GitHub Alternative)
```bash
# Access Gitea instance
ssh admin@gitea.strategickhaos.internal

# Verify replication status
gitea admin repo-sync --all

# Test clone operation
git clone http://gitea.strategickhaos.internal/strategickhaos/main-repo.git
```

### Activate Keycloak (OAuth Alternative)
```bash
# Start Keycloak container
docker-compose -f keycloak/docker-compose.yml up -d

# Import user database
./keycloak/import_users.sh

# Test authentication
curl -X POST http://keycloak.internal/auth/realms/strategickhaos/protocol/openid-connect/token
```

### Activate Matrix (Discord Alternative)
```bash
# Start Matrix Synapse server
docker-compose -f matrix/docker-compose.yml up -d

# Configure Element client
cp matrix/element-config.json /var/www/element/

# Import Discord history
python3 matrix/import_discord.py --channel-id ALL
```

### Activate Ollama (OpenAI Alternative)
```bash
# Verify Ollama nodes
for node in athena lyra nova ipower; do
  ssh $node "ollama list"
done

# Load Qwen 2.5 72B model
ollama pull qwen2.5:72b

# Test inference
curl http://ollama.internal:11434/api/generate -d '{
  "model": "qwen2.5:72b",
  "prompt": "Test sovereignty"
}'
```

### Activate Local K8s (GCP Alternative)
```bash
# Check cluster status
kubectl cluster-info

# Deploy workload from GCP
kubectl apply -f gcp-migration/deployment.yaml

# Verify pods running
kubectl get pods -A
```

## Certification Levels

### 💎 Platinum Sovereign Systems
These systems have NO vendor in the critical path:
- ✅ Code Hosting (Gitea primary)
- ✅ LLM Services (Ollama primary)
- ✅ Monitoring (Prometheus/Grafana)

### 🥇 Gold - Self-Hosted Ready
Self-hosted alternative tested and operational:
- ✅ Local Kubernetes cluster
- ✅ Matrix/Element server
- ✅ Keycloak identity

### 🥈 Silver - Alternative Configured
Self-hosted alternative configured, not yet primary:
- ✅ MongoDB
- 🔄 Payment processing (Thread Bank)

## Maintenance Schedule

| System | Health Check | Update Frequency | Last Verified |
|--------|--------------|------------------|---------------|
| Gitea | Daily | Weekly | 2025-12-07 |
| Keycloak | Daily | Monthly | 2025-12-05 |
| Matrix | Daily | Weekly | 2025-12-06 |
| Ollama | Hourly | As needed | 2025-12-07 |
| Local K8s | Hourly | Weekly | 2025-12-07 |
| Prometheus | Continuous | Monthly | 2025-12-01 |

## Cost Comparison

| Service | Vendor Cost | Self-Hosted Cost | Savings |
|---------|-------------|------------------|---------|
| Code Hosting | $21/mo (GitHub Teams) | $15/mo (hosting) | 29% |
| LLM API | $200-500/mo (OpenAI) | $80/mo (power) | 60-84% |
| Monitoring | $150/mo (Datadog) | $30/mo (hosting) | 80% |
| Identity | $120/mo (Okta) | $25/mo (hosting) | 79% |
| **Total** | ~$491-791/mo | ~$150/mo | **70-81%** |

*Plus: Complete data sovereignty and vendor independence*

## Disaster Recovery

### Emergency Failover Process
1. Detect vendor outage (automated monitoring)
2. Activate emergency communications (satellite if needed)
3. Execute failover scripts from `escape_routes.yaml`
4. Verify self-hosted alternatives operational
5. Update DNS/routing to internal infrastructure
6. Monitor for 48 hours, adjust as needed

### Recovery Time Objectives (RTO)
- Critical services: < 15 minutes
- Standard services: < 2 hours
- Full migration: < 24 hours

### Recovery Point Objectives (RPO)
- Code repositories: Real-time (continuous sync)
- Databases: < 5 minutes (replication)
- Configuration: < 1 hour (version control)

## Contact

- **Infrastructure Team:** infrastructure@strategickhaos.ai
- **Emergency:** See `escape_routes.yaml` emergency protocols
- **Documentation:** All guides in this directory

---

*True sovereignty means owning your infrastructure.*
