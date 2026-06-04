/// One row from the Excel wafer CSV export
#[derive(Debug, Clone)]
pub struct WaferRow {
    pub pipe_rack: String,
    pub usc: String,
    pub orientation: String,
    pub circuit: String,
    pub pid: String,
    pub wts: String,
    pub fr: String,
}

impl WaferRow {
    /// Parse a CSV line into a WaferRow (skips header)
    pub fn from_csv_line(line: &str) -> Option<Self> {
        let cols: Vec<&str> = line.split(',').collect();
        if cols.len() < 8 { return None; }
        Some(WaferRow {
            pipe_rack:   cols[0].trim().to_string(),
            usc:         cols[1].trim().to_string(),
            orientation: cols[2].trim().to_string(),
            circuit:     cols[3].trim().to_string(),
            pid:         cols[4].trim().to_string(),
            wts:         cols[5].trim().to_string(),
            fr:          cols[7].trim().to_string(),
        })
    }

    /// Extract numeric degrees from orientation string e.g. "108E" → 108
    pub fn orientation_degrees(&self) -> i32 {
        self.orientation
            .chars()
            .take_while(|c| c.is_ascii_digit())
            .collect::<String>()
            .parse()
            .unwrap_or(0)
    }

    /// Extract numeric part from PIC string e.g. "PIC1" → 1
    pub fn pic_number(&self) -> i32 {
        self.pid
            .chars()
            .filter(|c| c.is_ascii_digit())
            .collect::<String>()
            .parse()
            .unwrap_or(0)
    }

    /// Extract numeric part from WTS string e.g. "WTS11" → 11
    pub fn wts_number(&self) -> i32 {
        self.wts
            .chars()
            .filter(|c| c.is_ascii_digit())
            .collect::<String>()
            .parse()
            .unwrap_or(0)
    }

    /// Extract numeric part from FR string e.g. "FR-32" → 32
    pub fn fr_number(&self) -> i32 {
        self.fr
            .chars()
            .filter(|c| c.is_ascii_digit())
            .collect::<String>()
            .parse()
            .unwrap_or(0)
    }
}

pub fn load_wafer(csv_content: &str) -> Vec<WaferRow> {
    csv_content
        .lines()
        .skip(1)                            // skip header
        .filter(|l| !l.trim().is_empty())
        .filter_map(WaferRow::from_csv_line)
        .collect()
}
