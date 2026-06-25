/// hydrate.rs — Resolve pending placeholders
///
/// For every PlaceholderStatus::Pending entry in the store:
///   1. Check if the local file still exists and SHA-256 matches
///   2. If yes → attempt upload via DriveClient
///   3. On success → mark Uploaded, record drive_id
///   4. On failure → mark Failed, record error
///
/// This is the "fill in the gaps" pass — run it after connectivity is restored
/// or after files that were deferred become available.

use anyhow::Result;

use crate::{
    drive_client::DriveClient,
    hasher::sha256_file,
    placeholder::{PlaceholderStatus, PlaceholderStore},
};

pub struct HydrateResult {
    pub resolved: usize,
    pub failed:   usize,
    pub skipped:  usize,
}

pub async fn hydrate(
    store:     &PlaceholderStore,
    client:    &DriveClient,
    folder_id: &str,
) -> Result<HydrateResult> {
    let pending = store.pending()?;
    let total = pending.len();

    if total == 0 {
        tracing::info!("No pending placeholders to hydrate.");
        return Ok(HydrateResult { resolved: 0, failed: 0, skipped: 0 });
    }

    tracing::info!("Hydrating {} pending placeholder(s)…", total);

    let mut resolved = 0usize;
    let mut failed   = 0usize;
    let mut skipped  = 0usize;

    for entry in &pending {
        let path = std::path::Path::new(&entry.local_path);

        if !path.exists() {
            tracing::warn!("Placeholder file missing: {} — skipping", entry.local_path);
            skipped += 1;
            continue;
        }

        // Verify SHA-256 hasn't changed
        let current_hash = match sha256_file(path) {
            Ok(h) => h,
            Err(e) => {
                tracing::error!("Hash error for {}: {}", entry.local_path, e);
                store.update_status(
                    &entry.sha256,
                    PlaceholderStatus::Failed,
                    None,
                    Some(format!("Hash error: {}", e)),
                )?;
                failed += 1;
                continue;
            }
        };

        if current_hash != entry.sha256 {
            tracing::warn!(
                "SHA-256 mismatch for {} — file changed since placeholder was created. Skipping.",
                entry.local_path
            );
            store.update_status(
                &entry.sha256,
                PlaceholderStatus::Failed,
                None,
                Some(format!("SHA-256 mismatch: stored={} current={}", entry.sha256, current_hash)),
            )?;
            failed += 1;
            continue;
        }

        // Attempt upload
        store.update_status(&entry.sha256, PlaceholderStatus::Uploading, None, None)?;

        let mime = crate::drive_client::guess_mime_type(path);
        match client.upload_file(path, &entry.file_name, folder_id, mime).await {
            Ok(drive_file) => {
                tracing::info!("  ✓ {} → Drive ID {}", entry.file_name, drive_file.id);
                store.update_status(
                    &entry.sha256,
                    PlaceholderStatus::Uploaded,
                    Some(drive_file.id),
                    None,
                )?;
                resolved += 1;
            }
            Err(e) => {
                tracing::error!("  ✗ {} failed: {}", entry.file_name, e);
                store.update_status(
                    &entry.sha256,
                    PlaceholderStatus::Failed,
                    None,
                    Some(e.to_string()),
                )?;
                failed += 1;
            }
        }
    }

    Ok(HydrateResult { resolved, failed, skipped })
}
