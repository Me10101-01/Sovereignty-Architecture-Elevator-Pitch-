use std::collections::HashMap;
use crate::ingest::ra_sheet::{Cut, Circuit, RASheet};

pub fn load_csv(path: &str) -> Result<RASheet, String> {
    let mut rdr = csv::Reader::from_path(path)
        .map_err(|e| format!("Cannot open CSV '{}': {}", path, e))?;

    let headers = rdr
        .headers()
        .map_err(|e| format!("Cannot read CSV headers: {}", e))?
        .clone();

    // Map header names (lowercase) → column index
    let col: HashMap<String, usize> = headers
        .iter()
        .enumerate()
        .map(|(i, h)| (h.trim().to_lowercase(), i))
        .collect();

    let get = |record: &csv::StringRecord, name: &str| -> String {
        col.get(name)
            .and_then(|&i| record.get(i))
            .unwrap_or("")
            .trim()
            .to_string()
    };

    let get_f64 = |record: &csv::StringRecord, name: &str| -> f64 {
        get(record, name).parse().unwrap_or(0.0)
    };

    let get_u32 = |record: &csv::StringRecord, name: &str| -> u32 {
        get(record, name).parse().unwrap_or(1)
    };

    let get_bool = |record: &csv::StringRecord, name: &str| -> bool {
        matches!(get(record, name).to_lowercase().as_str(), "yes" | "true" | "1")
    };

    // Group rows by circuit id preserving insertion order
    let mut circuit_order: Vec<String> = Vec::new();
    let mut circuit_map: HashMap<String, Vec<Cut>> = HashMap::new();

    for (row_idx, result) in rdr.records().enumerate() {
        let record = result.map_err(|e| format!("CSV row {} error: {}", row_idx + 2, e))?;

        let circuit_id = get(&record, "circuit");
        if circuit_id.is_empty() {
            continue;
        }

        let cut_id = get(&record, "cut");
        let cut = Cut {
            id: if cut_id.is_empty() {
                format!("{}", row_idx + 1)
            } else {
                cut_id
            },
            description: get(&record, "description"),
            cost_code: get(&record, "cost_code"),
            lnf_total: get_f64(&record, "lnf_total"),
            lnf_done: get_f64(&record, "lnf_done"),
            estimate_hrs: get_f64(&record, "estimate_hrs"),
            used_hrs: get_f64(&record, "used_hrs"),
            elevation_ft: get_f64(&record, "elevation_ft"),
            bands: get_u32(&record, "bands"),
            metal: get_bool(&record, "metal"),
            access: get(&record, "access"),
        };

        if !circuit_map.contains_key(&circuit_id) {
            circuit_order.push(circuit_id.clone());
            circuit_map.insert(circuit_id.clone(), Vec::new());
        }
        circuit_map.get_mut(&circuit_id).unwrap().push(cut);
    }

    let circuits: Vec<Circuit> = circuit_order
        .into_iter()
        .map(|id| Circuit {
            cuts: circuit_map.remove(&id).unwrap_or_default(),
            id,
        })
        .collect();

    // Project name = filename stem
    let project_name = std::path::Path::new(path)
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("Unknown")
        .to_string();

    Ok(RASheet { project_name, circuits })
}

pub fn load_demo() -> RASheet {
    RASheet {
        project_name: "Stratford-Job-1".to_string(),
        circuits: vec![
            Circuit {
                id: "E-1706-NA-1A".to_string(),
                cuts: vec![
                    Cut {
                        id: "1".to_string(),
                        description: "Main run south wall".to_string(),
                        cost_code: "MC-001".to_string(),
                        lnf_total: 46.0,
                        lnf_done: 18.0,
                        estimate_hrs: 280.0,
                        used_hrs: 40.0,
                        elevation_ft: 0.0,
                        bands: 1,
                        metal: false,
                        access: "ground".to_string(),
                    },
                    Cut {
                        id: "2".to_string(),
                        description: "High-bay ladder run".to_string(),
                        cost_code: "MC-002".to_string(),
                        lnf_total: 30.0,
                        lnf_done: 30.0,
                        estimate_hrs: 210.0,
                        used_hrs: 427.5,
                        elevation_ft: 15.0,
                        bands: 2,
                        metal: true,
                        access: "ladder".to_string(),
                    },
                ],
            },
            Circuit {
                id: "E-1706-NA-2A".to_string(),
                cuts: vec![
                    Cut {
                        id: "1".to_string(),
                        description: "Roof-level rope access run".to_string(),
                        cost_code: "MC-003".to_string(),
                        lnf_total: 120.0,
                        lnf_done: 120.0,
                        estimate_hrs: 491.0,
                        used_hrs: 1020.3,
                        elevation_ft: 45.0,
                        bands: 3,
                        metal: true,
                        access: "rope".to_string(),
                    },
                ],
            },
            Circuit {
                id: "E-1706-NA-3A".to_string(),
                cuts: vec![
                    Cut {
                        id: "1".to_string(),
                        description: "Ground-level conduit run".to_string(),
                        cost_code: "MC-004".to_string(),
                        lnf_total: 80.0,
                        lnf_done: 40.0,
                        estimate_hrs: 1080.0,
                        used_hrs: 579.2,
                        elevation_ft: 0.0,
                        bands: 1,
                        metal: false,
                        access: "ground".to_string(),
                    },
                ],
            },
        ],
    }
}
