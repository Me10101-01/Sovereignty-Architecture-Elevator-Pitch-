// sagco-binscan — binary structure analysis and entropy probe
// Usage: sagco-binscan <file>
// License: SSL-1.0 — Strategickhaos DAO LLC
use sagco_core::crypto::sha256_hex;
use std::{env, fs, process};

fn shannon_entropy(data: &[u8]) -> f64 {
    if data.is_empty() { return 0.0; }
    let mut counts = [0usize; 256];
    for &b in data { counts[b as usize] += 1; }
    let len = data.len() as f64;
    counts.iter()
        .filter(|&&c| c > 0)
        .map(|&c| { let p = c as f64 / len; -p * p.log2() })
        .sum()
}

fn detect_zip_entries(data: &[u8]) -> Vec<String> {
    // ZIP local file header: PK\x03\x04 followed by filename at offset 30
    let sig = [0x50u8, 0x4B, 0x03, 0x04];
    let mut entries = Vec::new();
    let mut i = 0;
    while i + 30 < data.len() {
        if data[i..i+4] == sig {
            let name_len = u16::from_le_bytes([data[i+26], data[i+27]]) as usize;
            let extra_len = u16::from_le_bytes([data[i+28], data[i+29]]) as usize;
            if i + 30 + name_len <= data.len() {
                let name = String::from_utf8_lossy(&data[i+30..i+30+name_len]);
                entries.push(name.to_string());
            }
            // advance past this entry header
            let compressed_size = u32::from_le_bytes([data[i+18],data[i+19],data[i+20],data[i+21]]) as usize;
            i += 30 + name_len + extra_len + compressed_size.min(data.len() - i - 30);
        } else {
            i += 1;
        }
    }
    entries.truncate(20);
    entries
}

fn classify_entropy(e: f64) -> &'static str {
    match e as u32 {
        0..=2 => "SPARSE — likely mostly zeros or padding",
        3..=5 => "NORMAL — typical document or source text",
        6     => "DENSE  — compressed or encrypted sections present",
        _     => "MAXIMAL — likely encrypted, compressed, or random",
    }
}

fn structural_markers(data: &[u8]) -> Vec<String> {
    let mut marks = Vec::new();
    let s = String::from_utf8_lossy(data);

    if s.contains("%%EOF")         { marks.push("PDF_EOF_MARKER".into()); }
    if s.contains("/Type /Page")   { marks.push("PDF_PAGE_TREE".into()); }
    if s.contains("word/document") { marks.push("DOCX_WORD_XML".into()); }
    if s.contains("[Content_Types]") { marks.push("OOXML_CONTENT_TYPES".into()); }
    if s.contains("<?xml")        { marks.push("XML_DECLARATION".into()); }
    if s.contains("# ")           { marks.push("MARKDOWN_HEADERS".into()); }
    if s.contains("fn ")          { marks.push("RUST_FUNCTION_DECL".into()); }
    if s.contains("struct ")      { marks.push("RUST_STRUCT_DECL".into()); }
    if s.contains("SAGCO")        { marks.push("SAGCO_DNA_PRESENT".into()); }
    marks
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: sagco-binscan <file>");
        process::exit(1);
    }
    let path = &args[1];
    let data = match fs::read(path) {
        Ok(d) => d,
        Err(e) => {
            println!("BINSCAN_TARGET={}", path);
            println!("STATUS=PATH_DISCOVERY_ANTIBODY  error={}", e);
            process::exit(1);
        }
    };

    let sha      = sha256_hex(&data);
    let entropy  = shannon_entropy(&data);
    let markers  = structural_markers(&data);

    let magic_hex: String = data[..data.len().min(8)]
        .iter().map(|b| format!("{:02x}", b)).collect::<Vec<_>>().join(" ");
    let magic_str: String = data[..data.len().min(4)]
        .iter().map(|&b| if b >= 0x20 && b < 0x7F { b as char } else { '.' })
        .collect();

    let zip_entries = detect_zip_entries(&data);

    println!("BINSCAN_TARGET={}", path);
    println!("FILE_SIZE_BYTES={}", data.len());
    println!("MAGIC_HEX={}", magic_hex);
    println!("MAGIC_ASCII={}", magic_str);
    println!("SHA256={}", sha);
    println!("ENTROPY={:.4}  ({})", entropy, classify_entropy(entropy));
    println!();
    println!("STRUCTURAL_MARKERS={}", if markers.is_empty() { "none".into() } else { markers.join(", ") });
    if !zip_entries.is_empty() {
        println!();
        println!("EMBEDDED_FILES={}", zip_entries.len());
        for e in &zip_entries { println!("  ENTRY={}", e); }
    }
    println!();
    println!("DNA=a364ca9f90356c85");
    println!("STATUS=SAGCO_BINSCAN_PASS");
}
