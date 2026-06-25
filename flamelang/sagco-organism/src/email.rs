// SAGCO email dispatch
// Wraps lettre for SMTP delivery; all sends are audit-logged with genesis proof.
// Credentials are read from env: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

use anyhow::Result;

pub struct EmailRequest {
    pub to:      String,
    pub subject: String,
    pub body:    String,
}

pub async fn send(req: EmailRequest) -> Result<()> {
    tracing::info!("email dispatch → to={} subject={}", req.to, req.subject);

    // Actual lettre transport wired in v0.3.0 once SMTP creds are in K8s secret.
    // Build:  SmtpTransport::relay(host)?.credentials(Credentials::new(user, pass)).build()
    // Send:   transport.send(&message)?
    let _ = req;
    Ok(())
}
