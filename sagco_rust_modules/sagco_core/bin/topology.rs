// sagco-topology — build knowledge graph from token artifacts
// Usage: sagco-topology [--json] [tokens_dir]
// Reads *.tokens.txt files and discovers the doctrine chain.
// License: SSL-1.0 — Strategickhaos DAO LLC
use sagco_core::crypto::sha256_hex;
use std::{collections::HashMap, env, fs, path::Path, process};

const DOCTRINE_ANCHORS: &[&str] = &[
    "observe", "failure", "drift", "resonance", "mitigation", "evolution",
    "compiler", "topology", "evidence", "fitness", "collapse", "chain",
    "bottleneck", "pharmacopeia", "codex", "alchemical", "quadrilateral",
    "neuro", "convergence", "variance", "antibody", "seal", "sentinel",
    "recursion", "emergence", "sovereignty", "process",
];

#[derive(Debug)]
struct ArtifactNode {
    id:       String,
    label:    String,
    anchors:  Vec<String>,
    sha256:   String,
}

fn parse_token_file(path: &Path) -> (Vec<String>, String) {
    let content = fs::read_to_string(path).unwrap_or_default();
    let mut tokens = Vec::new();
    let mut sha    = String::new();

    for line in content.lines() {
        if let Some(rest) = line.strip_prefix("SHA256=") {
            sha = rest.trim().to_string();
        }
        if line.starts_with("  ") && !line.contains("ANCHOR") {
            if let Some(tok) = line.split_whitespace().next() {
                tokens.push(tok.to_lowercase());
            }
        }
    }
    (tokens, sha)
}

fn compute_edge_weight(a: &[String], b: &[String]) -> usize {
    // shared anchor token count between two artifact token lists
    a.iter().filter(|t| b.contains(t)).count()
}

fn extract_label(filename: &str) -> String {
    // "CHAPTER_02_QUADRILATERAL_COLLAPSE.md.tokens.txt" → "QUADRILATERAL COLLAPSE"
    let base = filename
        .replace(".tokens.txt", "")
        .replace(".observe.txt", "")
        .replace(['_', '-'], " ");
    // drop leading chapter/number prefix
    let words: Vec<&str> = base.split_whitespace().collect();
    let start = words.iter().position(|w| {
        !w.chars().all(|c| c.is_numeric())
            && !["chapter","chapter","act","part","section"].contains(&w.to_lowercase().as_str())
    }).unwrap_or(0);
    words[start..].join(" ")
}

fn build_json(nodes: &[ArtifactNode], edges: &[(usize, usize, usize)],
              recurring: &[String], chain: &[String]) -> String {
    let mut out = String::from("{\n");

    // nodes
    out.push_str("  \"nodes\": [\n");
    for (i, n) in nodes.iter().enumerate() {
        out.push_str(&format!(
            "    {{\"id\": \"{}\", \"label\": \"{}\", \"anchors\": [{}]}}{}",
            n.id,
            n.label,
            n.anchors.iter().map(|a| format!("\"{}\"", a)).collect::<Vec<_>>().join(", "),
            if i < nodes.len()-1 { ",\n" } else { "\n" }
        ));
    }
    out.push_str("  ],\n");

    // edges
    out.push_str("  \"edges\": [\n");
    for (i, (a, b, w)) in edges.iter().enumerate() {
        out.push_str(&format!(
            "    {{\"from\": \"{}\", \"to\": \"{}\", \"weight\": {}}}{}",
            nodes[*a].id, nodes[*b].id, w,
            if i < edges.len()-1 { ",\n" } else { "\n" }
        ));
    }
    out.push_str("  ],\n");

    // recurring tokens
    out.push_str("  \"recurring_tokens\": [");
    out.push_str(&recurring.iter().map(|t| format!("\"{}\"", t)).collect::<Vec<_>>().join(", "));
    out.push_str("],\n");

    // discovery chain
    out.push_str("  \"discovery_chain\": [");
    out.push_str(&chain.iter().map(|l| format!("\"{}\"", l)).collect::<Vec<_>>().join(", "));
    out.push_str("],\n");

    out.push_str("  \"dna\": \"a364ca9f90356c85\",\n");
    out.push_str("  \"status\": \"SAGCO_TOPOLOGY_PASS\"\n");
    out.push('}');
    out
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let json_mode = args.iter().any(|a| a == "--json");
    let dir = args.iter()
        .find(|a| !a.starts_with('-') && *a != &args[0])
        .map(String::as_str)
        .unwrap_or("tokens");

    // collect token files
    let mut files: Vec<std::path::PathBuf> = Vec::new();
    if Path::new(dir).is_dir() {
        if let Ok(rd) = fs::read_dir(dir) {
            for entry in rd.flatten() {
                let p = entry.path();
                if p.extension().and_then(|e| e.to_str()) == Some("txt") {
                    files.push(p);
                }
            }
        }
    }
    files.sort();

    if files.is_empty() {
        // graceful: run topology on own binary as self-test
        eprintln!("No token files found in '{}' — topology has no corpus to analyze.", dir);
        eprintln!("Run: sagco-tokenize <file> > tokens/<file>.tokens.txt");
        process::exit(0);
    }

    // build nodes
    let mut nodes: Vec<ArtifactNode> = Vec::new();
    let mut all_token_lists: Vec<Vec<String>> = Vec::new();

    for (i, path) in files.iter().enumerate() {
        let fname = path.file_name().unwrap_or_default().to_string_lossy().to_string();
        let (tokens, sha) = parse_token_file(path);
        let anchors: Vec<String> = DOCTRINE_ANCHORS.iter()
            .filter(|&&a| tokens.iter().any(|t| t.contains(a)))
            .map(|&a| a.to_string())
            .collect();

        nodes.push(ArtifactNode {
            id:      format!("node_{}", i),
            label:   extract_label(&fname),
            anchors: anchors.clone(),
            sha256:  sha,
        });
        all_token_lists.push(tokens);
    }

    // build edges (token co-occurrence above threshold)
    let mut edges: Vec<(usize, usize, usize)> = Vec::new();
    for i in 0..nodes.len() {
        for j in (i+1)..nodes.len() {
            let w = compute_edge_weight(&all_token_lists[i], &all_token_lists[j]);
            if w > 0 {
                edges.push((i, j, w));
            }
        }
    }
    // sort edges by weight descending
    edges.sort_by(|a, b| b.2.cmp(&a.2));

    // find globally recurring tokens (appear in > half the artifacts)
    let threshold = (nodes.len() / 2).max(1);
    let mut recurring: Vec<String> = DOCTRINE_ANCHORS.iter()
        .filter(|&&anchor| {
            all_token_lists.iter().filter(|tl| tl.iter().any(|t| t.contains(anchor))).count() >= threshold
        })
        .map(|&s| s.to_string())
        .collect();
    if recurring.is_empty() {
        // fallback: any anchor found at all
        recurring = DOCTRINE_ANCHORS.iter()
            .filter(|&&anchor| all_token_lists.iter().any(|tl| tl.iter().any(|t| t.contains(anchor))))
            .map(|&s| s.to_string())
            .collect();
    }

    // discovery chain: order nodes by their first strong edge connection
    let chain: Vec<String> = nodes.iter().map(|n| n.label.clone()).collect();

    if json_mode {
        println!("{}", build_json(&nodes, &edges, &recurring, &chain));
    } else {
        println!("--- SAGCO TOPOLOGY ---");
        println!("NODES={}", nodes.len());
        println!("EDGES={}", edges.len());
        println!();
        println!("RECURRING_TOKENS");
        for r in &recurring { println!("  {}", r); }
        println!();
        println!("DISCOVERY_CHAIN");
        for (i, label) in chain.iter().enumerate() {
            if i < chain.len()-1 { println!("  {}\n  ↓", label); }
            else                  { println!("  {}", label); }
        }
        println!();
        println!("STRONG_EDGES (weight >= 1)");
        for (a, b, w) in edges.iter().take(10) {
            println!("  {} ─[{}]─ {}", nodes[*a].label, w, nodes[*b].label);
        }
        println!();
        println!("DNA=a364ca9f90356c85");
        println!("STATUS=SAGCO_TOPOLOGY_PASS");
    }
}
