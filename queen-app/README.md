# Queen Orchestrator

> Central coordination hub for the Strategickhaos sovereign infrastructure

👑 **queen.strategickhaos.ai**

## Overview

The Queen Orchestrator serves as the central nervous system for the Strategickhaos ecosystem, routing signals between all system components:

- **Academic Systems** - SNHU/Education integration
- **Financial Systems** - ValorYield Engine operations
- **Governance Systems** - DAO decision tracking
- **Development Systems** - GitHub event processing
- **Treasury Operations** - Dividend distribution coordination

## 🏛️ Legal Foundation

| Entity | EIN | Role |
|--------|-----|------|
| Strategickhaos DAO LLC | 39-2900295 | Autonomous Operations |
| ValorYield Engine PBC | 39-2923503 | Mission-Locked Financial Operations |

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start the server
npm start

# Server runs on http://localhost:3001
```

## 📡 Signal Routes

| Route | Endpoint | Description |
|-------|----------|-------------|
| Academic | `POST /signals/academic` | Educational event routing |
| Financial | `POST /signals/financial` | Treasury and financial operations |
| Governance | `POST /signals/governance` | DAO governance and voting |
| GitHub | `POST /webhooks/github` | GitHub webhook events |
| Treasury | `POST /treasury/allocate` | Treasury allocation requests |

## 🤖 AI Council

The Queen coordinates with an AI Council for decision recommendations:

| Member | Provider | Role |
|--------|----------|------|
| Claude | Anthropic | Reasoning |
| GPT-4 | OpenAI | General |
| Grok | xAI | Analysis |

All AI recommendations require human approval from the Managing Member.

### Consult the Council

```bash
curl -X POST http://localhost:3001/council/consult \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Should we increase emergency fund allocation?",
    "context": {"currentBalance": 50000, "emergencyRequests": 5}
  }'
```

## 👤 Human Operator

- **Name**: Domenic Garza
- **Role**: Managing Member
- **Permissions**: veto, approve, override

The human operator holds final authority over all decisions.

## 📊 API Endpoints

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API documentation |
| GET | `/health` | Health check |
| GET | `/status` | Full system status |
| GET | `/routes` | List all signal routes |

### Signals

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signals/academic` | Academic event signal |
| POST | `/signals/financial` | Financial operation signal |
| POST | `/signals/governance` | Governance decision signal |
| POST | `/webhooks/github` | GitHub webhook receiver |
| POST | `/treasury/allocate` | Treasury allocation signal |
| GET | `/signals` | List signal log |

### AI Council

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/council/consult` | Request council consultation |
| GET | `/council/members` | List council members |
| GET | `/council/consultations` | List past consultations |

## 🔗 Integration with ValorYield

The Queen routes financial signals to the ValorYield Financial OS:

```bash
# Set ValorYield URL
export VALORYIELD_URL=http://localhost:3000

# Send financial signal
curl -X POST http://localhost:3001/signals/financial \
  -H "Content-Type: application/json" \
  -d '{
    "action": "deposit",
    "amount": 5000,
    "source": "Partner Revenue"
  }'
```

## 🏗️ Architecture

```
                    ┌─────────────────────────────────────┐
                    │        👑 QUEEN ORCHESTRATOR        │
                    │      queen.strategickhaos.ai        │
                    └───────────────────┬─────────────────┘
                                        │
            ┌───────────────────────────┼───────────────────────────┐
            │                           │                           │
            ▼                           ▼                           ▼
    ┌───────────────┐         ┌─────────────────┐         ┌───────────────┐
    │   Academic    │         │   Financial     │         │  Governance   │
    │   SNHU/Edu    │         │  ValorYield     │         │     DAO       │
    └───────────────┘         └─────────────────┘         └───────────────┘
            │                           │                           │
            ▼                           ▼                           ▼
    ┌───────────────┐         ┌─────────────────┐         ┌───────────────┐
    │    GitHub     │         │    Treasury     │         │   AI Council  │
    │   Webhooks    │         │   Allocation    │         │ Claude/GPT/Grok│
    └───────────────┘         └─────────────────┘         └───────────────┘
```

## 🚀 Kubernetes Deployment

See `../queen-k8s/` for Kubernetes deployment manifests:

```bash
cd ../queen-k8s
./deploy-to-gke.sh
```

## 📜 Wyoming DAO Compliance

The Queen Orchestrator operates under:
- Wyoming DAO LLC Statute
- Public Benefit Corporation governance
- Transparent audit logging
- AI-assisted, human-supervised decision making

## 📄 License

MIT License - See LICENSE file for details.

---

**Built with 💜 by the Strategickhaos Swarm Intelligence collective**
