/// Antibody layer — brick 7.
///
/// Detects bad schema, corrupt pages, slow scans, and abnormal patterns.
/// Emits a diagnosis + optional heal action.

use std::io;
use std::path::Path;
use std::fs;

use crate::cell::Cell;
use crate::storage::{StorageEngine, PAGE_HEADER_SIZE};

#[derive(Debug, Clone, PartialEq)]
pub enum AntibodyStatus {
    Healthy,
    Warning(String),
    Critical(String),
}

#[derive(Debug, Clone)]
pub struct Diagnosis {
    pub check: &'static str,
    pub status: AntibodyStatus,
}

impl Diagnosis {
    fn ok(check: &'static str) -> Self {
        Self { check, status: AntibodyStatus::Healthy }
    }
    fn warn(check: &'static str, msg: impl Into<String>) -> Self {
        Self { check, status: AntibodyStatus::Warning(msg.into()) }
    }
    fn critical(check: &'static str, msg: impl Into<String>) -> Self {
        Self { check, status: AntibodyStatus::Critical(msg.into()) }
    }
}

/// Run all antibody checks on a table. Returns list of diagnoses.
pub fn run(engine: &StorageEngine, table: &str) -> io::Result<Vec<Diagnosis>> {
    let mut checks: Vec<Diagnosis> = vec![];

    // 1. Page file exists
    let page_path = engine.pages_dir.join(format!("{}.sagco", table));
    if !page_path.exists() {
        checks.push(Diagnosis::critical("page_exists", format!("no page file for table {:?}", table)));
        return Ok(checks);
    }
    checks.push(Diagnosis::ok("page_exists"));

    // 2. Page file readable (header check)
    let header = engine.page_header(table)?;
    match header {
        None => {
            checks.push(Diagnosis::critical("page_readable", "page header missing or corrupt"));
            return Ok(checks);
        }
        Some(h) => {
            checks.push(Diagnosis::ok("page_readable"));

            // 3. Table name matches
            if h.table != table {
                checks.push(Diagnosis::warn(
                    "table_name_match",
                    format!("page says {:?} but we requested {:?}", h.table, table),
                ));
            } else {
                checks.push(Diagnosis::ok("table_name_match"));
            }
        }
    }

    // 4. Scan for corrupt cells — count errors
    let mut total = 0usize;
    let mut corrupt = 0usize;
    let mut deleted = 0usize;
    let mut max_value_kb: f64 = 0.0;

    use std::fs::File;
    use std::io::{BufReader, Read};
    use crate::storage::PageHeader;
    use crate::cell::Cell;

    {
        let f = File::open(&page_path)?;
        let mut r = BufReader::new(f);
        PageHeader::read_from(&mut r)?; // skip header

        loop {
            match Cell::read_from(&mut r) {
                Ok(Some(cell)) => {
                    total += 1;
                    if cell.is_deleted() { deleted += 1; }
                    let vkb = cell.value.len() as f64 / 1024.0;
                    if vkb > max_value_kb { max_value_kb = vkb; }
                }
                Ok(None) => break,
                Err(_) => {
                    corrupt += 1;
                    break; // can't continue reliably after corrupt cell
                }
            }
        }
    }

    if corrupt > 0 {
        checks.push(Diagnosis::critical(
            "cell_integrity",
            format!("{} corrupt cell(s) found — compact recommended", corrupt),
        ));
    } else {
        checks.push(Diagnosis::ok("cell_integrity"));
    }

    // 5. Tombstone ratio
    if total > 0 {
        let dead_ratio = deleted as f64 / total as f64;
        if dead_ratio > 0.5 {
            checks.push(Diagnosis::warn(
                "tombstone_ratio",
                format!("{:.0}% tombstones — run sagco db compact {}", dead_ratio * 100.0, table),
            ));
        } else {
            checks.push(Diagnosis::ok("tombstone_ratio"));
        }
    }

    // 6. Huge value warning (values > 256KB suggest misuse)
    if max_value_kb > 256.0 {
        checks.push(Diagnosis::warn(
            "value_size",
            format!("max value {:.1}KB — consider storing large blobs as file references", max_value_kb),
        ));
    } else {
        checks.push(Diagnosis::ok("value_size"));
    }

    // 7. Page file size sanity
    let file_size = fs::metadata(&page_path)?.len();
    let expected_min = PAGE_HEADER_SIZE as u64;
    if file_size < expected_min {
        checks.push(Diagnosis::critical(
            "page_size",
            format!("page file only {} bytes — truncated?", file_size),
        ));
    } else {
        checks.push(Diagnosis::ok("page_size"));
    }

    Ok(checks)
}

pub fn print_diagnosis(table: &str, checks: &[Diagnosis]) {
    let critical = checks.iter().filter(|d| matches!(d.status, AntibodyStatus::Critical(_))).count();
    let warnings = checks.iter().filter(|d| matches!(d.status, AntibodyStatus::Warning(_))).count();
    let healthy  = checks.iter().filter(|d| d.status == AntibodyStatus::Healthy).count();

    let overall = if critical > 0 { "CRITICAL" } else if warnings > 0 { "WARNING" } else { "HEALTHY" };

    println!("\n  Antibody Report — table: {}", table);
    println!("  Overall: {}  ({} ok / {} warn / {} critical)", overall, healthy, warnings, critical);
    println!("  {}", "─".repeat(50));
    for d in checks {
        let icon = match &d.status {
            AntibodyStatus::Healthy       => "✓",
            AntibodyStatus::Warning(_)    => "~",
            AntibodyStatus::Critical(_)   => "✗",
        };
        let msg = match &d.status {
            AntibodyStatus::Healthy        => String::new(),
            AntibodyStatus::Warning(m)
            | AntibodyStatus::Critical(m)  => format!("  {}", m),
        };
        println!("  {} {:25}  {}", icon, d.check, msg);
    }
    println!();
}
