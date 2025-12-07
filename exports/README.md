# Data Export Samples

This directory contains sample data exports demonstrating compliance with **Principal 1: DATA PORTABILITY** of the Zero Vendor Lock-in Principals (ZVLI-2025-001).

## Purpose

All StrategicKhaos systems must support data export to universal, open formats. This directory provides:
1. Sample export files in multiple formats
2. Export script examples
3. Import validation procedures
4. Format conversion utilities

## Export Formats

### Supported Formats
- **JSON** - Structured data, API responses, configurations
- **CSV** - Tabular data, reports, user lists
- **YAML** - Configuration files, infrastructure definitions
- **Markdown** - Documentation, knowledge base
- **XML** - Legacy system compatibility

### Prohibited Formats
- ❌ Proprietary binary formats
- ❌ Vendor-specific schemas without open documentation
- ❌ Encrypted formats without open decryption keys

## Sample Exports

### 1. User Database Export (CSV)
```csv
user_id,email,created_at,last_login,role,status
001,user@example.com,2025-01-15T10:00:00Z,2025-12-07T08:30:00Z,member,active
002,admin@example.com,2025-01-15T10:05:00Z,2025-12-07T09:15:00Z,admin,active
```

### 2. System Configuration (JSON)
```json
{
  "export_metadata": {
    "timestamp": "2025-12-07T20:00:00Z",
    "system": "strategickhaos-core",
    "version": "2.1.0",
    "format": "json",
    "schema_version": "1.0"
  },
  "configurations": [
    {
      "service": "identity",
      "provider": "keycloak",
      "endpoint": "https://auth.strategickhaos.internal",
      "failover": ["google_oauth", "local_auth"]
    },
    {
      "service": "llm",
      "provider": "ollama",
      "models": ["qwen2.5:72b", "claude", "gpt"],
      "failover_order": ["ollama", "claude", "gpt"]
    }
  ]
}
```

### 3. Infrastructure State (YAML)
```yaml
export_metadata:
  timestamp: 2025-12-07T20:00:00Z
  system: infrastructure
  format: yaml
  
infrastructure:
  compute:
    - name: athena
      type: physical
      role: kubernetes_node
      status: operational
    - name: lyra
      type: physical
      role: kubernetes_node
      status: operational
      
  cloud:
    - provider: gcp
      region: us-central1
      cluster: jarvis-swarm-personal-001
      nodes: 3
      fallback: local_kubernetes
```

### 4. Knowledge Base (Markdown)
See `exports/sample_exports/knowledge_base_export.md`

## Export Scripts

### Daily Automated Exports
```bash
#!/bin/bash
# Location: /scripts/daily_export.sh
# Runs daily via cron

EXPORT_DATE=$(date +%Y-%m-%d)
EXPORT_DIR="/backups/exports/${EXPORT_DATE}"

mkdir -p "${EXPORT_DIR}"

# Export user database
pg_dump strategickhaos_users --format=csv > "${EXPORT_DIR}/users.csv"
pg_dump strategickhaos_users --format=json > "${EXPORT_DIR}/users.json"

# Export configurations
kubectl get configmaps -A -o yaml > "${EXPORT_DIR}/k8s_configs.yaml"
cp -r /etc/strategickhaos/*.yaml "${EXPORT_DIR}/"

# Export documentation
tar -czf "${EXPORT_DIR}/docs.tar.gz" /docs/

# Verify integrity
sha256sum "${EXPORT_DIR}"/* > "${EXPORT_DIR}/checksums.txt"

# Upload to multiple locations
aws s3 sync "${EXPORT_DIR}" s3://strategickhaos-backups/exports/${EXPORT_DATE}/
rsync -av "${EXPORT_DIR}" backup-server:/backups/
```

### On-Demand Export (< 24 hour guarantee)
```bash
#!/bin/bash
# Location: /scripts/emergency_export.sh
# Executes complete data export

export_all_data() {
  echo "Starting emergency export..."
  
  # User data
  ./scripts/export_users.sh
  
  # Application data
  ./scripts/export_app_data.sh
  
  # Infrastructure state
  ./scripts/export_infra.sh
  
  # Code repositories
  ./scripts/export_git_bundles.sh
  
  # Documentation
  ./scripts/export_docs.sh
  
  echo "Export complete. Estimated time: 4-6 hours"
}

export_all_data
```

## Import Validation

### Testing Import to Alternative Platform
```bash
#!/bin/bash
# Verify exported data can be imported to alternative systems

# Test 1: Import to PostgreSQL
psql new_database < exports/users.sql

# Test 2: Import to MongoDB
mongoimport --db strategickhaos --collection users --file exports/users.json

# Test 3: Validate JSON schema
python3 scripts/validate_export_schema.py exports/config.json

# Test 4: Checksum verification
sha256sum -c exports/checksums.txt
```

## Compliance Verification

### Attorney Verification Checklist
- [x] Data export completes in < 24 hours
- [x] All exports in open, documented formats
- [x] No proprietary encoding or encryption
- [x] Export scripts tested quarterly
- [x] Import validation successful
- [x] Multiple export locations maintained

### Export Completeness Test
```bash
# Verify all system data included in exports
./scripts/verify_export_completeness.sh

# Expected output:
# ✅ User database: 100% exported
# ✅ Application data: 100% exported  
# ✅ Configuration: 100% exported
# ✅ Code repositories: 100% exported
# ✅ Documentation: 100% exported
# ✅ Infrastructure state: 100% exported
```

## Sample Files in This Directory

```
exports/
├── README.md (this file)
└── sample_exports/
    ├── users_sample.csv
    ├── config_sample.json
    ├── infrastructure_sample.yaml
    ├── knowledge_base_sample.md
    ├── export_metadata.json
    └── checksums.txt
```

## Export Retention Policy

| Export Type | Retention Period | Storage Locations |
|-------------|------------------|-------------------|
| Daily | 30 days | Local, S3, Backup server |
| Weekly | 90 days | Local, S3, Backup server |
| Monthly | 1 year | S3, Backup server, Glacier |
| Annual | 7 years | Glacier, Encrypted offline |

## Emergency Export Procedures

### Scenario: Vendor Data Hostage
1. Initiate emergency export immediately
2. Verify export completeness (checksum validation)
3. Import to alternative platform for testing
4. Document any data gaps or issues
5. Activate self-hosted alternatives
6. Communicate status to stakeholders

### Maximum Export Time: 6 hours
(Well under 24-hour guarantee)

## Format Conversion Utilities

### CSV to JSON
```bash
python3 scripts/csv_to_json.py input.csv output.json
```

### YAML to JSON
```bash
python3 scripts/yaml_to_json.py input.yaml output.json
```

### JSON to Database
```bash
python3 scripts/json_to_db.py input.json --db postgresql
```

## Contact

- **Data Export Issues:** data@strategickhaos.ai
- **Emergency Export:** See `escape_routes.yaml` protocols
- **Format Questions:** documentation@strategickhaos.ai

---

*Your data, your formats, your freedom.*
