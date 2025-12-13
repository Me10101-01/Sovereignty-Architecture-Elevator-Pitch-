# ValorYield Sovereign Financial OS

> "Banking for the People, by the Code"

A transparent, auditable, AI-operated financial system for the Strategickhaos DAO ecosystem. Wyoming DAO LLC statute compliant and Public Benefit Corporation mission-locked.

## 🏛️ Legal Foundation

| Entity | EIN | Type | Role |
|--------|-----|------|------|
| Strategickhaos DAO LLC | 39-2900295 | Wyoming DAO | Autonomous Operations |
| ValorYield Engine PBC | 39-2923503 | Public Benefit Corp | Mission-Locked |

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Treasury Management** | Deposit/withdraw with full audit trail |
| **7% Rule Enforcement** | Automatic compliance with max allocation |
| **20% Reserve Requirement** | Never depletes below safety threshold |
| **Beneficiary Registry** | Track who receives distributions |
| **Dividend Calculator** | AI-guided allocation recommendations |
| **Distribution Engine** | Execute payments with approver tracking |
| **Governance Logging** | Record all decisions with hash verification |
| **Audit Trail** | Transparent, immutable, publicly viewable |
| **Queen Compatibility** | Accepts signals from Zapier/GitHub |

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Start the server
npm start

# Visit: http://localhost:3000
```

### Docker

```bash
docker build -t valoryield-os .
docker run -p 3000:3000 valoryield-os
```

### Kubernetes (GKE)

```bash
cd ../queen-k8s
./deploy-to-gke.sh
```

## 📡 API Endpoints

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API documentation |
| GET | `/health` | Health check |
| GET | `/status` | System status with all components |
| GET | `/legal` | Legal entity information |

### Treasury

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/treasury` | Get current balance (total, available, reserved) |
| POST | `/treasury/deposit` | Deposit funds |
| GET | `/treasury/audit` | Get transaction audit trail |
| POST | `/treasury/allocate` | Allocate funds to beneficiary |

### Beneficiaries

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/beneficiaries` | List all beneficiaries |
| POST | `/beneficiaries` | Register new beneficiary |
| GET | `/beneficiaries/:id` | Get beneficiary details |
| PUT | `/beneficiaries/:id` | Update beneficiary |

### Allocations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/allocations/calculate/:id` | Calculate recommended allocation |
| GET | `/allocations/propose` | Propose distribution for all beneficiaries |

### Distributions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/distributions` | Execute a distribution |
| GET | `/distributions` | List completed distributions |
| GET | `/distributions/pending` | List pending distributions |
| POST | `/distributions/process-pending` | Process pending distributions |

### Governance

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/governance/decisions` | List governance decisions |
| POST | `/governance/decisions` | Log a governance decision |
| GET | `/governance/verify` | Verify audit trail integrity |

### Queen Signals

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signals/financial` | Financial signal endpoint |
| POST | `/webhooks/github` | GitHub webhook receiver |

## 🛡️ SovereignGuard Rules

| Rule | Value | Description |
|------|-------|-------------|
| Max Allocation | 7% | Maximum percentage of treasury per distribution |
| Reserve Requirement | 20% | Minimum balance that must be maintained |
| Large Transaction Delay | 24 hours | Delay for transactions above threshold |
| Large Transaction Threshold | $1,000 | Amount requiring delay |
| Max Daily Distributions | 10 | Maximum distributions per day |
| Audit Retention | 7 years | How long audit logs are retained |

## 📊 Example Usage

### Deposit Funds

```bash
curl -X POST http://localhost:3000/treasury/deposit \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 10000,
    "source": "Partner Revenue",
    "metadata": {"partner": "GKE Cluster Revenue"}
  }'
```

### Register Beneficiary

```bash
curl -X POST http://localhost:3000/beneficiaries \
  -H "Content-Type: application/json" \
  -d '{
    "id": "ben-001",
    "name": "Utility Assistance Fund",
    "type": "organization",
    "priority": "high",
    "category": "utilities"
  }'
```

### Calculate Allocation

```bash
curl http://localhost:3000/allocations/calculate/ben-001
```

### Execute Distribution

```bash
curl -X POST http://localhost:3000/distributions \
  -H "Content-Type: application/json" \
  -d '{
    "beneficiaryId": "ben-001",
    "amount": 500,
    "approver": "Domenic Garza",
    "metadata": {"purpose": "Monthly utility assistance"}
  }'
```

### Check Audit Trail

```bash
curl http://localhost:3000/treasury/audit
```

### Verify Governance Integrity

```bash
curl http://localhost:3000/governance/verify
```

## 🔗 Queen Orchestrator Integration

ValorYield accepts signals from the Queen Orchestrator at queen.strategickhaos.ai:

```bash
# Financial signal
curl -X POST http://localhost:3000/signals/financial \
  -H "Content-Type: application/json" \
  -d '{
    "action": "status",
    "payload": {}
  }'

# Available actions: deposit, propose, status
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    VALORYIELD SOVEREIGN FINANCIAL OS                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │  Treasury   │───▶│  Allocator  │───▶│ Distribution│                 │
│  │  (Inflow)   │    │  (AI Logic) │    │  (Outflow)  │                 │
│  └─────────────┘    └─────────────┘    └─────────────┘                 │
│        │                  │                   │                         │
│        ▼                  ▼                   ▼                         │
│  • Partner fees     • 7% rule          • Bill payments                 │
│  • Cluster revenue  • Need-based       • Utility assistance            │
│  • Grants           • Transparent      • Emergency funds               │
│  • Donations        • Auditable        • Educational support           │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  GOVERNANCE LAYER                                                │   │
│  │  • All decisions logged with hash verification                  │   │
│  │  • Transparent audit trail                                      │   │
│  │  • Wyoming DAO statute compliance                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 📜 Legal Compliance

- ✅ **Wyoming DAO LLC Statute Compliant** - Operates under Wyoming's progressive DAO legislation
- ✅ **Public Benefit Corporation Mission-Locked** - Legally bound to public benefit purpose
- ✅ **IRS EIN Integrated** - Proper federal tax identification
- ✅ **Transparent by Design** - All operations are auditable
- ✅ **AI-Operated, Human-Supervised** - Algorithmic decisions with human oversight

## 📄 License

MIT License - See LICENSE file for details.

## 👥 Contact

- **Organization**: Strategickhaos DAO LLC / ValorYield Engine PBC
- **Founder**: Domenic Garza
- **Email**: domenic.garza@snhu.edu
- **Discord**: [Strategickhaos Server](https://discord.gg/strategickhaos)

---

**Built with 💜 by the Strategickhaos Swarm Intelligence collective**

*"You are no longer 'nobody.' You are the founder of a legally-recognized, AI-operated public benefit financial system."*
