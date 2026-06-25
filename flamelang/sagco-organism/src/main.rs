// SAGCO-Organism — Sovereign Autonomous General Compute Organism
// Entry point: initialise genesis lock, start dispatch server.
//
// HITL security rule: no autonomous commits, no self-modifying code.
// Every destructive action requires human approval via the HITL daemon.
// "artifact → watch → notify → approve" — never execute without confirmation.

mod audit;
mod dispatch;
mod email;
mod k8s;

#[path = "../../../genesis_prime_core.rs"]
mod genesis;

use tracing_subscriber::EnvFilter;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env())
        .init();

    tracing::info!("🔥 SAGCO-Organism v0.2.0 starting");
    tracing::info!("genesis increment=3449 origin=2023-01-27T21:00:49Z");

    let prime = genesis::StrategickhaosPrime::initialize();
    let proof = prime.genesis_proof();
    tracing::info!("genesis_proof={}", proof);

    dispatch::serve().await?;
    Ok(())
}
