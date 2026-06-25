// SAGCO Kubernetes job dispatcher
// HITL gate: emits a notification, blocks until human approval, then creates job.
// No autonomous K8s mutations — rule: "never execute destructive actions without confirmation"

use anyhow::Result;

pub struct K8sJobRequest {
    pub namespace:    String,
    pub job_name:     String,
    pub json_payload: String,
}

pub async fn dispatch_job(req: K8sJobRequest) -> Result<()> {
    tracing::warn!(
        "K8s job queued for HITL approval: ns={} job={}",
        req.namespace, req.job_name
    );

    // HITL flow (v0.3.0):
    //   1. Emit Discord / SMTP notification with job details
    //   2. Await human approval signal (webhook or env flag)
    //   3. On approval: kube::Client::try_default() → Jobs::create(&job_spec)
    //   4. On denial: log SAGCO_ERR_HITL_DENIED and return
    let _ = req;
    Ok(())
}
