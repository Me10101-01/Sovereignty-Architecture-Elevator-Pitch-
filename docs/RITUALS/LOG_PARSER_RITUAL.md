# Log Parser Ritual

A standardized workflow for parsing and analyzing logs within the Black Ops Lab.

---

## Purpose

Ensure consistent, reproducible log analysis across experiments and agents.

---

## Input Preparation

### 1. Acquire Raw Logs

```bash
# GKE audit logs example
gcloud logging read 'resource.type="k8s_cluster"' \
  --project=your-project \
  --format=json \
  > logs/raw_gke_audit/$(date +%Y%m%d)_audit.json
```

### 2. Validate Format

- Confirm JSON is well-formed
- Check for truncation or missing entries
- Note time range covered

### 3. Document Source

Create metadata file:

```yaml
# logs/raw_gke_audit/YYYY-MM-DD_metadata.yaml
source: gcloud logging
project: your-project-id
time_range:
  start: "2024-01-15T00:00:00Z"
  end: "2024-01-16T00:00:00Z"
filters_applied:
  - resource.type="k8s_cluster"
record_count: 45823
```

---

## Parsing Workflow

### 1. Initialize Parser

```bash
# Using the lab CLI
cargo run --bin swarm_lab_cli -- parse \
  --input logs/raw_gke_audit/20240115_audit.json \
  --parser gke_audit \
  --output logs/derived/
```

### 2. Common Parsers

| Parser | Input | Output |
|--------|-------|--------|
| `gke_audit` | GKE audit JSON | Structured events |
| `lease_activity` | Audit events | Lease lifecycle data |
| `autoscaler` | Node pool logs | Scaling decisions |

### 3. Verify Output

- Check record counts match expectations
- Spot-check random entries for accuracy
- Validate schema compliance

---

## Analysis Patterns

### Lease Churn Detection

```rust
// Identify rapid lease creates/deletes
pub fn detect_churn(events: &[LeaseEvent], window_secs: u64) -> Vec<ChurnAnomaly> {
    // Group by namespace/lease name
    // Calculate create/delete frequency
    // Flag anomalies exceeding threshold
}
```

### Autoscaler Noise

```rust
// Find thrashing scale-up/down cycles
pub fn detect_thrashing(events: &[ScaleEvent]) -> Vec<ThrashingPeriod> {
    // Identify rapid oscillations
    // Calculate stability score
}
```

---

## Output Standards

### Derived Data Format

All parsed data goes to `logs/derived/` in standardized formats:

```text
logs/derived/
├─ YYYYMMDD_lease_activity.csv
├─ YYYYMMDD_anomaly_reports.json
├─ YYYYMMDD_scale_events.parquet
└─ YYYYMMDD_summary.md
```

### CSV Schema

```csv
timestamp,namespace,lease_name,action,holder,duration_ms,anomaly_flag
2024-01-15T10:30:00Z,kube-system,kube-controller-manager,acquire,node-1,0,false
```

### JSON Schema

```json
{
  "anomalies": [
    {
      "type": "lease_churn",
      "namespace": "kube-system",
      "lease": "kube-scheduler",
      "severity": "high",
      "details": "45 transitions in 60s window",
      "timestamp_range": ["2024-01-15T10:30:00Z", "2024-01-15T10:31:00Z"]
    }
  ]
}
```

---

## SWARM-HS Integration

When parsing logs as part of a SWARM-HS handshake:

1. **SYN**: Attach raw logs + parsing intent
2. **SYN-ACK**: Agent proposes parser config/approach
3. **ACK**: Human approves, agent generates code
4. **FIN**: Output reviewed, findings documented

---

## Troubleshooting

### Parser Failures

- Check JSON validity with `jq .`
- Verify expected fields exist
- Look for encoding issues (UTF-8)

### Missing Data

- Confirm time range covers expected period
- Check for log sampling or rate limiting
- Verify IAM permissions for log access

### Performance Issues

- Stream large files instead of loading fully
- Use parallel processing for independent records
- Consider sampling for initial analysis
