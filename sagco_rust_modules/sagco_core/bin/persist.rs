// sagco-persist — translate SAGCO pipeline stdout into SQL INSERT statements
// Usage: sagco-evidence reports/ tokens/ | sagco-persist | psql $DATABASE_URL
//        sagco-topology --json tokens/ | sagco-persist --topology | psql $DATABASE_URL
//        sagco-core pipeline.txt | sagco-persist --events | psql $DATABASE_URL
//
// Flags:
//   --evidence   (default) parse sagco-evidence output → sagco_seals + sagco_evidence_chains
//   --topology              parse sagco-topology --json → sagco_topology_nodes + sagco_topology_edges
//   --events                parse sagco-core output     → sagco_antibody_events + sagco_sentinel_events
//   --tokens                parse sagco-tokenize output → sagco_token_frequencies
//   --dry-run               print SQL but do not write to stdout (use stderr for diagnostics)
//
// License: SSL-1.0 — Strategickhaos DAO LLC
use std::{env, io::{self, BufRead}, process};

const DNA: &str = "a364ca9f90356c85";

// ─── SQL helpers ─────────────────────────────────────────────────────────────

fn sql_str(s: &str) -> String {
    format!("'{}'", s.replace('\'', "''"))
}

fn sql_array(items: &[&str]) -> String {
    if items.is_empty() {
        return "'{}'".to_string();
    }
    let inner: Vec<String> = items.iter().map(|s| format!("\"{}\"", s.replace('"', "\\\""))).collect();
    format!("ARRAY[{}]::TEXT[]", inner.iter().map(|s| format!("'{}'", s)).collect::<Vec<_>>().join(", "))
}

// ─── Evidence / Seal parser ───────────────────────────────────────────────────

fn parse_evidence(lines: &[String]) -> Vec<String> {
    let mut sql = Vec::new();
    let mut chain_hash = String::new();
    let mut reports_dir = String::new();
    let mut tokens_dir  = String::new();
    let mut total: i64  = 0;

    for line in lines {
        if let Some(v) = line.strip_prefix("CHAIN_HASH=") {
            chain_hash = v.trim().to_string();
        } else if let Some(v) = line.strip_prefix("REPORTS_DIR=") {
            reports_dir = v.trim().to_string();
        } else if let Some(v) = line.strip_prefix("TOKENS_DIR=") {
            tokens_dir = v.trim().to_string();
        } else if let Some(v) = line.strip_prefix("TOTAL_ARTIFACTS=") {
            total = v.trim().parse().unwrap_or(0);
        } else if line.starts_with("REPORT  ") || line.starts_with("TOKEN  ") {
            // "REPORT  <sha256>  <path>" or "TOKEN  <sha256>  <path>"
            let parts: Vec<&str> = line.splitn(3, "  ").collect();
            if parts.len() == 3 {
                let sha   = parts[1].trim();
                let path  = parts[2].trim();
                if sha == "EMPTY_PAYLOAD_ANTIBODY" {
                    // log as antibody event, not a seal
                    sql.push(format!(
                        "INSERT INTO sagco_antibody_events (antibody_name, variant, message, target, tool_source, dna) VALUES ({}, {}, {}, {}, {}, {});",
                        sql_str("EMPTY_PAYLOAD_ANTIBODY"),
                        sql_str("EmptyPayload"),
                        sql_str("File had zero bytes — EMPTY_PAYLOAD_ANTIBODY"),
                        sql_str(path),
                        sql_str("sagco-evidence"),
                        sql_str(DNA),
                    ));
                } else {
                    let artifact = format!("{}.seal", path);
                    sql.push(format!(
                        "INSERT INTO sagco_seals (target, sha256, artifact_path, dna) VALUES ({}, {}, {}, {});",
                        sql_str(path),
                        sql_str(sha),
                        sql_str(&artifact),
                        sql_str(DNA),
                    ));
                }
            }
        }
    }

    if !chain_hash.is_empty() {
        sql.push(format!(
            "INSERT INTO sagco_evidence_chains (chain_hash, reports_dir, tokens_dir, total_artifacts, dna) VALUES ({}, {}, {}, {}, {}) ON CONFLICT (chain_hash) DO NOTHING;",
            sql_str(&chain_hash),
            sql_str(&reports_dir),
            sql_str(&tokens_dir),
            total,
            sql_str(DNA),
        ));
    }

    sql
}

// ─── Topology JSON parser (minimal, no serde dep) ────────────────────────────

fn extract_json_str_field<'a>(obj: &'a str, key: &str) -> Option<&'a str> {
    let needle = format!("\"{}\":", key);
    let pos = obj.find(&needle)?;
    let after = obj[pos + needle.len()..].trim_start();
    if after.starts_with('"') {
        let inner = &after[1..];
        let end   = inner.find('"')?;
        Some(&inner[..end])
    } else {
        None
    }
}

fn extract_json_int_field(obj: &str, key: &str) -> Option<i64> {
    let needle = format!("\"{}\":", key);
    let pos = obj.find(&needle)?;
    let after = obj[pos + needle.len()..].trim_start();
    let end = after.find(|c: char| !c.is_ascii_digit())?;
    after[..end].parse().ok()
}

fn extract_json_str_array(obj: &str, key: &str) -> Vec<String> {
    let needle = format!("\"{}\":", key);
    let Some(pos) = obj.find(&needle) else { return Vec::new(); };
    let after = obj[pos + needle.len()..].trim_start();
    if !after.starts_with('[') { return Vec::new(); }
    let Some(close) = after.find(']') else { return Vec::new(); };
    let inner = &after[1..close];
    inner.split(',')
        .map(|s| s.trim().trim_matches('"').to_string())
        .filter(|s| !s.is_empty())
        .collect()
}

fn parse_topology(lines: &[String]) -> Vec<String> {
    let raw = lines.join("\n");
    let mut sql = Vec::new();

    // parse nodes array
    if let Some(nodes_start) = raw.find("\"nodes\":") {
        let after = &raw[nodes_start..];
        if let Some(arr_start) = after.find('[') {
            // split on "}," to get individual node objects
            let arr_region = &after[arr_start..];
            let items: Vec<&str> = arr_region.split("},{").collect();
            for (i, item) in items.iter().enumerate() {
                let node_id = extract_json_str_field(item, "id").unwrap_or("").to_string();
                let label   = extract_json_str_field(item, "label").unwrap_or("").to_string();
                let anchors = extract_json_str_array(item, "anchors");
                if node_id.is_empty() { continue; }
                let anchor_refs: Vec<&str> = anchors.iter().map(|s| s.as_str()).collect();
                sql.push(format!(
                    "INSERT INTO sagco_topology_nodes (node_id, label, anchors, dna) VALUES ({}, {}, {}, {}) ON CONFLICT (node_id) DO UPDATE SET label=EXCLUDED.label, anchors=EXCLUDED.anchors;",
                    sql_str(&node_id),
                    sql_str(&label),
                    sql_array(&anchor_refs),
                    sql_str(DNA),
                ));
                let _ = i; // suppress warning
            }
        }
    }

    // parse edges array
    if let Some(edges_start) = raw.find("\"edges\":") {
        let after = &raw[edges_start..];
        if let Some(arr_start) = after.find('[') {
            let arr_region = &after[arr_start..];
            let items: Vec<&str> = arr_region.split("},{").collect();
            for item in &items {
                let from   = extract_json_str_field(item, "from").unwrap_or("").to_string();
                let to     = extract_json_str_field(item, "to").unwrap_or("").to_string();
                let weight = extract_json_int_field(item, "weight").unwrap_or(0);
                if from.is_empty() || to.is_empty() { continue; }
                sql.push(format!(
                    "INSERT INTO sagco_topology_edges (from_node_id, to_node_id, weight, dna) VALUES ({}, {}, {}, {}) ON CONFLICT (from_node_id, to_node_id) DO UPDATE SET weight=EXCLUDED.weight;",
                    sql_str(&from),
                    sql_str(&to),
                    weight,
                    sql_str(DNA),
                ));
            }
        }
    }

    sql
}

// ─── SAGCO-core event parser (antibody + sentinel) ────────────────────────────

fn parse_events(lines: &[String]) -> Vec<String> {
    let mut sql = Vec::new();

    for line in lines {
        // Antibody lines look like: [ANTIBODY] PATH_DISCOVERY_ANTIBODY target=<path> ...
        if line.contains("ANTIBODY") && !line.contains("INSERT") {
            let variant = if line.contains("EMPTY_PAYLOAD") { "EmptyPayload" }
                else if line.contains("PATH_DISCOVERY") { "PathDiscovery" }
                else if line.contains("MISSING_SEAL") { "MissingSeal" }
                else if line.contains("CREEP_ALERT") || line.contains("SAGCO_CREEP") { "CreepAlert" }
                else { "Unknown" };
            let target = line.split("target=").nth(1)
                .map(|s| s.split_whitespace().next().unwrap_or(""))
                .unwrap_or("");
            sql.push(format!(
                "INSERT INTO sagco_antibody_events (antibody_name, variant, message, target, tool_source, dna) VALUES ({}, {}, {}, {}, {}, {});",
                sql_str(&format!("{}_ANTIBODY", variant.to_uppercase())),
                sql_str(variant),
                sql_str(line.trim()),
                sql_str(target),
                sql_str("sagco-core"),
                sql_str(DNA),
            ));
        }
        // Sentinel lines
        else if line.starts_with("SAGCO_CREEP_ALERT") {
            let target = line.split("target=").nth(1)
                .map(|s| s.split_whitespace().next().unwrap_or(""))
                .unwrap_or("");
            let alert_type = if line.contains("ARTIFACT_MISSING") { "ArtifactMissing" }
                else if line.contains("HASH_TAMPERED") { "HashTampered" }
                else if line.contains("DNA_MUTATED") { "DnaMutated" }
                else { "Unknown" };
            sql.push(format!(
                "INSERT INTO sagco_sentinel_events (alert_type, target, message, dna) VALUES ({}, {}, {}, {});",
                sql_str(alert_type),
                sql_str(target),
                sql_str(line.trim()),
                sql_str(DNA),
            ));
        } else if line.starts_with("REALITY_HOLDS") {
            sql.push(format!(
                "INSERT INTO sagco_sentinel_events (alert_type, target, message, dna) VALUES ({}, {}, {}, {});",
                sql_str("RealityHolds"),
                sql_str(""),
                sql_str(line.trim()),
                sql_str(DNA),
            ));
        }
    }

    sql
}

// ─── Token frequency parser ───────────────────────────────────────────────────

fn parse_tokens(lines: &[String]) -> Vec<String> {
    let mut sql       = Vec::new();
    let mut source    = String::new();
    let mut anchors   = std::collections::HashSet::new();
    let mut in_table  = false;

    for line in lines {
        if let Some(v) = line.strip_prefix("TOKENIZE_TARGET=") {
            source = v.trim().to_string();
        } else if line.starts_with("  ANCHOR=") {
            anchors.insert(line.trim_start().replace("ANCHOR=", ""));
        } else if line.starts_with("TOKEN_FREQUENCY_TABLE") {
            in_table = true;
        } else if in_table && line.starts_with("  ") {
            let parts: Vec<&str> = line.trim().splitn(2, '\t').collect();
            if parts.len() == 2 {
                let token = parts[0].trim();
                let freq: i64 = parts[1].trim().parse().unwrap_or(0);
                let is_anchor = anchors.contains(token);
                sql.push(format!(
                    "INSERT INTO sagco_token_frequencies (token, frequency, source_file, is_anchor, dna) VALUES ({}, {}, {}, {}, {});",
                    sql_str(token),
                    freq,
                    sql_str(&source),
                    if is_anchor { "TRUE" } else { "FALSE" },
                    sql_str(DNA),
                ));
            }
        }
    }

    sql
}

// ─── main ─────────────────────────────────────────────────────────────────────

fn main() {
    let args: Vec<String> = env::args().collect();

    let mode_topology = args.iter().any(|a| a == "--topology");
    let mode_events   = args.iter().any(|a| a == "--events");
    let mode_tokens   = args.iter().any(|a| a == "--tokens");
    // default mode: evidence
    let mode_evidence = !mode_topology && !mode_events && !mode_tokens
        || args.iter().any(|a| a == "--evidence");
    let dry_run       = args.iter().any(|a| a == "--dry-run");

    // read all stdin
    let stdin = io::stdin();
    let lines: Vec<String> = stdin.lock().lines()
        .filter_map(|l| l.ok())
        .collect();

    if lines.is_empty() {
        eprintln!("sagco-persist: no input — pipe sagco-evidence, sagco-topology --json, sagco-tokenize, or sagco-core output");
        process::exit(1);
    }

    let sql_stmts: Vec<String> = if mode_topology {
        parse_topology(&lines)
    } else if mode_events {
        parse_events(&lines)
    } else if mode_tokens {
        parse_tokens(&lines)
    } else if mode_evidence {
        parse_evidence(&lines)
    } else {
        Vec::new()
    };

    if sql_stmts.is_empty() {
        eprintln!("sagco-persist: no SQL generated — check input format or mode flag");
        process::exit(1);
    }

    // emit a transaction so all-or-nothing
    let output = format!(
        "-- sagco-persist output | DNA={} | {} statements\nBEGIN;\n{}\nCOMMIT;\n",
        DNA,
        sql_stmts.len(),
        sql_stmts.join("\n")
    );

    if dry_run {
        eprintln!("{}", output);
    } else {
        print!("{}", output);
    }
}
