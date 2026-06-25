use anyhow::Result;
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

use crate::config::ScanConfig;

#[derive(Debug, Clone)]
pub struct ScanEntry {
    pub path:      PathBuf,
    pub file_name: String,
    pub size:      u64,
    pub mime_type: String,
}

pub fn scan_directories(cfg: &ScanConfig) -> Result<Vec<ScanEntry>> {
    let mut entries = Vec::new();

    for dir in &cfg.scan_dirs {
        let root = Path::new(dir);
        if !root.exists() {
            tracing::warn!("scan_dir does not exist: {}", dir);
            continue;
        }

        for entry in WalkDir::new(root)
            .follow_links(false)
            .into_iter()
            .filter_map(|e| e.ok())
        {
            let path = entry.path().to_path_buf();
            if !path.is_file() {
                continue;
            }

            // Apply exclude patterns
            let path_str = path.to_string_lossy();
            if cfg.exclude_patterns.iter().any(|p| path_matches_pattern(&path_str, p)) {
                continue;
            }

            // Apply include extensions filter
            if !cfg.include_extensions.is_empty() {
                let ext = path.extension()
                    .and_then(|e| e.to_str())
                    .unwrap_or("");
                if !cfg.include_extensions.iter().any(|ie| ie.trim_start_matches('.') == ext) {
                    continue;
                }
            }

            let size = path.metadata().map(|m| m.len()).unwrap_or(0);

            // Apply max file size filter
            if cfg.max_file_size_bytes > 0 && size > cfg.max_file_size_bytes {
                tracing::debug!("Skipping oversized file: {} ({} bytes)", path.display(), size);
                continue;
            }

            let file_name = path.file_name()
                .and_then(|n| n.to_str())
                .unwrap_or("unknown")
                .to_string();

            let mime_type = crate::drive_client::guess_mime_type(&path).to_string();

            entries.push(ScanEntry { path, file_name, size, mime_type });
        }
    }

    entries.sort_by(|a, b| a.path.cmp(&b.path));
    Ok(entries)
}

fn path_matches_pattern(path: &str, pattern: &str) -> bool {
    // Simple glob: if pattern starts with * match suffix, else check component
    if pattern.starts_with('*') {
        let suffix = pattern.trim_start_matches('*');
        path.ends_with(suffix)
    } else {
        // Match if any path component equals the pattern
        path.split('/').any(|c| c == pattern) || path.split('\\').any(|c| c == pattern)
    }
}
