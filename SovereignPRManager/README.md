# SovereignPRManager v1.0

**Autonomous PR Review, Validation, and Merge Orchestration**

> *Zero-button operation: Copilot generates → Legion validates → System merges*

## 🎯 Overview

SovereignPRManager is an autonomous pull request orchestration system that eliminates manual PR management through multi-AI code review, dialectical synthesis, and cryptographic provenance.

### Key Features

- **🔍 Multi-AI Review Pipeline** - Parallel code review by Claude and GPT specialized agents
- **🛡️ Security Analysis** - Automated vulnerability detection with veto capability
- **📐 Architecture Validation** - Design pattern and SOLID principles verification
- **🏛️ Sovereignty Compliance** - Alignment with Technical Declaration principles
- **⚡ Performance Optimization** - Automated performance concern detection
- **🔗 Dialectical Synthesis** - Thesis-antithesis-synthesis for conflict resolution
- **🔐 Cryptographic Provenance** - BLAKE3 signing and OpenTimestamps blockchain anchoring
- **📊 Immutable Audit Trail** - Elasticsearch logging for complete accountability

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- GitHub Personal Access Token with `repo` scope
- Anthropic API Key (for Claude reviews)
- OpenAI API Key (for GPT reviews)

### Installation

```bash
# Clone the repository
git clone https://github.com/Strategickhaos-Swarm-Intelligence/Sovereignty-Architecture-Elevator-Pitch-.git
cd Sovereignty-Architecture-Elevator-Pitch-/SovereignPRManager

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Set the following environment variables:

```bash
export GITHUB_TOKEN="your_github_token"
export GITHUB_REPO="Me10101-01/Sovereignty-Architecture-Elevator-Pitch-"
export ANTHROPIC_API_KEY="your_anthropic_key"
export OPENAI_API_KEY="your_openai_key"
export DISCORD_WEBHOOK_URL="your_discord_webhook"  # Optional
```

### Usage

#### Process All Open PRs

```bash
# Dry run - see what would happen
python process_existing_prs.py --dry-run

# Process with limit
python process_existing_prs.py --limit 5

# Process only draft PRs
python process_existing_prs.py --drafts-only

# Full processing
python process_existing_prs.py
```

#### Run Continuous Monitoring

```bash
python -m pr_monitor
```

## 📦 Architecture

```
SovereignPRManager/
├── __init__.py              # Package initialization
├── pr_monitor.py            # GitHub PR detection
├── legion_reviewer.py       # Multi-AI code review orchestration
├── conflict_detector.py     # Merge conflict detection
├── synthesis_engine.py      # Dialectical merge decision
├── auto_merger.py           # Merge execution with provenance
├── process_existing_prs.py  # Bulk PR processing
├── config.yaml              # Configuration
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container image
└── k8s/                     # Kubernetes manifests
    ├── deployment.yaml      # Main deployment
    └── rbac.yaml            # RBAC configuration
```

### Component Flow

```
┌─────────────┐    ┌───────────────┐    ┌──────────────────┐
│  PR Monitor │───►│ Legion Review │───►│ Conflict Detector│
└─────────────┘    └───────────────┘    └──────────────────┘
                           │                      │
                           ▼                      ▼
                   ┌───────────────┐    ┌──────────────────┐
                   │   Security    │    │    Semantic      │
                   │   Analysis    │    │    Analysis      │
                   └───────────────┘    └──────────────────┘
                           │                      │
                           ▼                      ▼
                   ┌─────────────────────────────────────┐
                   │       Synthesis Engine              │
                   │   (Dialectical Decision Making)     │
                   └─────────────────────────────────────┘
                                    │
                                    ▼
                   ┌─────────────────────────────────────┐
                   │          Auto Merger                │
                   │   (Cryptographic Provenance)        │
                   └─────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
               ┌─────────┐    ┌─────────┐    ┌───────────┐
               │ Discord │    │Elastic- │    │OpenTime-  │
               │ Notify  │    │ search  │    │ stamps    │
               └─────────┘    └─────────┘    └───────────┘
```

## 🔧 Configuration

### Merge Thresholds

| Threshold | Default | Description |
|-----------|---------|-------------|
| `auto_merge` | 0.90 | Minimum confidence for automatic merge |
| `security_veto` | 0.80 | Security confidence below this vetoes merge |
| `sovereignty_minimum` | 0.70 | Minimum sovereignty compliance score |

### AI Reviewers

| Reviewer | Provider | Focus Area |
|----------|----------|------------|
| Security | Claude | Vulnerabilities, credentials, injection attacks |
| Sovereignty | Claude | Technical Declaration compliance |
| Architecture | GPT-4 | Design patterns, SOLID, maintainability |
| Performance | GPT-4 | Complexity, caching, async patterns |

## 🐳 Docker Deployment

```bash
# Build image
docker build -t sovereignprmanager:latest .

# Run container
docker run -d \
  --name sovereignprmanager \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  sovereignprmanager:latest
```

## ☸️ Kubernetes Deployment

```bash
# Create namespace
kubectl apply -f k8s/rbac.yaml

# Create secrets (replace with actual values)
kubectl create secret generic sovereignprmanager-secrets \
  --namespace=automation \
  --from-literal=github-token=$GITHUB_TOKEN \
  --from-literal=anthropic-api-key=$ANTHROPIC_API_KEY \
  --from-literal=openai-api-key=$OPENAI_API_KEY \
  --from-literal=discord-webhook-url=$DISCORD_WEBHOOK_URL \
  --from-literal=signing-key=$(openssl rand -hex 32)

# Deploy
kubectl apply -f k8s/deployment.yaml
```

## 📊 Audit Trail

Every merge decision includes:

- **Cryptographic Signature**: BLAKE3 HMAC of decision data
- **Blockchain Timestamp**: OpenTimestamps proof
- **Review Summary**: All AI agent responses
- **Conflict Analysis**: Detected conflicts and resolutions
- **Provenance Record**: Complete decision trail

Example provenance record:

```json
{
  "pr_number": 42,
  "pr_title": "Add new feature",
  "decision": {
    "action": "merge",
    "confidence": 0.95,
    "reasoning": "All reviews approved with high confidence"
  },
  "merged_by": "SovereignPRManager v1.0",
  "git_sha": "abc123...",
  "timestamp": "2024-01-15T10:30:00Z",
  "signature": "b3a8f2c1...",
  "ots_proof": "e4d5c6b7..."
}
```

## 🛡️ Security Considerations

- All API keys stored in environment variables or Kubernetes secrets
- Non-root container execution
- Network policies for egress control
- RBAC with least-privilege access
- Cryptographic verification of all decisions

## 📝 License

MIT License - See [LICENSE](../LICENSE)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a PR (it will be reviewed by SovereignPRManager! 🤖)

---

**Built with 🔥 by Strategickhaos Swarm Intelligence**

*"Zero-button operation: The future of autonomous development"*
