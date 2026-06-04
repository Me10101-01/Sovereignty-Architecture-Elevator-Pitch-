// crates/sagco-core/src/excavate.rs
// SAGCO Excavate module — walks a folder and classifies artifacts.
// Called from main.rs Command::Excavate handler.

use std::fs;
use std::path::Path;

pub struct ExcavateResult {
    pub folder:   String,
    pub total:    usize,
    pub reports:  usize,
    pub waves:    usize,
    pub configs:  usize,
    pub sources:  usize,
    pub other:    usize,
    pub manifest: String,
}

pub fn excavate(folder: &str) -> Result<ExcavateResult, String> {
    let root = Path::new(folder);
    if !root.exists() {
        return Err(format!("not_found:{}", folder));
    }

    let mut total   = 0usize;
    let mut reports = 0usize;
    let mut waves   = 0usize;
    let mut configs = 0usize;
    let mut sources = 0usize;
    let mut other   = 0usize;

    let entries = fs::read_dir(root)
        .map_err(|e| format!("read_dir_fail:{}", e))?;

    for entry in entries.flatten() {
        total += 1;
        let name = entry.file_name().to_string_lossy().to_string();
        let ext  = entry.path()
            .extension()
            .unwrap_or_default()
            .to_string_lossy()
            .to_string();

        match ext.as_str() {
            "md" | "txt" => reports += 1,
            "wav"        => waves   += 1,
            "yaml" | "yml" | "json" | "toml" | "csv" => configs += 1,
            "rs"  | "py" | "sh"  => sources += 1,
            _ => {
                if name.contains("report") || name.ends_with(".md") {
                    reports += 1;
                } else {
                    other += 1;
                }
            }
        }
    }

    let stamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();

    let manifest = format!(
        "EXCAVATE_TARGET={folder}\nSTAMP={stamp}\nARTIFACTS={total}\n\
         REPORTS={reports}\nWAVES={waves}\nCONFIGS={configs}\n\
         SOURCES={sources}\nOTHER={other}\nSTATUS=SAGCO_EXCAVATE_SEALED\n",
        folder  = folder,
        stamp   = stamp,
        total   = total,
        reports = reports,
        waves   = waves,
        configs = configs,
        sources = sources,
        other   = other,
    );

    Ok(ExcavateResult { folder: folder.to_string(), total, reports, waves, configs, sources, other, manifest })
}
