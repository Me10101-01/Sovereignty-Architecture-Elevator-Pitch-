// sagco-observe — artifact observation pass
// Usage: sagco-observe <file>
// License: SSL-1.0 — Strategickhaos DAO LLC
use sagco_core::crypto::sha256_hex;
use std::{env, fs, process};

fn detect_format(magic: &[u8], name: &str) -> &'static str {
    match magic {
        [0x25, 0x50, 0x44, 0x46, ..] => "PDF",
        [0x50, 0x4B, 0x03, 0x04, ..] => "ZIP/DOCX/XLSX",
        [0x50, 0x4B, 0x05, 0x06, ..] => "ZIP_EMPTY",
        [0xD0, 0xCF, 0x11, 0xE0, ..] => "OLE2/DOC/XLS",
        [0x1F, 0x8B, ..] => "GZIP",
        _ if name.ends_with(".md") || name.ends_with(".txt") => "PLAINTEXT",
        _ if name.ends_with(".json") => "JSON",
        _ if name.ends_with(".yaml") || name.ends_with(".yml") => "YAML",
        _ if name.ends_with(".rs") => "RUST_SOURCE",
        _ => "BINARY",
    }
}

fn readable_ratio(data: &[u8]) -> f64 {
    if data.is_empty() { return 0.0; }
    let sample = &data[..data.len().min(4096)];
    let readable = sample.iter().filter(|&&b| b >= 0x20 && b < 0x7F || b == b'\n' || b == b'\r').count();
    readable as f64 / sample.len() as f64
}

fn extract_text_sample(data: &[u8], fmt: &str) -> String {
    match fmt {
        "PLAINTEXT" | "JSON" | "YAML" | "RUST_SOURCE" => {
            String::from_utf8_lossy(&data[..data.len().min(512)])
                .lines()
                .take(5)
                .collect::<Vec<_>>()
                .join(" | ")
        }
        "PDF" => {
            // scan for text between BT...ET markers (basic PDF text extraction)
            let text = String::from_utf8_lossy(data);
            let mut out = Vec::new();
            let mut in_text = false;
            for line in text.lines() {
                if line.contains("BT") { in_text = true; }
                if in_text {
                    // extract strings in parentheses: (Hello World)
                    let mut i = 0;
                    let bytes = line.as_bytes();
                    while i < bytes.len() {
                        if bytes[i] == b'(' {
                            let end = bytes[i+1..].iter().position(|&b| b == b')').unwrap_or(0);
                            let s = &line[i+1..i+1+end];
                            if s.chars().all(|c| c.is_ascii_graphic() || c == ' ') && s.len() > 2 {
                                out.push(s.to_string());
                            }
                            i += end + 2;
                        } else { i += 1; }
                    }
                }
                if line.contains("ET") { in_text = false; }
                if out.len() > 12 { break; }
            }
            out.join(" ")
        }
        _ => {
            // printable ASCII run extraction
            let mut runs = Vec::new();
            let mut current = Vec::new();
            for &b in data.iter().take(8192) {
                if b >= 0x20 && b < 0x7F {
                    current.push(b);
                } else if current.len() >= 6 {
                    runs.push(String::from_utf8_lossy(&current).to_string());
                    current.clear();
                } else {
                    current.clear();
                }
            }
            runs.into_iter().take(8).collect::<Vec<_>>().join(" | ")
        }
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: sagco-observe <file>");
        process::exit(1);
    }
    let path = &args[1];
    let data = match fs::read(path) {
        Ok(d) => d,
        Err(e) => {
            println!("OBSERVE_TARGET={}", path);
            println!("STATUS=PATH_DISCOVERY_ANTIBODY  error={}", e);
            process::exit(1);
        }
    };

    let name = std::path::Path::new(path)
        .file_name().unwrap_or_default()
        .to_string_lossy();
    let magic: &[u8] = if data.len() >= 4 { &data[..4] } else { &data };
    let fmt   = detect_format(magic, &name);
    let ratio = readable_ratio(&data);
    let sha   = sha256_hex(&data);
    let sample = extract_text_sample(&data, fmt);

    let magic_hex: String = data[..data.len().min(8)]
        .iter().map(|b| format!("{:02x}", b)).collect::<Vec<_>>().join(" ");

    println!("OBSERVE_TARGET={}", path);
    println!("FILE_SIZE_BYTES={}", data.len());
    println!("FILE_FORMAT={}", fmt);
    println!("MAGIC_BYTES={}", magic_hex);
    println!("READABLE_RATIO={:.4}", ratio);
    println!("SHA256={}", sha);
    println!("CONTENT_SAMPLE={}", sample);
    println!("DNA=a364ca9f90356c85");
    println!("STATUS=SAGCO_OBSERVE_PASS");
}
