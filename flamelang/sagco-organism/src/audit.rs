// SAGCO audit log — genesis-signed append-only event stream
// Every organism action is written here before execution.

use anyhow::Result;

pub struct AuditEntry {
    pub component: String,
    pub event:     String,
    pub data:      String,
}

pub fn log(entry: AuditEntry) -> Result<()> {
    // v0.3.0: append to /var/lib/sagco/audit.jsonl with genesis-chain hash
    tracing::info!(
        "[AUDIT] component={} event={} data={}",
        entry.component, entry.event, entry.data
    );
    Ok(())
}
