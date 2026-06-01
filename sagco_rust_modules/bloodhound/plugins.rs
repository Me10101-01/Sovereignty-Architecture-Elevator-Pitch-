// SAGCO Plugin Registry — SagcoInput implementations for every source type
// Every source: PDF | URL | Terminal | Image | SQL | Obsidian | GoogleDrive
// License: SSL-1.0 — Strategickhaos DAO LLC

use super::types::{SagcoInput, SagcoArtifact};
use crate::antibody::types::{Antibody, Trajectory, EurScore};

// ── plugin tag ────────────────────────────────────────────────────────────────
#[derive(Debug, Clone, PartialEq)]
pub enum PluginKind {
    Pdf,
    Url,
    Terminal,
    Image,
    Sql,
    Obsidian,
    GoogleDrive,
    Dropbox,
    Claude,
    RustBinary,
    Markdown,
    Yaml,
}

impl PluginKind {
    pub fn from_path(path: &str) -> Self {
        let p = path.to_lowercase();
        if p.ends_with(".pdf")        { PluginKind::Pdf }
        else if p.ends_with(".rs")    { PluginKind::RustBinary }
        else if p.ends_with(".md")    { PluginKind::Markdown }
        else if p.ends_with(".yaml") || p.ends_with(".yml") { PluginKind::Yaml }
        else if p.ends_with(".db")    { PluginKind::Sql }
        else if p.starts_with("http") { PluginKind::Url }
        else if p.contains("drive.google") { PluginKind::GoogleDrive }
        else if p.contains("dropbox") { PluginKind::Dropbox }
        else if p.contains("claude")  { PluginKind::Claude }
        else if p.contains("obsidian") { PluginKind::Obsidian }
        else                          { PluginKind::Terminal }
    }

    pub fn extractor_command(&self) -> &'static str {
        match self {
            PluginKind::Pdf        => "pdftotext <file> - | strings",
            PluginKind::Url        => "curl -sL <url> | strings",
            PluginKind::Terminal   => "bash -c '<cmd>' 2>&1 | strings",
            PluginKind::Image      => "tesseract <file> stdout | strings",
            PluginKind::Sql        => "sqlite3 <db> .dump | strings",
            PluginKind::Obsidian   => "find <vault> -name '*.md' | xargs cat",
            PluginKind::GoogleDrive => "gdrive download <id> | strings",
            PluginKind::Dropbox    => "curl -L '<dropbox_url>' | strings",
            PluginKind::Claude     => "sagco past <session_log>",
            PluginKind::RustBinary => "strings <elf> | grep sagco",
            PluginKind::Markdown   => "cat <file> | strings",
            PluginKind::Yaml       => "cat <file> | strings",
        }
    }
}

// ── generic plugin wrapper ────────────────────────────────────────────────────
pub struct SagcoPlugin {
    pub kind:      PluginKind,
    pub source_id: String,
    pub raw_text:  String,
    pub sha256:    String,
}

impl SagcoPlugin {
    pub fn new(source: &str, raw_text: String) -> Self {
        let kind = PluginKind::from_path(source);
        // deterministic mock sha — real impl uses sha2 crate
        let sha256 = format!("{:016x}", raw_text.len() as u64 * 0xdeadbeef);
        SagcoPlugin {
            kind,
            source_id: source.to_owned(),
            raw_text,
            sha256,
        }
    }
}

impl SagcoInput for SagcoPlugin {
    fn source_id(&self) -> &str { &self.source_id }

    fn tokenize(&self) -> Vec<String> {
        self.raw_text
            .split_whitespace()
            .filter(|w| w.len() >= 4)
            .map(|w| w.to_lowercase())
            .collect::<std::collections::HashSet<_>>()
            .into_iter()
            .collect()
    }

    fn fingerprint(&self) -> String {
        // content-addressable 64-bit hex
        let h: u64 = self.raw_text.bytes()
            .enumerate()
            .fold(0xcbf29ce484222325_u64, |acc, (i, b)| {
                acc.wrapping_mul(0x100000001b3)
                   .wrapping_add(b as u64)
                   .wrapping_add(i as u64)
            });
        format!("{:016x}", h)
    }

    fn classify(&self) -> (Antibody, Trajectory) {
        let t = self.raw_text.to_lowercase();
        if t.contains("pass") || t.is_empty() {
            (Antibody::PassImmunity, Trajectory::Stabilized)
        } else if t.contains("no such file") || t.contains("not found") {
            (Antibody::PathDiscovery, Trajectory::Adaptation)
        } else if t.contains("host not in allowlist") {
            (Antibody::Dependency, Trajectory::Evolution)
        } else {
            (Antibody::UnknownVariance, Trajectory::Mutation)
        }
    }

    fn artifact(&self) -> SagcoArtifact {
        let tokens = self.tokenize();
        let (antibody, trajectory) = self.classify();
        let score = match trajectory {
            Trajectory::Stabilized => EurScore::Pass,
            Trajectory::Adaptation => EurScore::Adapt,
            Trajectory::Evolution  => EurScore::Evolve,
            Trajectory::Mutation   => EurScore::Fail,
        };
        SagcoArtifact {
            source_id:   self.source_id.clone(),
            token_count: tokens.len(),
            fingerprint: self.fingerprint(),
            sha256:      self.sha256.clone(),
            antibody,
            trajectory,
            score,
        }
    }
}

// ── plugin registry ───────────────────────────────────────────────────────────
pub struct PluginRegistry {
    plugins: Vec<SagcoPlugin>,
}

impl PluginRegistry {
    pub fn new() -> Self { PluginRegistry { plugins: vec![] } }

    pub fn register(&mut self, source: &str, raw_text: String) {
        self.plugins.push(SagcoPlugin::new(source, raw_text));
    }

    pub fn run_all(&self) -> Vec<SagcoArtifact> {
        self.plugins.iter().map(|p| p.artifact()).collect()
    }

    pub fn frequency_map(&self) -> Vec<(String, usize)> {
        let mut counts = std::collections::HashMap::new();
        for p in &self.plugins {
            let (ab, _) = p.classify();
            *counts.entry(format!("{:?}", ab)).or_insert(0usize) += 1;
        }
        let mut v: Vec<_> = counts.into_iter().collect();
        v.sort_by(|a, b| b.1.cmp(&a.1));
        v
    }
}
