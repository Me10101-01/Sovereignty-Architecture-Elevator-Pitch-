use anyhow::{bail, Result};
use reqwest::{multipart, Client};
use serde::{Deserialize, Serialize};
use std::path::Path;

const DRIVE_API: &str = "https://www.googleapis.com/drive/v3";
const UPLOAD_API: &str = "https://www.googleapis.com/upload/drive/v3/files";

/// Metadata returned by Drive on successful upload
#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct DriveFile {
    pub id:           String,
    pub name:         String,
    #[serde(rename = "mimeType")]
    pub mime_type:    String,
    pub size:         Option<String>,
    #[serde(rename = "webViewLink")]
    pub web_view_link: Option<String>,
}

pub struct DriveClient {
    http:         Client,
    access_token: String,
}

impl DriveClient {
    pub fn new(access_token: String) -> Self {
        Self {
            http: Client::new(),
            access_token,
        }
    }

    /// Upload a file to Google Drive (multipart upload).
    ///
    /// Returns the DriveFile metadata on success.
    pub async fn upload_file(
        &self,
        local_path: &Path,
        file_name:  &str,
        folder_id:  &str,
        mime_type:  &str,
    ) -> Result<DriveFile> {
        let file_bytes = tokio::fs::read(local_path).await
            .map_err(|e| anyhow::anyhow!("Cannot read {}: {}", local_path.display(), e))?;

        // Metadata part
        let metadata = serde_json::json!({
            "name": file_name,
            "parents": [folder_id],
        });
        let metadata_part = multipart::Part::text(metadata.to_string())
            .mime_str("application/json")?;

        // File content part
        let file_part = multipart::Part::bytes(file_bytes)
            .file_name(file_name.to_string())
            .mime_str(mime_type)?;

        let form = multipart::Form::new()
            .part("metadata", metadata_part)
            .part("file", file_part);

        let resp = self
            .http
            .post(format!("{}?uploadType=multipart", UPLOAD_API))
            .bearer_auth(&self.access_token)
            .multipart(form)
            .send()
            .await?;

        if !resp.status().is_success() {
            let status = resp.status();
            let body = resp.text().await.unwrap_or_default();
            bail!("Drive upload failed: {} — {}", status, body);
        }

        let drive_file: DriveFile = resp.json().await?;
        Ok(drive_file)
    }

    /// Check whether a file with the given name already exists in folder_id.
    pub async fn find_by_name(
        &self,
        file_name: &str,
        folder_id: &str,
    ) -> Result<Option<DriveFile>> {
        let q = format!(
            "name='{}' and '{}' in parents and trashed=false",
            file_name.replace('\'', "\\'"),
            folder_id
        );
        let resp = self
            .http
            .get(format!("{}/files", DRIVE_API))
            .bearer_auth(&self.access_token)
            .query(&[
                ("q", q.as_str()),
                ("fields", "files(id,name,mimeType,size,webViewLink)"),
                ("pageSize", "1"),
            ])
            .send()
            .await?
            .error_for_status()?
            .json::<serde_json::Value>()
            .await?;

        let files = resp["files"].as_array().cloned().unwrap_or_default();
        if files.is_empty() {
            return Ok(None);
        }
        let f: DriveFile = serde_json::from_value(files[0].clone())?;
        Ok(Some(f))
    }

    /// Delete a file by Drive ID.
    pub async fn delete_file(&self, file_id: &str) -> Result<()> {
        self.http
            .delete(format!("{}/files/{}", DRIVE_API, file_id))
            .bearer_auth(&self.access_token)
            .send()
            .await?
            .error_for_status()?;
        Ok(())
    }
}

pub fn guess_mime_type(path: &Path) -> &'static str {
    match path.extension().and_then(|e| e.to_str()).unwrap_or("") {
        "pdf"  => "application/pdf",
        "md"   => "text/markdown",
        "yaml" | "yml" => "application/yaml",
        "toml" => "application/toml",
        "json" => "application/json",
        "txt"  => "text/plain",
        "png"  => "image/png",
        "jpg" | "jpeg" => "image/jpeg",
        "rs"   => "text/x-rust",
        "py"   => "text/x-python",
        "c"    => "text/x-csrc",
        "sh"   => "text/x-sh",
        _      => "application/octet-stream",
    }
}
