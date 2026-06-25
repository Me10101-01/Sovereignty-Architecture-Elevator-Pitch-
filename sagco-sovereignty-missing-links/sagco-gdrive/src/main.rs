mod auth;
mod config;
mod drive_client;
mod hasher;
mod hydrate;
mod placeholder;
mod scanner;

use anyhow::Result;
use chrono::Utc;
use clap::{Parser, Subcommand};
use serde_json::json;
use std::io::Write as IoWrite;
use std::path::Path;
use tracing::info;

use crate::{
    auth::{get_access_token, Credentials},
    config::Config,
    drive_client::{DriveClient, guess_mime_type},
    hasher::{sha256_bytes, sha256_file},
    hydrate::hydrate,
    placeholder::{PlaceholderEntry, PlaceholderStatus, PlaceholderStore},
    scanner::scan_directories,
};

#[derive(Parser)]
#[command(
    name    = "sagco-gdrive",
    version = "0.1.0",
    about   = "SAGCO Google Drive uploader — SHA-256 sealed file sync"
)]
struct Cli {
    #[arg(short, long, default_value = "")]
    config: String,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Scan local directories and upload files to Google Drive
    Upload {
        /// Only scan, do not actually upload (dry run)
        #[arg(long)]
        dry_run: bool,
    },
    /// Resolve pending placeholders (retry failed/deferred uploads)
    Hydrate,
    /// Show placeholder status
    Status,
    /// SHA-256 seal all uploaded files and write SHA256SUMS.txt
    Seal,
    /// Scan directories and report what would be uploaded
    Scan,
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::from_default_env()
                .add_directive("sagco_gdrive=info".parse()?)
        )
        .init();

    let cli = Cli::parse();

    let config_path = if cli.config.is_empty() {
        Config::default_path().to_string_lossy().to_string()
    } else {
        cli.config.clone()
    };

    let cfg = Config::load(&config_path)
        .map_err(|e| anyhow::anyhow!("Config error: {}\nCreate config at: {}", e, config_path))?;

    match cli.command {
        Commands::Scan => cmd_scan(&cfg),
        Commands::Upload { dry_run } => cmd_upload(&cfg, dry_run).await,
        Commands::Hydrate => cmd_hydrate(&cfg).await,
        Commands::Status => cmd_status(&cfg),
        Commands::Seal => cmd_seal(&cfg),
    }
}

// --- scan -------------------------------------------------------------------

fn cmd_scan(cfg: &Config) -> Result<()> {
    let entries = scan_directories(&cfg.scan)?;
    println!("\n  SAGCO GDRIVE SCAN");
    println!("  {:50}  {:>10}  {}", "Path", "Size", "MIME");
    println!("  {}", "-".repeat(80));
    for e in &entries {
        println!("  {:50}  {:>10}  {}", e.path.display(), e.size, e.mime_type);
    }
    println!("\n  Total: {} files", entries.len());
    Ok(())
}

// --- upload -----------------------------------------------------------------

async fn cmd_upload(cfg: &Config, dry_run: bool) -> Result<()> {
    let entries = scan_directories(&cfg.scan)?;
    let creds   = Credentials::load(&cfg.auth.credentials_path)?;
    let token   = get_access_token(&creds, &cfg.auth.scopes).await?;
    let client  = DriveClient::new(token);
    let store   = PlaceholderStore::new(&cfg.logs.placeholder_dir)?;

    std::fs::create_dir_all(
        Path::new(&cfg.logs.upload_log).parent().unwrap_or(Path::new("."))
    )?;
    let mut log_file = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&cfg.logs.upload_log)?;

    let mut uploaded = 0usize;
    let mut skipped  = 0usize;
    let mut failed   = 0usize;

    for entry in &entries {
        let hash = sha256_file(&entry.path)?;

        if dry_run {
            println!("  [DRY] {} sha256={}", entry.file_name, &hash[..8]);
            continue;
        }

        // Check if already uploaded (same SHA-256 in placeholder store)
        let existing = store.load_all()?;
        if existing.iter().any(|e| e.sha256 == hash && e.status == PlaceholderStatus::Uploaded) {
            info!("  SKIP (already uploaded): {}", entry.file_name);
            skipped += 1;
            continue;
        }

        // Check if file already exists by name in Drive (if overwrite disabled)
        if !cfg.drive.overwrite_existing {
            if let Some(_) = client.find_by_name(&entry.file_name, &cfg.drive.upload_folder_id).await? {
                info!("  SKIP (exists in Drive): {}", entry.file_name);
                skipped += 1;
                continue;
            }
        }

        let mime = cfg.drive.mime_type.as_deref()
            .unwrap_or_else(|| guess_mime_type(&entry.path));

        match client.upload_file(&entry.path, &entry.file_name, &cfg.drive.upload_folder_id, mime).await {
            Ok(drive_file) => {
                info!("  ✓ {} → Drive:{}", entry.file_name, drive_file.id);
                // Log receipt
                let receipt = json!({
                    "ts":        Utc::now().to_rfc3339(),
                    "file":      entry.path.to_string_lossy(),
                    "name":      entry.file_name,
                    "sha256":    hash,
                    "drive_id":  drive_file.id,
                    "verdict":   "COMPUTED",
                });
                writeln!(log_file, "{}", receipt)?;

                // Update placeholder store
                let ph = PlaceholderEntry::new(
                    &entry.path.to_string_lossy(),
                    &entry.file_name,
                    &hash,
                    entry.size,
                );
                store.append(&ph)?;
                store.update_status(&hash, PlaceholderStatus::Uploaded, Some(drive_file.id), None)?;
                uploaded += 1;
            }
            Err(e) => {
                tracing::error!("  ✗ {} failed: {}", entry.file_name, e);
                let ph = PlaceholderEntry::new(
                    &entry.path.to_string_lossy(),
                    &entry.file_name,
                    &hash,
                    entry.size,
                );
                store.append(&ph)?;
                failed += 1;
            }
        }
    }

    println!("\n  Upload complete: uploaded={} skipped={} failed={}", uploaded, skipped, failed);
    if failed > 0 {
        println!("  Run `sagco-gdrive hydrate` to retry failed uploads.");
    }
    Ok(())
}

// --- hydrate ----------------------------------------------------------------

async fn cmd_hydrate(cfg: &Config) -> Result<()> {
    let creds  = Credentials::load(&cfg.auth.credentials_path)?;
    let token  = get_access_token(&creds, &cfg.auth.scopes).await?;
    let client = DriveClient::new(token);
    let store  = PlaceholderStore::new(&cfg.logs.placeholder_dir)?;

    let result = hydrate(&store, &client, &cfg.drive.upload_folder_id).await?;
    println!("\n  Hydrate: resolved={} failed={} skipped={}", result.resolved, result.failed, result.skipped);
    Ok(())
}

// --- status -----------------------------------------------------------------

fn cmd_status(cfg: &Config) -> Result<()> {
    let store = PlaceholderStore::new(&cfg.logs.placeholder_dir)?;
    let all   = store.load_all()?;

    println!("\n  SAGCO GDRIVE STATUS");
    println!("  {:50}  {:10}  {}", "File", "Status", "SHA-256 (8)");
    println!("  {}", "-".repeat(80));
    for e in &all {
        let status = format!("{:?}", e.status);
        println!("  {:50}  {:10}  {}", e.file_name, status, &e.sha256[..8]);
    }
    println!("\n  Total: {}", all.len());
    Ok(())
}

// --- seal -------------------------------------------------------------------

fn cmd_seal(cfg: &Config) -> Result<()> {
    let store   = PlaceholderStore::new(&cfg.logs.placeholder_dir)?;
    let entries = store.load_all()?;
    let uploaded: Vec<_> = entries.iter()
        .filter(|e| e.status == PlaceholderStatus::Uploaded)
        .collect();

    let seal_path = &cfg.logs.sha256_sums_file;
    let mut f = std::fs::File::create(seal_path)?;
    for e in &uploaded {
        writeln!(f, "{}  {}", e.sha256, e.file_name)?;
    }

    // Seal the SHA256SUMS file itself
    let sums_content = std::fs::read_to_string(seal_path)?;
    let meta_hash = sha256_bytes(sums_content.as_bytes());
    writeln!(f, "{}  SHA256SUMS.meta", meta_hash)?;

    println!("\n  Sealed {} files → {}", uploaded.len(), seal_path);
    println!("  SHA256SUMS meta hash: {}", meta_hash);
    println!("  Verdict: {}", if uploaded.is_empty() { "INFLATED" } else { "PROVEN" });
    Ok(())
}
