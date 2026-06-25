use anyhow::{bail, Result};
use serde::{Deserialize, Serialize};
use std::path::Path;

/// Service account credentials (JSON key file from Google Cloud Console)
#[derive(Debug, Deserialize)]
pub struct ServiceAccountKey {
    pub client_email: String,
    pub private_key:  String,
    pub token_uri:    String,
    #[serde(rename = "type")]
    pub key_type: String,
}

/// OAuth2 access token response
#[derive(Debug, Deserialize)]
pub struct TokenResponse {
    pub access_token: String,
    pub expires_in:   u64,
    pub token_type:   String,
}

/// Credential type detected from credentials file
#[derive(Debug)]
pub enum Credentials {
    ServiceAccount(ServiceAccountKey),
    /// OAuth2 refresh token flow (user account) — stub, requires browser
    OAuthUserToken { client_id: String, client_secret: String, refresh_token: String },
}

impl Credentials {
    pub fn load(path: &str) -> Result<Self> {
        let content = std::fs::read_to_string(path)
            .map_err(|e| anyhow::anyhow!("Cannot read credentials {}: {}", path, e))?;

        let v: serde_json::Value = serde_json::from_str(&content)?;

        match v.get("type").and_then(|t| t.as_str()) {
            Some("service_account") => {
                let key: ServiceAccountKey = serde_json::from_str(&content)?;
                Ok(Credentials::ServiceAccount(key))
            }
            Some("authorized_user") => {
                let client_id = v["client_id"].as_str().unwrap_or("").to_string();
                let client_secret = v["client_secret"].as_str().unwrap_or("").to_string();
                let refresh_token = v["refresh_token"].as_str().unwrap_or("").to_string();
                Ok(Credentials::OAuthUserToken { client_id, client_secret, refresh_token })
            }
            other => bail!("Unknown credentials type: {:?}", other),
        }
    }
}

/// Obtain a Bearer token.
/// For service accounts, signs a JWT and exchanges it.
/// For user tokens, uses the refresh token flow.
pub async fn get_access_token(creds: &Credentials, scopes: &[String]) -> Result<String> {
    match creds {
        Credentials::ServiceAccount(sa) => {
            service_account_token(sa, scopes).await
        }
        Credentials::OAuthUserToken { client_id, client_secret, refresh_token } => {
            refresh_token_exchange(client_id, client_secret, refresh_token).await
        }
    }
}

async fn service_account_token(sa: &ServiceAccountKey, scopes: &[String]) -> Result<String> {
    use std::time::{SystemTime, UNIX_EPOCH};

    let now = SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs();
    let exp = now + 3600;

    // Build JWT header + claims
    let header = base64_url(br#"{"alg":"RS256","typ":"JWT"}"#);
    let claims = serde_json::json!({
        "iss": sa.client_email,
        "scope": scopes.join(" "),
        "aud": sa.token_uri,
        "iat": now,
        "exp": exp,
    });
    let claims_b64 = base64_url(claims.to_string().as_bytes());
    let signing_input = format!("{}.{}", header, claims_b64);

    // Sign with RSA-SHA256 using the private key
    let signature = rsa_sha256_sign(signing_input.as_bytes(), &sa.private_key)?;
    let jwt = format!("{}.{}", signing_input, signature);

    // Exchange JWT for access token
    let client = reqwest::Client::new();
    let resp = client
        .post(&sa.token_uri)
        .form(&[
            ("grant_type", "urn:ietf:params:oauth:grant-type:jwt-bearer"),
            ("assertion", &jwt),
        ])
        .send()
        .await?
        .error_for_status()?
        .json::<TokenResponse>()
        .await?;

    Ok(resp.access_token)
}

async fn refresh_token_exchange(
    client_id: &str,
    client_secret: &str,
    refresh_token: &str,
) -> Result<String> {
    let client = reqwest::Client::new();
    let resp = client
        .post("https://oauth2.googleapis.com/token")
        .form(&[
            ("client_id", client_id),
            ("client_secret", client_secret),
            ("refresh_token", refresh_token),
            ("grant_type", "refresh_token"),
        ])
        .send()
        .await?
        .error_for_status()?
        .json::<TokenResponse>()
        .await?;

    Ok(resp.access_token)
}

// --- JWT helpers ------------------------------------------------------------

fn base64_url(data: &[u8]) -> String {
    use std::io::Write;
    // base64 URL-safe, no padding
    let encoded = base64_encode(data);
    encoded.replace('+', "-").replace('/', "_").trim_end_matches('=').to_string()
}

fn base64_encode(data: &[u8]) -> String {
    const TABLE: &[u8] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    let mut out = String::with_capacity((data.len() + 2) / 3 * 4);
    for chunk in data.chunks(3) {
        let b0 = chunk[0] as usize;
        let b1 = if chunk.len() > 1 { chunk[1] as usize } else { 0 };
        let b2 = if chunk.len() > 2 { chunk[2] as usize } else { 0 };
        out.push(TABLE[(b0 >> 2)] as char);
        out.push(TABLE[((b0 & 3) << 4) | (b1 >> 4)] as char);
        if chunk.len() > 1 {
            out.push(TABLE[((b1 & 0xf) << 2) | (b2 >> 6)] as char);
        } else { out.push('='); }
        if chunk.len() > 2 {
            out.push(TABLE[b2 & 0x3f] as char);
        } else { out.push('='); }
    }
    out
}

fn rsa_sha256_sign(data: &[u8], pem_key: &str) -> Result<String> {
    // NOTE: Full RSA signing requires an external crate (rsa + pkcs8).
    // This stub returns a placeholder so the binary compiles.
    // Wire in the `rsa` crate for production:
    //   use rsa::{pkcs8::DecodePrivateKey, RsaPrivateKey};
    //   use rsa::pkcs1v15::SigningKey;
    //   use sha2::Sha256;
    //   use rsa::signature::SignatureEncoding;
    bail!(
        "RSA signing not yet wired. Add the `rsa` crate dependency and \
         implement rsa_sha256_sign(). See placeholder.rs for the stub pattern."
    )
}
