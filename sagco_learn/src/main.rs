/// sagco-learn — SAGCO organism URL fetch + learn pipeline
///
/// Usage:
///   sagco-learn <url> [output_dir]
///   sagco-learn https://youtu.be/jQ194vU4Qkk ~/sagco_learning
///
/// Writes per-URL artifacts:
///   sagco_learn_<id>.manifest  — JSON metadata
///   sagco_learn_<id>.txt       — extracted text
///   sagco_learn_<id>.md        — structured learning note
///
/// Primitives emitted: FETCH_URL → LEARN_INGEST → DNA_ENCODE

use std::{
    collections::HashSet,
    fs,
    path::PathBuf,
    time::{SystemTime, UNIX_EPOCH},
};

// ── Primitive lattice extensions ──────────────────────────────────────────────
const PRIM_FETCH:   &str = "FETCH_URL";
const PRIM_LEARN:   &str = "LEARN_INGEST";
const PRIM_DNA:     &str = "DNA_ENCODE";
const PRIM_RECON:   &str = "RECON_SCAN";
const PRIM_SYNTH:   &str = "SYNTH_EMIT";
const PRIM_KERNEL:  &str = "KERNEL_EXEC";
const PRIM_BYTECODE:&str = "BYTECODE_EMIT";
const PRIM_AGENT:   &str = "AGENT_SPAWN";
const PRIM_VAULT:   &str = "VAULT_WRITE";
const PRIM_DEPLOY:  &str = "DEPLOY_EXEC";
const PRIM_DISPATCH:&str = "DISPATCH_CALL";
const PRIM_INGEST:  &str = "INGEST";

// Keyword → primitive mapping (organism domain classifier)
const DOMAIN_MAP: &[(&str, &str)] = &[
    ("recon",      PRIM_RECON),
    ("exploit",    "EXPLOIT_MODEL"),
    ("kerberos",   "KERBEROS_TICKET"),
    ("sql",        "SQLI_PATTERN"),
    ("neural",     PRIM_DNA),
    ("rust",       PRIM_BYTECODE),
    ("kubernetes", PRIM_DEPLOY),
    ("assembly",   PRIM_KERNEL),
    ("crypto",     PRIM_VAULT),
    ("agent",      PRIM_AGENT),
    ("learn",      PRIM_LEARN),
    ("music",      PRIM_SYNTH),
    ("audio",      PRIM_SYNTH),
    ("dispatch",   PRIM_DISPATCH),
    ("ingest",     PRIM_INGEST),
    ("compile",    PRIM_BYTECODE),
    ("kernel",     PRIM_KERNEL),
    ("deploy",     PRIM_DEPLOY),
    ("sovereign",  PRIM_DISPATCH),
    ("sagco",      PRIM_INGEST),
    ("dna",        PRIM_DNA),
    ("cell",       PRIM_DNA),
    ("organism",   PRIM_DNA),
];

// ── Artifact ─────────────────────────────────────────────────────────────────
struct Artifact {
    id:         String,
    url:        String,
    title:      String,
    text:       String,
    primitives: Vec<String>,
    ts:         u64,
    status:     u16,
}

impl Artifact {
    fn manifest_json(&self) -> String {
        let prims = self.primitives
            .iter()
            .map(|p| format!("\"{}\"", p))
            .collect::<Vec<_>>()
            .join(",");
        format!(
            r#"{{"id":"{}","url":"{}","title":"{}","status":{},"primitives":[{}],"ts":{}}}"#,
            self.id,
            self.url.replace('"', "%22"),
            self.title.replace('"', "'").replace('\n', " "),
            self.status,
            prims,
            self.ts,
        )
    }

    fn md_note(&self) -> String {
        let prims = self.primitives.join(", ");
        let preview = &self.text[..self.text.len().min(1800)];
        format!(
            "# SAGCO Learn: {}\n\n\
             - **url**: {}\n\
             - **ts**: {}\n\
             - **status**: {}\n\
             - **primitives**: {}\n\n\
             ## Extracted Content\n\n{}\n",
            self.title, self.url, self.ts, self.status, prims, preview
        )
    }

    fn write_to(&self, dir: &PathBuf) -> Result<(), String> {
        fs::create_dir_all(dir)
            .map_err(|e| format!("mkdir {}: {}", dir.display(), e))?;

        let base = dir.join(format!("sagco_learn_{}", self.id));

        fs::write(base.with_extension("manifest"), self.manifest_json() + "\n")
            .map_err(|e| format!("write manifest: {}", e))?;

        fs::write(base.with_extension("txt"), &self.text)
            .map_err(|e| format!("write txt: {}", e))?;

        fs::write(base.with_extension("md"), self.md_note())
            .map_err(|e| format!("write md: {}", e))?;

        Ok(())
    }
}

// ── HTTP fetch ────────────────────────────────────────────────────────────────
fn fetch(url: &str) -> Result<(u16, String, String), String> {
    let agent = ureq::AgentBuilder::new()
        .user_agent("SAGCO-Organism/0.1 (learn-mode; +https://github.com/Me10101-01/Sovereignty-Architecture-Elevator-Pitch-)")
        .redirects(6)
        .build();

    let resp = agent
        .get(url)
        .call()
        .map_err(|e| format!("fetch {}: {}", url, e))?;

    let status = resp.status();
    let content_type = resp.header("content-type").unwrap_or("").to_string();
    let body = resp
        .into_string()
        .map_err(|e| format!("read body: {}", e))?;

    Ok((status, content_type, body))
}

// ── HTML → text ───────────────────────────────────────────────────────────────
fn extract_title(html: &str) -> String {
    let lower = html.to_lowercase();
    if let (Some(s), Some(e)) = (lower.find("<title>"), lower.find("</title>")) {
        if e > s + 7 {
            return html[s + 7..e].trim().to_string();
        }
    }
    String::new()
}

fn strip_html(html: &str) -> String {
    let lower = html.to_lowercase();
    let mut out = String::with_capacity(html.len() / 2);
    let mut in_tag = false;
    let mut skip_block = false;
    let mut i = 0;
    let b = html.as_bytes();

    while i < b.len() {
        let rest = &lower[i..];
        if !skip_block && (rest.starts_with("<script") || rest.starts_with("<style")) {
            skip_block = true;
        }
        if skip_block && (rest.starts_with("</script>") || rest.starts_with("</style>")) {
            skip_block = false;
            i += 9;
            continue;
        }
        if skip_block { i += 1; continue; }
        match b[i] as char {
            '<'  => in_tag = true,
            '>'  => { in_tag = false; out.push(' '); }
            c if !in_tag => out.push(c),
            _ => {}
        }
        i += 1;
    }
    // Collapse whitespace
    out.split_whitespace().collect::<Vec<_>>().join(" ")
}

// ── Primitive classifier ──────────────────────────────────────────────────────
fn classify(text: &str, content_type: &str) -> Vec<String> {
    let lower = text.to_lowercase();
    let mut seen = HashSet::new();
    let mut prims = vec![PRIM_FETCH.to_string(), PRIM_LEARN.to_string()];
    seen.insert(PRIM_FETCH);
    seen.insert(PRIM_LEARN);

    if content_type.contains("html")  { prims.push("PARSE_HTML".to_string()); }
    if content_type.contains("json")  { prims.push("PARSE_JSON".to_string()); }
    if content_type.contains("audio") { prims.push(PRIM_SYNTH.to_string()); }
    if content_type.contains("video") { prims.push(PRIM_SYNTH.to_string()); }

    for (kw, prim) in DOMAIN_MAP {
        if !seen.contains(prim) && lower.contains(kw) {
            prims.push(prim.to_string());
            seen.insert(prim);
        }
    }
    prims
}

// ── Artifact ID ───────────────────────────────────────────────────────────────
fn artifact_id(ts: u64, url: &str) -> String {
    // Simple non-crypto hash: FNV-1a over url bytes XOR ts
    let mut h: u64 = 0xcbf29ce484222325;
    for b in url.bytes() {
        h ^= b as u64;
        h = h.wrapping_mul(0x100000001b3);
    }
    h ^= ts;
    format!("{:016x}", h)
}

// ── Main ──────────────────────────────────────────────────────────────────────
fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        eprintln!("usage: sagco-learn <url> [output_dir]");
        eprintln!("       sagco-learn https://youtu.be/jQ194vU4Qkk ~/sagco_learning");
        std::process::exit(1);
    }

    let url        = &args[1];
    let output_dir = PathBuf::from(args.get(2).map(String::as_str).unwrap_or("./sagco_learning"));

    let ts = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();

    println!("[sagco-learn] fetching: {}", url);

    let (status, content_type, body) = match fetch(url) {
        Ok(r)  => r,
        Err(e) => { eprintln!("[sagco-learn] error: {}", e); std::process::exit(1); }
    };

    let title = if content_type.contains("html") {
        let t = extract_title(&body);
        if t.is_empty() { url.clone() } else { t }
    } else {
        url.split('/').last().unwrap_or(url).to_string()
    };

    let text = if content_type.contains("html") {
        strip_html(&body)
    } else {
        body.clone()
    };

    let primitives = classify(&text, &content_type);
    let id         = artifact_id(ts, url);

    let artifact = Artifact { id: id.clone(), url: url.clone(), title: title.clone(),
                              text, primitives: primitives.clone(), ts, status };

    match artifact.write_to(&output_dir) {
        Ok(_)  => {},
        Err(e) => { eprintln!("[sagco-learn] write error: {}", e); std::process::exit(1); }
    }

    println!("[sagco-learn] ✓");
    println!("  title      : {}", title);
    println!("  status     : {}", status);
    println!("  primitives : {}", primitives.join(" → "));
    println!("  id         : {}", id);
    println!("  output     : {}/sagco_learn_{}.{{manifest,txt,md}}", output_dir.display(), id);
}
