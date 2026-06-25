use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

#[derive(Debug, Deserialize, Serialize)]
pub struct Config {
    pub auth: AuthConfig,
    pub drive: DriveConfig,
    pub scan: ScanConfig,
    pub logs: LogConfig,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct AuthConfig {
    /// Path to Google service account JSON or OAuth2 credentials JSON
    pub credentials_path: String,
    /// OAuth2 scopes
    #[serde(default = "default_scopes")]
    pub scopes: Vec<String>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct DriveConfig {
    /// Google Drive folder ID to upload into
    pub upload_folder_id: String,
    /// Whether to overwrite existing files with same name
    #[serde(default)]
    pub overwrite_existing: bool,
    /// MIME type override (None = auto-detect)
    pub mime_type: Option<String>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct ScanConfig {
    /// Local directories to scan for uploadable files
    pub scan_dirs: Vec<String>,
    /// File extensions to include (empty = all)
    #[serde(default)]
    pub include_extensions: Vec<String>,
    /// Patterns to exclude
    #[serde(default = "default_excludes")]
    pub exclude_patterns: Vec<String>,
    /// Max file size in bytes (0 = no limit)
    #[serde(default)]
    pub max_file_size_bytes: u64,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct LogConfig {
    pub upload_log: String,
    pub placeholder_dir: String,
    pub sha256_sums_file: String,
}

fn default_scopes() -> Vec<String> {
    vec!["https://www.googleapis.com/auth/drive.file".to_string()]
}

fn default_excludes() -> Vec<String> {
    vec![
        ".git".to_string(),
        "__pycache__".to_string(),
        "*.gpg".to_string(),
        "target".to_string(),
    ]
}

impl Config {
    pub fn load(path: &str) -> Result<Self> {
        let content = std::fs::read_to_string(path)
            .map_err(|e| anyhow::anyhow!("Cannot read config {}: {}", path, e))?;
        let config: Config = serde_yaml::from_str(&content)
            .map_err(|e| anyhow::anyhow!("Config parse error: {}", e))?;
        Ok(config)
    }

    pub fn default_path() -> PathBuf {
        dirs_next::home_dir()
            .unwrap_or_else(|| PathBuf::from("."))
            .join("SAGCO")
            .join("gdrive-config.yaml")
    }
}
