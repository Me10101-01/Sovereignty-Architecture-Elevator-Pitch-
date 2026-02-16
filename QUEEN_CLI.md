# QUEEN CLI - Command & Control Interface
## Sovereign Command Line Interface for Empire Management

**Version:** 1.0  
**Codename:** QUEEN  
**Classification:** COMMAND & CONTROL  
**Governing Entity:** Strategickhaos DAO LLC

---

## OVERVIEW

The **Queen CLI** is the unified command-line interface for managing the entire Strategickhaos sovereign empire. It provides secure, GPG-signed commands for deployment, monitoring, security operations, and governance.

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUEEN CLI ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  $ queen status                                                 │
│  $ queen treasury --balance                                     │
│  $ queen deploy --service khaosbase                            │
│  $ queen chaos --inject treasury-delay                         │
│                                                                 │
│  ┌─────────────────┐                                           │
│  │   LOCAL CLI     │                                           │
│  │   (queen-cli)   │                                           │
│  └────────┬────────┘                                           │
│           │ GPG Sign                                            │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │  PRIVACY LAYER  │                                           │
│  │  ├─ Tor         │                                           │
│  │  ├─ WireGuard   │                                           │
│  │  └─ Tailscale   │                                           │
│  └────────┬────────┘                                           │
│           │ Encrypted                                           │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │  QUEEN SERVER   │                                           │
│  │  (GKE/Local)    │                                           │
│  └─────────────────┘                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 INSTALLATION

### Prerequisites
- GPG key configured and trusted
- WireGuard or Tailscale connectivity to Queen server
- Python 3.11+ or Go 1.21+

### Install from Source

```bash
# Clone the repository
git clone https://github.com/strategickhaos/queen-cli
cd queen-cli

# Install dependencies
pip install -r requirements.txt
# OR for Go version:
# go install ./cmd/queen

# Configure
cp .env.example .env
# Edit .env with your GPG key ID and server endpoint

# Verify installation
queen --version
```

### Install via Package Manager

```bash
# NixOS
nix-env -iA nixpkgs.queen-cli

# Homebrew (macOS/Linux)
brew install strategickhaos/tap/queen-cli

# APT (Debian/Ubuntu)
curl -fsSL https://pkg.strategickhaos.ai/gpg | sudo apt-key add -
echo "deb https://pkg.strategickhaos.ai stable main" | sudo tee /etc/apt/sources.list.d/khaos.list
sudo apt update && sudo apt install queen-cli
```

---

## 📋 COMMAND REFERENCE

### Empire Status

```bash
# View all systems status
queen status

# Check specific cluster
queen status --cluster jarvis

# Treasury health
queen status --treasury

# Detailed health with metrics
queen status --verbose --format json
```

### Deployment Operations

```bash
# Deploy a service
queen deploy khaosbase

# Deploy with specific version
queen deploy khaosbase --version v2.1.0

# Deploy to specific environment
queen deploy khaosbase --env production

# Rollback to previous version
queen rollback khaosbase v1.2

# Scale service
queen scale khaosbase --replicas 3

# Auto-scale configuration
queen scale khaosbase --autoscale --min 2 --max 10
```

### Security & Chaos Engineering

```bash
# Inject network partition
queen chaos --inject network-partition

# Simulate bank timeout
queen chaos --inject bank-timeout

# Test service resilience
queen chaos --inject pod-failure --service khaosbase

# Run security audit
queen audit --export json

# Vulnerability scan
queen audit --scan --severity high

# Generate compliance report
queen audit --compliance --standard soc2
```

### AI Board Operations

```bash
# Submit proposal to AI Board
queen board --vote "Deploy new feature X"

# Check consensus status
queen board --consensus

# View voting history
queen board --history

# Emergency override (requires multi-sig)
queen board --override --reason "Emergency security patch"

# View AI Board composition
queen board --members
```

### Treasury Management

```bash
# View current balance
queen treasury --balance

# Distribute charitable contribution (7%)
queen treasury --distribute 7%

# Generate monthly report
queen treasury --report monthly

# View transaction history
queen treasury --history --format csv

# Set up recurring distribution
queen treasury --schedule --amount 7% --frequency monthly
```

### Infrastructure Management

```bash
# List all clusters
queen cluster list

# Create new cluster
queen cluster create --name athena-prod --region us-central1

# Scale cluster nodes
queen cluster scale jarvis --nodes 5

# Upgrade cluster
queen cluster upgrade jarvis --version 1.28

# Get cluster credentials
queen cluster creds jarvis
```

### Monitoring & Logs

```bash
# Tail logs from service
queen logs khaosbase --follow

# Query logs with filter
queen logs --service khaosbase --level error --since 1h

# Export logs
queen logs --export --format json --output logs.json

# View metrics
queen metrics khaosbase --window 1h

# Create alert rule
queen alert create --service khaosbase --condition "error_rate > 5%"
```

### Secrets Management

```bash
# List secrets
queen secrets list

# Create new secret
queen secrets create api-key --value "sk-..."

# Rotate secret
queen secrets rotate database-password

# Grant access to secret
queen secrets grant api-key --service khaosbase

# Audit secret access
queen secrets audit api-key
```

### Networking

```bash
# List VPN peers
queen vpn list

# Add new peer
queen vpn add-peer --name mobile-device

# Generate WireGuard config
queen vpn config --peer mobile-device --output mobile.conf

# Check Tailscale status
queen tailscale status

# Approve new Tailscale node
queen tailscale approve --node athena-laptop
```

---

## 🔐 SECURITY MODEL

### GPG Signing

All Queen CLI commands are cryptographically signed using GPG to ensure:
- **Authentication:** Verify command origin
- **Integrity:** Detect tampering
- **Non-repudiation:** Audit trail of all actions

```bash
# Configure GPG key
queen config set gpg-key-id "0x1234567890ABCDEF"

# Verify GPG configuration
queen config verify

# Sign command explicitly (usually automatic)
queen deploy khaosbase --sign
```

### Privacy Layer

Commands are routed through configurable privacy layers:

```bash
# Route through Tor
queen config set privacy-mode tor

# Route through WireGuard
queen config set privacy-mode wireguard

# Route through Tailscale
queen config set privacy-mode tailscale

# Direct connection (development only)
queen config set privacy-mode direct
```

### Multi-Factor Authentication

Critical operations require additional verification:

```bash
# Configure YubiKey
queen config set mfa yubikey

# Configure TOTP
queen config set mfa totp

# Require MFA for specific operations
queen config set mfa-required "deploy,rollback,board"
```

---

## ⚙️ CONFIGURATION

### Environment Variables

```bash
# Queen server endpoint
export QUEEN_SERVER_URL="https://queen.strategickhaos.ai"

# GPG key ID
export QUEEN_GPG_KEY="0x1234567890ABCDEF"

# Privacy mode
export QUEEN_PRIVACY_MODE="wireguard"

# Default cluster
export QUEEN_DEFAULT_CLUSTER="jarvis"

# Output format
export QUEEN_OUTPUT_FORMAT="table"  # table, json, yaml
```

### Configuration File

`~/.config/queen/config.yaml`:

```yaml
server:
  url: https://queen.strategickhaos.ai
  timeout: 30s
  
security:
  gpg_key_id: "0x1234567890ABCDEF"
  privacy_mode: wireguard
  mfa_enabled: true
  mfa_method: yubikey
  
defaults:
  cluster: jarvis
  output_format: table
  
clusters:
  jarvis:
    project: strategickhaos-empire
    region: us-central1
    zone: us-central1-a
    
  athena:
    project: strategickhaos-prod
    region: us-east1
    zone: us-east1-b
```

---

## 🧪 EXAMPLES

### Complete Deployment Workflow

```bash
# 1. Check current status
queen status --cluster jarvis

# 2. Deploy new version to staging
queen deploy khaosbase --version v2.2.0 --env staging

# 3. Run smoke tests
queen test khaosbase --env staging --suite smoke

# 4. Check for errors
queen logs khaosbase --env staging --level error --since 10m

# 5. Deploy to production
queen deploy khaosbase --version v2.2.0 --env production

# 6. Monitor deployment
queen status khaosbase --watch

# 7. Verify health
queen audit khaosbase --health-check
```

### Chaos Engineering Session

```bash
# 1. Baseline metrics
queen metrics khaosbase --window 5m --export baseline.json

# 2. Inject failure
queen chaos --inject pod-failure --service khaosbase --duration 2m

# 3. Monitor impact
queen metrics khaosbase --watch

# 4. Compare results
queen metrics khaosbase --window 5m --compare baseline.json

# 5. Generate report
queen chaos --report --export chaos-report.pdf
```

### Emergency Response

```bash
# 1. Identify issue
queen status --all --verbose

# 2. Check recent changes
queen audit --history --since 1h

# 3. Rollback if needed
queen rollback khaosbase --to-stable

# 4. Scale up for traffic
queen scale khaosbase --replicas 10

# 5. Enable emergency mode
queen config set emergency-mode true

# 6. Notify AI Board
queen board --emergency "Production incident: rolling back khaosbase"
```

---

## 🔧 DEVELOPMENT

### Building from Source

```bash
# Python version
python setup.py build
python setup.py install

# Go version
go build -o queen ./cmd/queen
go install ./cmd/queen
```

### Running Tests

```bash
# Unit tests
queen test --unit

# Integration tests
queen test --integration

# E2E tests
queen test --e2e --cluster test-cluster
```

### Contributing

See `CONTRIBUTING.md` for development guidelines.

---

## 📊 TELEMETRY

Queen CLI collects minimal, privacy-preserving telemetry:
- Command usage statistics (no arguments)
- Error rates and types
- Performance metrics
- GPG signature verification success rate

All telemetry can be disabled:

```bash
queen config set telemetry false
```

---

## 📚 ADDITIONAL RESOURCES

- [Queen CLI GitHub Repository](https://github.com/strategickhaos/queen-cli)
- [API Documentation](https://docs.strategickhaos.ai/queen-cli)
- [Security Advisories](https://security.strategickhaos.ai)
- [Community Forum](https://forum.strategickhaos.ai)

---

**Document Status:** COMMAND REFERENCE  
**Version:** 1.0  
**Last Updated:** 2025-12-07

---

*"Command with sovereignty. Execute with precision."* ⚔️👑
