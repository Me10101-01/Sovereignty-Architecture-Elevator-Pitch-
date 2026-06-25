/// Placeholder system — tracks files that are pending upload.
///
/// When a file is discovered but upload is deferred or failed, a
/// `.sagco_placeholder` JSONL entry is written. hydrate.rs resolves
/// placeholders when the file becomes uploadable.

use anyhow::Result;
use chrono::Utc;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

#[derive(Debug, Deserialize, Serialize, Clone, PartialEq)]
pub enum PlaceholderStatus {
    Pending,
    Uploading,
    Uploaded,
    Failed,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct PlaceholderEntry {
    pub ts:          String,
    pub local_path:  String,
    pub file_name:   String,
    pub sha256:      String,
    pub status:      PlaceholderStatus,
    pub drive_id:    Option<String>,
    pub error:       Option<String>,
    pub size:        u64,
}

impl PlaceholderEntry {
    pub fn new(local_path: &str, file_name: &str, sha256: &str, size: u64) -> Self {
        Self {
            ts:         Utc::now().to_rfc3339(),
            local_path: local_path.to_string(),
            file_name:  file_name.to_string(),
            sha256:     sha256.to_string(),
            status:     PlaceholderStatus::Pending,
            drive_id:   None,
            error:      None,
            size,
        }
    }
}

pub struct PlaceholderStore {
    path: PathBuf,
}

impl PlaceholderStore {
    pub fn new(placeholder_dir: &str) -> Result<Self> {
        let dir = PathBuf::from(placeholder_dir);
        std::fs::create_dir_all(&dir)?;
        Ok(Self { path: dir.join("placeholders.jsonl") })
    }

    pub fn append(&self, entry: &PlaceholderEntry) -> Result<()> {
        use std::io::Write;
        let mut f = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.path)?;
        writeln!(f, "{}", serde_json::to_string(entry)?)?;
        Ok(())
    }

    pub fn load_all(&self) -> Result<Vec<PlaceholderEntry>> {
        if !self.path.exists() {
            return Ok(vec![]);
        }
        let content = std::fs::read_to_string(&self.path)?;
        let entries = content
            .lines()
            .filter(|l| !l.trim().is_empty())
            .filter_map(|l| serde_json::from_str::<PlaceholderEntry>(l).ok())
            .collect();
        Ok(entries)
    }

    pub fn pending(&self) -> Result<Vec<PlaceholderEntry>> {
        Ok(self
            .load_all()?
            .into_iter()
            .filter(|e| e.status == PlaceholderStatus::Pending)
            .collect())
    }

    /// Rewrite the entire JSONL file with updated entries.
    pub fn update_status(&self, sha256: &str, status: PlaceholderStatus, drive_id: Option<String>, error: Option<String>) -> Result<()> {
        use std::io::Write;
        let mut entries = self.load_all()?;
        for e in &mut entries {
            if e.sha256 == sha256 {
                e.status   = status.clone();
                e.drive_id = drive_id.clone();
                e.error    = error.clone();
            }
        }
        let mut f = std::fs::File::create(&self.path)?;
        for e in &entries {
            writeln!(f, "{}", serde_json::to_string(e)?)?;
        }
        Ok(())
    }
}
