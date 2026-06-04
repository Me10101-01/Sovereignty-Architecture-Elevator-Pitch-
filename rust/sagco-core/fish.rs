// crates/sagco-core/src/fish.rs
// SAGCO Fish module — recursive filesystem search.
// fish <folder>  →  walks entire subtree, classifies all artifacts,
//                   returns match list + manifest.
// Contrast with excavate: excavate = top-level census, fish = deep search.

use std::fs;
use std::path::{Path, PathBuf};

pub struct FishMatch {
    pub path:  String,
    pub kind:  String,   // SOURCE | CONFIG | REPORT | PIPELINE | BINARY | DOCS | OTHER
    pub bytes: u64,
}

pub struct FishResult {
    pub folder:    String,
    pub total:     usize,
    pub sources:   usize,
    pub configs:   usize,
    pub reports:   usize,
    pub pipelines: usize,
    pub binaries:  usize,
    pub docs:      usize,
    pub other:     usize,
    pub depth_max: usize,
    pub matches:   Vec<FishMatch>,
    pub manifest:  String,
}

fn classify(path: &Path) -> &'static str {
    let ext = path.extension().unwrap_or_default().to_str().unwrap_or("");
    let stem = path.file_name().unwrap_or_default().to_str().unwrap_or("").to_lowercase();

    match ext {
        "rs" | "py" | "js" | "ts" | "go" | "c" | "cpp" | "h" | "java" | "kt" => "SOURCE",
        "yaml" | "yml" | "toml" | "json" | "env" | "ini" | "cfg" | "conf"     => "CONFIG",
        "txt" | "csv" if stem.contains("pipeline") || stem.starts_with("pipeline_") => "PIPELINE",
        "md" | "pdf" | "docx"                                                  => "DOCS",
        "bin" | "so" | "exe" | "elf"                                           => "BINARY",
        "txt" | "csv" | "log"                                                  => "REPORT",
        _ => {
            if stem.contains("report") || stem.contains("manifest") || stem.contains("evidence") {
                "REPORT"
            } else if stem.contains("pipeline") || stem.starts_with("pipeline_") {
                "PIPELINE"
            } else {
                "OTHER"
            }
        }
    }
}

fn walk(
    dir: &Path,
    depth: usize,
    max_depth: &mut usize,
    matches: &mut Vec<FishMatch>,
) {
    if depth > 12 { return; }  // guard against deep symlink loops

    let entries = match fs::read_dir(dir) {
        Ok(e)  => e,
        Err(_) => return,
    };

    for entry in entries.flatten() {
        let path = entry.path();
        let meta = match entry.metadata() {
            Ok(m)  => m,
            Err(_) => continue,
        };

        // skip hidden directories except .cargo inspection isn't needed
        let name = entry.file_name();
        let name_s = name.to_string_lossy();
        if name_s.starts_with('.') { continue; }
        if name_s == "target" { continue; }   // skip cargo build artifacts

        if meta.is_dir() {
            if depth + 1 > *max_depth { *max_depth = depth + 1; }
            walk(&path, depth + 1, max_depth, matches);
        } else if meta.is_file() {
            if depth > *max_depth { *max_depth = depth; }
            let kind  = classify(&path);
            let bytes = meta.len();
            matches.push(FishMatch {
                path:  path.to_string_lossy().to_string(),
                kind:  kind.to_string(),
                bytes,
            });
        }
    }
}

pub fn search(folder: &str) -> Result<FishResult, String> {
    let root = PathBuf::from(folder);
    if !root.exists() {
        return Err(format!("not_found:{}", folder));
    }
    if !root.is_dir() {
        return Err(format!("not_a_dir:{}", folder));
    }

    let mut matches:   Vec<FishMatch> = Vec::new();
    let mut depth_max: usize          = 0;

    walk(&root, 0, &mut depth_max, &mut matches);

    let total     = matches.len();
    let sources   = matches.iter().filter(|m| m.kind == "SOURCE").count();
    let configs   = matches.iter().filter(|m| m.kind == "CONFIG").count();
    let reports   = matches.iter().filter(|m| m.kind == "REPORT").count();
    let pipelines = matches.iter().filter(|m| m.kind == "PIPELINE").count();
    let binaries  = matches.iter().filter(|m| m.kind == "BINARY").count();
    let docs      = matches.iter().filter(|m| m.kind == "DOCS").count();
    let other     = matches.iter().filter(|m| m.kind == "OTHER").count();

    let stamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();

    // Top 10 largest files for the manifest summary
    let mut sorted: Vec<&FishMatch> = matches.iter().collect();
    sorted.sort_by(|a, b| b.bytes.cmp(&a.bytes));
    let top_files: String = sorted.iter().take(10).map(|m| {
        format!("  {}  {}B  {}\n", m.kind, m.bytes, m.path)
    }).collect();

    let manifest = format!(
        "FISH_TARGET={folder}\n\
         STAMP={stamp}\n\
         TOTAL={total}\n\
         SOURCES={sources}\n\
         CONFIGS={configs}\n\
         REPORTS={reports}\n\
         PIPELINES={pipelines}\n\
         BINARIES={binaries}\n\
         DOCS={docs}\n\
         OTHER={other}\n\
         DEPTH_MAX={depth_max}\n\
         TOP_FILES:\n{top_files}\
         STATUS=SAGCO_FISH_SEALED\n",
        folder    = folder,
        stamp     = stamp,
        total     = total,
        sources   = sources,
        configs   = configs,
        reports   = reports,
        pipelines = pipelines,
        binaries  = binaries,
        docs      = docs,
        other     = other,
        depth_max = depth_max,
        top_files = top_files,
    );

    Ok(FishResult {
        folder: folder.to_string(),
        total, sources, configs, reports, pipelines, binaries, docs, other,
        depth_max, matches, manifest,
    })
}

pub fn report(result: &Result<FishResult, String>) -> String {
    match result {
        Err(e) => format!("[FISH_ERROR]: {}\n", e),
        Ok(r)  => format!(
            "[FISH]: {folder} TOTAL={total} SOURCES={sources} CONFIGS={configs} \
             REPORTS={reports} PIPELINES={pipelines} DOCS={docs} OTHER={other} \
             DEPTH={depth}\n",
            folder    = r.folder,
            total     = r.total,
            sources   = r.sources,
            configs   = r.configs,
            reports   = r.reports,
            pipelines = r.pipelines,
            docs      = r.docs,
            other     = r.other,
            depth     = r.depth_max,
        ),
    }
}
