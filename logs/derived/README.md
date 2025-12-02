# Derived Data

This directory contains processed and analyzed data from the Black Ops Lab.

## File Types

### CSV Files
- `*_lease_activity.csv` - Parsed lease events
- `*_scale_events.csv` - Autoscaler activity

### JSON Files
- `*_anomaly_reports.json` - Detected anomalies
- `*_summary.json` - Analysis summaries

## Schema Examples

### lease_activity.csv
```csv
timestamp,namespace,lease_name,action,holder,duration_ms,anomaly_flag
2024-01-15T10:30:00Z,kube-system,kube-controller-manager,acquire,node-1,0,false
```

### anomaly_reports.json
```json
{
  "experiment_id": "2024-01-15_lease-analysis",
  "generated": "2024-01-15T12:00:00Z",
  "anomalies": [
    {
      "type": "lease_churn",
      "namespace": "kube-system",
      "lease": "kube-scheduler",
      "severity": "high",
      "details": "45 transitions in 60s window"
    }
  ]
}
```

## Notes

- Derived data may be committed if it contains no sensitive information
- Large files should be compressed or stored externally
- Reference experiment IDs for traceability
