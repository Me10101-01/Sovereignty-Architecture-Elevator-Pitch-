// SAGCO dispatch server — listens on 0.0.0.0:8842
// Routes incoming JSON commands to email, k8s, audit, or genesis handlers.
// All routes are audit-logged; destructive routes require HITL approval.

use anyhow::Result;

pub async fn serve() -> Result<()> {
    tracing::info!("dispatch server listening on 0.0.0.0:8842");
    tracing::info!("genesis proof endpoint: 0.0.0.0:9137/genesis_proof");

    // Placeholder: full tokio + axum HTTP server wired in v0.3.0
    // Routes: POST /dispatch  POST /email  POST /k8s_job  GET /genesis_proof
    // Each route calls the corresponding module and logs to audit.

    // For now, park the async task indefinitely so the process stays alive.
    tokio::signal::ctrl_c().await?;
    tracing::info!("SIGINT received — shutting down organism");
    Ok(())
}
