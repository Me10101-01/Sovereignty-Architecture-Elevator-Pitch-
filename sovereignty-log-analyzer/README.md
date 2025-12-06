# Sovereignty Log Analyzer

A Rust CLI tool for analyzing GKE (Google Kubernetes Engine) audit logs and computing sovereignty metrics.

## Overview

The Sovereignty Log Analyzer parses Kubernetes/GKE Cloud Audit Logs and provides:

- **Sovereignty metrics** calculation (automation ratio, decision latency, cost efficiency)
- **Multi-cluster analysis** support (e.g., `red-team`, `jarvis-swarm-personal-001`)
- **Anomaly detection** (flags user-initiated mutations in sensitive namespaces)
- **CLI dashboard** with real-time metrics visualization
- **Markdown report generation** for documentation and dashboards

## Installation

### Prerequisites

- Rust 1.70 or later
- Cargo (Rust's package manager)

### Build from Source

```bash
cd sovereignty-log-analyzer
cargo build --release
```

The binary will be available at `./target/release/sovereignty-log-analyzer`.

## Usage

### Analyze Logs

Analyze audit logs and display an activity summary:

```bash
# Analyze from file
./target/release/sovereignty-log-analyzer analyze --input path/to/audit_logs.json

# Filter by cluster
./target/release/sovereignty-log-analyzer analyze --input logs.json --cluster red-team

# Filter by namespace
./target/release/sovereignty-log-analyzer analyze --input logs.json --namespace kube-system

# Show only anomalies
./target/release/sovereignty-log-analyzer analyze --input logs.json --anomalies-only
```

### View Sovereignty Metrics Dashboard

Display a real-time sovereignty metrics dashboard:

```bash
# Display dashboard
./target/release/sovereignty-log-analyzer metrics --input path/to/audit_logs.json

# Output as JSON
./target/release/sovereignty-log-analyzer metrics --input logs.json --json
```

### Watch Live Logs

Watch logs in real-time from stdin:

```bash
# Pipe logs from another command
tail -f /var/log/audit.json | ./target/release/sovereignty-log-analyzer watch --input -

# With custom refresh interval (seconds)
cat logs.json | ./target/release/sovereignty-log-analyzer watch --input - --refresh 10
```

### Generate Reports

Generate a Markdown report suitable for Obsidian or other documentation:

```bash
./target/release/sovereignty-log-analyzer report --input logs.json --output report.md
```

## Metrics Explained

### Automation Ratio

The percentage of operations initiated by automated systems (service accounts, controllers) versus human operators.

- **High (>80%)**: Strong automation, reduced human error potential
- **Medium (50-80%)**: Moderate automation, room for improvement
- **Low (<50%)**: Heavy human intervention, consider automation

### Decision Latency

Estimated average time for operations to complete:

- **Automated operations**: ~60ms average
- **Human operations**: ~60,000ms (1 minute) average

### Cost Efficiency Score

A composite metric (0-100) based on:

- Automation ratio contribution
- Decision latency reduction
- Overall operational efficiency

### Speed Improvement

Displays the acceleration factor achieved through automation:

```
Speed Improvement: 1000x faster automated decisions
```

## Anomaly Detection

The analyzer flags the following as potential security concerns:

- **Sensitive Namespace Mutations**: User-initiated changes in `kube-system`, `kube-public`, `istio-system`
- **High Frequency Operations**: >100 operations per minute from a single principal
- **Authentication Failures**: 401/403 status codes
- **Critical Resource Deletions**: Deletions in sensitive namespaces
- **Unknown Principals**: Operations without identified actors

## Log Format

The analyzer supports GKE Cloud Audit Logs in JSON format. Both array format and newline-delimited JSON (NDJSON) are supported.

Example log entry:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "protoPayload": {
    "authenticationInfo": {
      "principalEmail": "system:serviceaccount:kube-system:controller"
    },
    "methodName": "io.k8s.core.v1.pods.update",
    "resourceName": "projects/my-project/zones/us-central1-a/clusters/my-cluster/namespaces/default/pods/my-pod"
  },
  "resource": {
    "labels": {
      "cluster_name": "my-cluster"
    }
  }
}
```

## Project Structure

```
sovereignty-log-analyzer/
├── Cargo.toml              # Rust crate configuration
├── README.md               # This file
└── src/
    ├── main.rs             # CLI entry point and commands
    ├── log_parser.rs       # GKE audit log JSON parser
    ├── analyzer.rs         # Filtering and anomaly detection
    └── sovereignty_metrics.rs  # Metrics computation and dashboard
```

## Development

### Run Tests

```bash
cargo test
```

### Run with Debug Output

```bash
RUST_LOG=debug cargo run -- metrics --input test-logs.json
```

### Format Code

```bash
cargo fmt
```

### Lint

```bash
cargo clippy
```

## Integration with Swarm Infrastructure

This tool is designed to integrate with the Strategickhaos Swarm infrastructure:

1. **GKE Audit Logs**: Export from Google Cloud Logging
2. **Pipeline**: Logs → Sovereignty Analyzer → Metrics Dashboard
3. **Git Integration**: Branch-based development with automated PR creation

## License

MIT License

## Contributing

Contributions are welcome! Please submit pull requests to the main repository.
