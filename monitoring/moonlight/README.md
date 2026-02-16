# 🌙 Moonlight Telemetry Agent

Session intelligence tracking for the Strategickhaos Sovereign Intelligence Stack.

## Overview

Moonlight is a telemetry agent that monitors and records session activity across the Strategickhaos ecosystem. It tracks AI interactions, knowledge graph evolution, system metrics, and board member contributions, storing them in KhaosBase for cryptographic verification and historical analysis.

### Key Features

- **Session Tracking**: Records complete session metadata and lifecycle
- **Event Logging**: Captures commands, file changes, AI queries, and knowledge updates
- **System Metrics**: Monitors CPU, memory, and network usage
- **GPG Signing**: Cryptographically signs all telemetry events (key: AE5519579584DEF5)
- **KhaosBase Integration**: Pushes telemetry to centralized knowledge base
- **Multi-Node Support**: Works across Athena, Nova, Lyra, and other nodes
- **Board Member DNA**: Tracks individual AI board member contributions

## Quick Start

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run in test mode**:
   ```bash
   python moonlight_agent.py --test
   ```

3. **View session report**:
   ```bash
   cat telemetry/moonlight_*_summary.json | jq
   ```

### Docker Deployment

1. **Build the image**:
   ```bash
   docker build -t strategickhaos/moonlight-agent:1.0.0 .
   ```

2. **Run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **View logs**:
   ```bash
   docker-compose logs -f moonlight-agent
   ```

### Kubernetes Deployment

1. **Apply the DaemonSet**:
   ```bash
   kubectl apply -f k8s-daemonset.yaml
   ```

2. **Check status**:
   ```bash
   kubectl get daemonset -n moonlight-telemetry
   kubectl get pods -n moonlight-telemetry
   ```

3. **View logs**:
   ```bash
   kubectl logs -n moonlight-telemetry -l app=moonlight-agent -f
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NODE_NAME` | Node identifier (Athena, Nova, Lyra) | Hostname |
| `OBSIDIAN_VAULT` | Obsidian vault name | `Athena` |
| `BOARD_MEMBER` | AI board member identifier | `Claude Opus 4.5` |
| `KHAOSBASE_URL` | KhaosBase API endpoint | `http://localhost:8080` |
| `KHAOSBASE_API_KEY` | API authentication key | - |
| `GPG_KEY_ID` | GPG signing key ID | `AE5519579584DEF5` |
| `TELEMETRY_DIR` | Output directory for telemetry | `./telemetry` |
| `AUTO_PUSH_TELEMETRY` | Auto-push to KhaosBase | `true` |
| `SESSION_TYPE` | Session type (local/codespace/remote) | Auto-detected |

### Configuration File

Create a `config.yaml`:

```yaml
node_name: "athena"
vault_name: "Athena"
board_member: "Claude Opus 4.5"
khaosbase_url: "http://khaosbase:8080"
gpg_key_id: "AE5519579584DEF5"
telemetry_dir: "/data/telemetry"
auto_push: true
```

## Architecture

### Data Flow

```
Session Events
    ↓
Moonlight Agent
    ↓
GPG Signature
    ↓
KhaosBase Storage
    ↓
Analytics & Reporting
```

### Event Types

- **command**: Shell command execution
- **file_change**: File modification events
- **ai_query**: AI model interactions
- **knowledge_update**: Knowledge graph changes
- **system_metric**: System resource usage
- **network_activity**: Network I/O events

### Schema

The telemetry schema is defined in `telemetry_schema.yaml`. Key collections:

- **sessions**: Session-level metadata
- **events**: Individual telemetry events
- **summaries**: Aggregated session statistics
- **knowledge_graph**: Knowledge evolution tracking
- **board_contributions**: Board member DNA tracking

## Usage Examples

### Python API

```python
from moonlight_agent import MoonlightAgent

# Initialize agent
agent = MoonlightAgent()

# Record events
agent.record_command('npm run build', exit_code=0, duration_ms=1234)
agent.record_file_change('/path/to/file.ts', 'modified')
agent.record_ai_interaction(
    query="How do I implement X?",
    response="Here's how...",
    model="claude-opus-4.5"
)

# Generate report
agent.print_session_report()

# Save data
agent.save_session_data()
```

### CLI Usage

```bash
# Run in daemon mode
python moonlight_agent.py

# Test mode with custom output
python moonlight_agent.py --test --output-dir /tmp/telemetry

# Custom config
python moonlight_agent.py --config config.yaml
```

## Integration

### With Obsidian

Monitor Obsidian vault changes:

```python
agent.record_knowledge_update(
    vault='Athena',
    note='telemetry-patterns.md',
    update_type='create'
)
```

### With GitHub Codespaces

Moonlight auto-detects Codespace environments:

```bash
export CODESPACES=true
python moonlight_agent.py
```

### With Prometheus

Metrics are exposed on port 9100:

```yaml
scrape_configs:
  - job_name: 'moonlight'
    static_configs:
      - targets: ['moonlight-agent:9100']
```

## Monitoring

### Session Reports

View real-time session statistics:

```bash
python -c "from moonlight_agent import MoonlightAgent; \
           agent = MoonlightAgent(); \
           agent.print_session_report()"
```

### Telemetry Files

Output structure:

```
telemetry/
├── moonlight_20251207_120000_athena_abc123_metadata.json
├── moonlight_20251207_120000_athena_abc123_events.jsonl
└── moonlight_20251207_120000_athena_abc123_summary.json
```

### Grafana Dashboards

Import the Moonlight dashboard from `grafana-dashboard.json` (if available).

## Security

### GPG Signatures

All events are signed with GPG key `AE5519579584DEF5`:

```python
# Verify signature
from moonlight_agent import GPGSigner

signer = GPGSigner('AE5519579584DEF5')
is_valid = signer.verify_signature(data, signature)
```

### Data Privacy

- Telemetry data contains hashes, not raw content
- Query/response content is hashed, not stored
- File paths are relative, not absolute
- Network data shows bytes, not content

## Troubleshooting

### Common Issues

**Agent not starting:**
```bash
# Check dependencies
pip list | grep -E 'pyyaml|psutil|requests'

# Check permissions
ls -la /data/telemetry
```

**KhaosBase connection failed:**
```bash
# Test connection
curl http://khaosbase:8080/health

# Check API key
echo $KHAOSBASE_API_KEY
```

**GPG signing errors:**
```bash
# Check GPG key
gpg --list-keys AE5519579584DEF5

# Import key if missing
gpg --import key.asc
```

## Development

### Running Tests

```bash
pytest tests/
pytest --cov=moonlight_agent
```

### Code Quality

```bash
# Format
black moonlight_agent.py

# Lint
flake8 moonlight_agent.py
mypy moonlight_agent.py
```

### VS Code DevContainer

Open in VS Code with Remote-Containers extension:

```bash
code .
# Select "Reopen in Container"
```

## Roadmap

- [ ] Real-time event streaming via WebSocket
- [ ] Machine learning on telemetry patterns
- [ ] Automatic anomaly detection
- [ ] Integration with ONSIT benchmarking
- [ ] Multi-vault synchronization tracking
- [ ] NFT signature verification
- [ ] Bloom's taxonomy bottleneck mapping

## License

MIT License - Strategickhaos DAO LLC

## Support

- **Documentation**: `/monitoring/moonlight/README.md`
- **Issues**: GitHub Issues
- **Discord**: Strategickhaos DAO Server
- **Email**: support@strategickhaos.io

## Related Components

- **ONSIT**: Knowledge graph benchmarking
- **Empire DNA**: Ecosystem health tracker
- **Network Scout**: Battlefield intelligence
- **Autistic Audit DNA**: Bottleneck → Revenue mapper

---

**Part of the Strategickhaos Sovereign Intelligence Stack**

```
╔══════════════════════════════════════════╗
║  2. 🌙 Moonlight: Session telemetry     ║
║     └── "What happened this session?"    ║
╚══════════════════════════════════════════╝
```
