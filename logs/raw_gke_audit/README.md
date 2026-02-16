# Raw GKE Audit Logs

This directory contains raw audit logs captured from GKE clusters.

## File Naming Convention

```
YYYYMMDD_audit.json       - Daily audit log exports
YYYYMMDD_metadata.yaml    - Metadata about the log capture
```

## How to Add Logs

1. Export from GCP:
```bash
gcloud logging read 'resource.type="k8s_cluster"' \
  --project=your-project \
  --format=json \
  > $(date +%Y%m%d)_audit.json
```

2. Create metadata file with source details

3. Run parser:
```bash
swarm_lab_cli parse --input YYYYMMDD_audit.json --parser gke_audit
```

## Contents

Logs should NOT be committed to git. Add log files to `.gitignore`.
