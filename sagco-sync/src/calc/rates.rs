use crate::ingest::ra_sheet::RASheet;

pub struct CutWeight {
    pub cut_id: String,
    pub lnf: f64,
    pub estimate_hrs: f64,
    /// E_hrs / LNF
    pub implied_rate: f64,
    /// implied_rate / avg_rate
    pub weight: f64,
}

pub struct DifficultyWeights {
    pub cuts: Vec<CutWeight>,
    pub avg_rate: f64,
}

pub fn extract_weights(ra: &RASheet) -> DifficultyWeights {
    // Collect all cuts with non-zero LNF
    let raw: Vec<(String, f64, f64, f64)> = ra
        .circuits
        .iter()
        .flat_map(|circ| {
            circ.cuts.iter().map(move |cut| {
                let rate = cut.implied_rate();
                (cut.id.clone(), cut.lnf_total, cut.estimate_hrs, rate)
            })
        })
        .filter(|(_, lnf, _, _)| *lnf > 0.0)
        .collect();

    let total_lnf: f64 = raw.iter().map(|(_, lnf, _, _)| lnf).sum();
    let avg_rate = if total_lnf == 0.0 {
        1.0
    } else {
        raw.iter().map(|(_, _, est, _)| est).sum::<f64>() / total_lnf
    };

    let cuts = raw
        .into_iter()
        .map(|(cut_id, lnf, estimate_hrs, implied_rate)| {
            let weight = if avg_rate == 0.0 { 1.0 } else { implied_rate / avg_rate };
            CutWeight { cut_id, lnf, estimate_hrs, implied_rate, weight }
        })
        .collect();

    DifficultyWeights { cuts, avg_rate }
}

/// Difficulty-Adjusted % = Σ(done_LNF × weight) / Σ(all_LNF × weight)
pub fn difficulty_adjusted_pct(ra: &RASheet, weights: &DifficultyWeights) -> f64 {
    // Build a quick lookup: cut_id → (done_lnf, total_lnf, weight)
    // We need lnf_done per cut — iterate circuits
    let mut done_by_id: std::collections::HashMap<&str, f64> = std::collections::HashMap::new();
    for circ in &ra.circuits {
        for cut in &circ.cuts {
            done_by_id.insert(cut.id.as_str(), cut.lnf_done);
        }
    }

    let mut numerator = 0.0_f64;
    let mut denominator = 0.0_f64;
    for cw in &weights.cuts {
        let done = done_by_id.get(cw.cut_id.as_str()).copied().unwrap_or(0.0);
        numerator += done * cw.weight;
        denominator += cw.lnf * cw.weight;
    }

    if denominator == 0.0 { 0.0 } else { numerator / denominator }
}
