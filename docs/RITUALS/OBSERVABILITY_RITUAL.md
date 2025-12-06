# Observability Ritual

A standardized workflow for capturing and analyzing system telemetry in the Black Ops Lab.

---

## Purpose

Ensure every experiment produces complete, usable telemetry that enables learning and iteration.

---

## The Three Pillars

### 1. Logs

**What**: Discrete events with structured context

**Where**: 
- Raw: `logs/raw_gke_audit/`
- Derived: `logs/derived/`

**Standard Fields**:
```json
{
  "timestamp": "ISO-8601",
  "level": "DEBUG|INFO|WARN|ERROR",
  "component": "parser|analyzer|cli",
  "experiment_id": "YYYY-MM-DD_name",
  "trace_id": "uuid-v4",
  "message": "Human-readable description",
  "context": {}
}
```

### 2. Metrics

**What**: Numerical measurements over time

**Where**: Prometheus/Grafana stack (if deployed)

**Standard Metrics**:
```text
swarm_lab_experiments_total{status="success|failure"}
swarm_lab_parse_duration_seconds
swarm_lab_anomalies_detected{type="lease_churn|thrashing"}
swarm_lab_handshakes_total{phase="syn|synack|ack|fin"}
```

### 3. Traces

**What**: Distributed operations across components

**Where**: OpenTelemetry collector (if deployed)

**Span Convention**:
```text
swarm_lab.experiment
├─ swarm_lab.parse
│  └─ swarm_lab.parse.file
├─ swarm_lab.analyze
│  └─ swarm_lab.analyze.detect_anomaly
└─ swarm_lab.report
```

---

## Pre-Experiment Setup

### 1. Verify Collection

```bash
# Check log collection is working
kubectl logs -n black-ops -l app=lab-agent --tail=10

# Verify metrics endpoint
curl http://localhost:9090/api/v1/targets

# Confirm trace export
curl http://localhost:4317/health
```

### 2. Establish Baseline

Before making changes:
- Capture 15 minutes of steady-state telemetry
- Document "normal" metric ranges
- Save log sample for comparison

### 3. Tag Experiment

Add experiment ID to all telemetry:
```bash
export EXPERIMENT_ID="2024-01-15_lease-analysis"
```

---

## During Experiment

### Real-Time Monitoring

```bash
# Stream logs with filtering
kubectl logs -f -n black-ops deploy/lab-agent | grep $EXPERIMENT_ID

# Watch key metrics
watch -n 5 'curl -s localhost:9090/api/v1/query?query=swarm_lab_experiments_total'
```

### Checkpoint Captures

At each phase transition:
1. Save log snapshot
2. Record metric values
3. Export trace spans

---

## Post-Experiment Collection

### 1. Gather All Telemetry

```bash
# Export logs
kubectl logs -n black-ops deploy/lab-agent \
  --since-time="$START_TIME" \
  > logs/raw_gke_audit/${EXPERIMENT_ID}_agent.log

# Export metrics
curl "http://localhost:9090/api/v1/query_range?query=swarm_lab_parse_duration_seconds&start=$START&end=$END" \
  > logs/derived/${EXPERIMENT_ID}_metrics.json

# Export traces
# (varies by backend)
```

### 2. Correlate Events

Create timeline of events:

```markdown
## Timeline: 2024-01-15_lease-analysis

| Time | Event | Telemetry |
|------|-------|-----------|
| 10:30:00 | SYN phase start | log: experiment_start |
| 10:30:15 | Parser invoked | metric: parse_start |
| 10:31:45 | Anomaly detected | log: anomaly_found, metric: anomalies_detected +1 |
| 10:32:00 | FIN phase complete | log: experiment_complete |
```

### 3. Archive

```bash
# Compress and archive
tar -czf archive/${EXPERIMENT_ID}.tar.gz \
  logs/raw_gke_audit/${EXPERIMENT_ID}* \
  logs/derived/${EXPERIMENT_ID}* \
  docs/experiments/${EXPERIMENT_ID}/
```

---

## Observability Checklist

Use this checklist for every experiment:

- [ ] Logging configured with experiment ID
- [ ] Baseline metrics captured
- [ ] Trace context propagating
- [ ] Real-time dashboards accessible
- [ ] Alert thresholds set (if needed)
- [ ] Post-experiment data exported
- [ ] Findings documented with telemetry references

---

## Dashboards

### Recommended Grafana Panels

1. **Experiment Overview**
   - Handshake phase progression
   - Success/failure counts
   - Duration distribution

2. **Parser Performance**
   - Parse rate (records/sec)
   - Error rate
   - Memory usage

3. **Anomaly Detection**
   - Anomalies by type
   - False positive rate
   - Detection latency

---

## Alert Rules

```yaml
# Example Prometheus alerting rules
groups:
  - name: black-ops-lab
    rules:
      - alert: ExperimentStalled
        expr: rate(swarm_lab_handshakes_total[5m]) == 0
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "No SWARM-HS activity in 10 minutes"
      
      - alert: HighAnomalyRate
        expr: rate(swarm_lab_anomalies_detected[5m]) > 10
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Unusual number of anomalies detected"
```
