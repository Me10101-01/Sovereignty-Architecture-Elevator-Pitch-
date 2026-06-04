use super::wafer::WaferRow;

#[derive(Debug)]
pub struct EruRecord {
    pub token_type: String,
    pub expected: String,
    pub actual: String,
    pub variance: i32,
    pub status: String,
}

impl EruRecord {
    pub fn new(token_type: &str, expected: &str, actual: &str, variance: i32) -> Self {
        let status = if variance == 0 {
            "GREEN".to_string()
        } else if variance.abs() <= 2 {
            "YELLOW".to_string()
        } else {
            "RED".to_string()
        };
        EruRecord {
            token_type: token_type.to_string(),
            expected: expected.to_string(),
            actual: actual.to_string(),
            variance,
            status,
        }
    }
}

/// One capture row from field_capture.csv
#[derive(Debug, Clone)]
pub struct CaptureRow {
    pub token_type: String,
    pub expected_value: String,
    pub actual_value: String,
}

pub fn load_captures(csv_content: &str, case_id: &str) -> Vec<CaptureRow> {
    csv_content
        .lines()
        .skip(1)
        .filter(|l| !l.trim().is_empty() && l.contains(case_id))
        .filter_map(|line| {
            let cols: Vec<&str> = line.split(',').collect();
            if cols.len() < 4 { return None; }
            Some(CaptureRow {
                token_type:     cols[1].trim().to_string(),
                expected_value: cols[2].trim().to_string(),
                actual_value:   cols[3].trim().to_string(),
            })
        })
        .collect()
}

/// Compute ERU variance records from wafer expected vs field captures
pub fn compute_eru(wafer: &[WaferRow], captures: &[CaptureRow]) -> Vec<EruRecord> {
    let mut records = Vec::new();

    // Orientation variance: compare degree values
    let wafer_orientations: Vec<i32> = wafer.iter().map(|r: &WaferRow| r.orientation_degrees()).collect();
    let cap_orientations: Vec<i32> = captures.iter()
        .filter(|c| c.token_type == "ORIENTATION")
        .map(|c| c.actual_value.chars().take_while(|ch| ch.is_ascii_digit())
            .collect::<String>().parse().unwrap_or(0))
        .collect();

    for (i, (exp, act)) in wafer_orientations.iter().zip(cap_orientations.iter()).enumerate() {
        records.push(EruRecord::new(
            &format!("ORIENTATION_{}", i + 1),
            &wafer[i].orientation,
            &captures.iter().filter(|c| c.token_type == "ORIENTATION").nth(i)
                .map(|c| c.actual_value.as_str()).unwrap_or("?"),
            act - exp,
        ));
    }

    // PIC variance: compare numbers
    let wafer_pics: Vec<i32> = wafer.iter().map(|r: &WaferRow| r.pic_number()).collect();
    let cap_pics: Vec<i32> = captures.iter()
        .filter(|c| c.token_type == "PIC")
        .map(|c| c.actual_value.chars().filter(|ch| ch.is_ascii_digit())
            .collect::<String>().parse().unwrap_or(0))
        .collect();

    for (i, (exp, act)) in wafer_pics.iter().zip(cap_pics.iter()).enumerate() {
        records.push(EruRecord::new(
            &format!("PIC_{}", i + 1),
            &wafer[i].pid,
            &captures.iter().filter(|c| c.token_type == "PIC").nth(i)
                .map(|c| c.actual_value.as_str()).unwrap_or("?"),
            act - exp,
        ));
    }

    // WTS variance
    let wafer_wts: Vec<i32> = wafer.iter().map(|r: &WaferRow| r.wts_number()).collect();
    let cap_wts: Vec<i32> = captures.iter()
        .filter(|c| c.token_type == "WTS")
        .map(|c| c.actual_value.chars().filter(|ch| ch.is_ascii_digit())
            .collect::<String>().parse().unwrap_or(0))
        .collect();

    for (i, (exp, act)) in wafer_wts.iter().zip(cap_wts.iter()).enumerate() {
        records.push(EruRecord::new(
            &format!("WTS_{}", i + 1),
            &wafer[i].wts,
            &captures.iter().filter(|c| c.token_type == "WTS").nth(i)
                .map(|c| c.actual_value.as_str()).unwrap_or("?"),
            act - exp,
        ));
    }

    // FR variance
    let wafer_frs: Vec<i32> = wafer.iter().map(|r: &WaferRow| r.fr_number()).collect();
    let cap_frs: Vec<i32> = captures.iter()
        .filter(|c| c.token_type == "FR")
        .map(|c| c.actual_value.chars().filter(|ch| ch.is_ascii_digit())
            .collect::<String>().parse().unwrap_or(0))
        .collect();

    for (i, (exp, act)) in wafer_frs.iter().zip(cap_frs.iter()).enumerate() {
        records.push(EruRecord::new(
            &format!("FR_{}", i + 1),
            &wafer[i].fr,
            &captures.iter().filter(|c| c.token_type == "FR").nth(i)
                .map(|c| c.actual_value.as_str()).unwrap_or("?"),
            act - exp,
        ));
    }

    records
}
