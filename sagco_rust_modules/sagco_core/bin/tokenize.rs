// sagco-tokenize — token extraction and frequency engine
// Usage: sagco-tokenize <file>
// License: SSL-1.0 — Strategickhaos DAO LLC
use sagco_core::crypto::sha256_hex;
use std::{collections::HashMap, env, fs, process};

// Semantic anchors — terms that indicate doctrine/concept density
const ANCHOR_TERMS: &[&str] = &[
    "process", "compiler", "topology", "evidence", "observe", "failure",
    "drift", "resonance", "mitigation", "evolution", "collapse", "chain",
    "bottleneck", "pharmacopeia", "codex", "alchemical", "quadrilateral",
    "neuro", "theorem", "convergence", "variance", "antibody", "seal",
    "sentinel", "recursion", "emergence", "sovereignty", "protocol",
];

fn extract_printable_text(data: &[u8]) -> String {
    // works for plaintext, MD, and extracts readable runs from binary formats
    if let Ok(s) = std::str::from_utf8(data) {
        return s.to_string();
    }
    // fallback: extract printable ASCII runs >= 4 chars
    let mut out = String::new();
    let mut run = Vec::new();
    for &b in data {
        if b >= 0x20 && b < 0x7F || b == b'\n' {
            run.push(b);
        } else if run.len() >= 4 {
            out.push_str(&String::from_utf8_lossy(&run));
            out.push(' ');
            run.clear();
        } else {
            run.clear();
        }
    }
    out
}

fn tokenize(text: &str) -> HashMap<String, usize> {
    let mut freq: HashMap<String, usize> = HashMap::new();
    for word in text.split(|c: char| !c.is_alphanumeric() && c != '_' && c != '-') {
        let w = word.to_lowercase();
        if w.len() >= 4
            && !["this","that","with","from","have","been","will","were",
                 "they","their","when","then","than","into","also","more",
                 "some","such","each","your","here","there","which","what",
                 "would","could","should","about","after","before","through"].contains(&w.as_str())
        {
            *freq.entry(w).or_insert(0) += 1;
        }
    }
    freq
}

fn find_anchors(freq: &HashMap<String, usize>) -> Vec<String> {
    ANCHOR_TERMS.iter()
        .filter(|&&term| freq.keys().any(|k| k.contains(term)))
        .map(|&t| t.to_string())
        .collect()
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: sagco-tokenize <file>");
        process::exit(1);
    }
    let path = &args[1];
    let data = match fs::read(path) {
        Ok(d) => d,
        Err(e) => {
            println!("TOKENIZE_TARGET={}", path);
            println!("STATUS=PATH_DISCOVERY_ANTIBODY  error={}", e);
            process::exit(1);
        }
    };

    let sha  = sha256_hex(&data);
    let text = extract_printable_text(&data);
    let freq = tokenize(&text);

    let mut ranked: Vec<(&String, &usize)> = freq.iter().collect();
    ranked.sort_by(|a, b| b.1.cmp(a.1).then(a.0.cmp(b.0)));
    ranked.truncate(40);

    let anchors = find_anchors(&freq);
    let top_tokens: Vec<String> = ranked.iter().take(10).map(|(k, _)| (*k).clone()).collect();

    println!("TOKENIZE_TARGET={}", path);
    println!("SHA256={}", sha);
    println!("TOTAL_UNIQUE_TOKENS={}", freq.len());
    println!("TOP_TOKENS={}", top_tokens.join(","));
    println!();
    println!("ANCHOR_TOKENS_FOUND={}", anchors.len());
    for a in &anchors { println!("  ANCHOR={}", a); }
    println!();
    println!("TOKEN_FREQUENCY_TABLE");
    for (token, count) in &ranked {
        println!("  {}\t{}", token, count);
    }
    println!();
    println!("DNA=a364ca9f90356c85");
    println!("STATUS=SAGCO_TOKENIZE_PASS");
}
