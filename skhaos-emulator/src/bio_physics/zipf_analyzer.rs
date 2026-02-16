// Zipf's Law Analyzer for Whale and Dolphin Communication Patterns
// 
// Implements Zipf's law: frequency ~ 1/rank^α (where α ≈ 1)
// Applied to humpback whale songs, dolphin whistles, and MIDI patterns
//
// Key concepts:
// - Frequent short units rank high (Menzerath's brevity law)
// - Cultural evolution for learnability
// - Entropy minimization through efficient encoding

use std::collections::HashMap;

/// Zipf distribution analyzer for bio-patterns
pub struct ZipfAnalyzer {
    /// Maps units (phrases, motifs) to their frequencies
    frequency_map: HashMap<String, usize>,
    /// Cached Zipf ranks
    rank_cache: Vec<(String, f64)>,
    /// Zipf exponent (typically ~1.0)
    alpha: f64,
}

impl ZipfAnalyzer {
    pub fn new() -> Self {
        ZipfAnalyzer {
            frequency_map: HashMap::new(),
            rank_cache: Vec::new(),
            alpha: 1.0,
        }
    }

    /// Set custom Zipf exponent
    pub fn with_alpha(mut self, alpha: f64) -> Self {
        self.alpha = alpha;
        self
    }

    /// Add a unit (phrase, motif, note sequence) to the analyzer
    pub fn add_unit(&mut self, unit: &str) {
        *self.frequency_map.entry(unit.to_string()).or_insert(0) += 1;
        self.invalidate_cache();
    }

    /// Analyze multiple units at once
    pub fn add_units(&mut self, units: &[&str]) {
        for unit in units {
            self.add_unit(unit);
        }
    }

    /// Calculate Zipf ranks for all units
    pub fn calculate_ranks(&mut self) -> &[(String, f64)] {
        if !self.rank_cache.is_empty() {
            return &self.rank_cache;
        }

        // Sort by frequency (descending)
        let mut sorted: Vec<_> = self.frequency_map.iter().collect();
        sorted.sort_by(|a, b| b.1.cmp(a.1));

        // Calculate Zipf ranks: frequency ~ 1/rank^α
        let mut ranks = Vec::new();
        for (rank, (unit, freq)) in sorted.iter().enumerate() {
            let rank_value = (rank + 1) as f64;
            let zipf_score = *freq as f64 / rank_value.powf(self.alpha);
            ranks.push((unit.to_string(), zipf_score));
        }

        self.rank_cache = ranks;
        &self.rank_cache
    }

    /// Get rank of a specific unit
    pub fn get_rank(&mut self, unit: &str) -> Option<f64> {
        self.calculate_ranks();
        self.rank_cache
            .iter()
            .find(|(u, _)| u == unit)
            .map(|(_, rank)| *rank)
    }

    /// Get frequency distribution (for plotting/analysis)
    pub fn get_distribution(&self) -> Vec<(String, usize)> {
        let mut dist: Vec<_> = self.frequency_map.iter()
            .map(|(k, v)| (k.clone(), *v))
            .collect();
        dist.sort_by(|a, b| b.1.cmp(&a.1));
        dist
    }

    /// Calculate entropy of the distribution
    /// H = -Σ p(x) * log(p(x))
    pub fn calculate_entropy(&self) -> f64 {
        let total: usize = self.frequency_map.values().sum();
        if total == 0 {
            return 0.0;
        }

        let mut entropy = 0.0;
        for count in self.frequency_map.values() {
            if *count > 0 {
                let p = *count as f64 / total as f64;
                entropy -= p * p.ln();
            }
        }
        entropy
    }

    /// Check if distribution follows Zipf's law (goodness of fit)
    /// Returns R² correlation coefficient
    pub fn zipf_goodness_of_fit(&mut self) -> f64 {
        let ranks = self.calculate_ranks();
        if ranks.len() < 2 {
            return 0.0;
        }

        // Calculate expected vs actual frequencies
        let mut sum_sq_diff = 0.0;
        let mut sum_sq_total = 0.0;
        let mean: f64 = ranks.iter().map(|(_, r)| r).sum::<f64>() / ranks.len() as f64;

        for (i, (_, actual)) in ranks.iter().enumerate() {
            let expected = 1.0 / (i + 1) as f64;
            sum_sq_diff += (actual - expected).powi(2);
            sum_sq_total += (actual - mean).powi(2);
        }

        if sum_sq_total == 0.0 {
            return 0.0;
        }

        1.0 - (sum_sq_diff / sum_sq_total)
    }

    /// Analyze whale song units (humpback example)
    pub fn analyze_whale_song(&mut self, song_units: &[&str]) -> WhaleAnalysis {
        self.add_units(song_units);
        let ranks = self.calculate_ranks();
        
        WhaleAnalysis {
            total_units: song_units.len(),
            unique_units: self.frequency_map.len(),
            entropy: self.calculate_entropy(),
            zipf_fit: self.zipf_goodness_of_fit(),
            top_units: ranks.iter().take(5).map(|(u, r)| (u.clone(), *r)).collect(),
        }
    }

    /// Analyze dolphin communication patterns
    pub fn analyze_dolphin_comm(&mut self, whistles: &[&str]) -> DolphinAnalysis {
        self.add_units(whistles);
        let ranks = self.calculate_ranks();
        
        DolphinAnalysis {
            total_whistles: whistles.len(),
            unique_signatures: self.frequency_map.len(),
            entropy: self.calculate_entropy(),
            signature_ranks: ranks.iter().take(10).map(|(u, r)| (u.clone(), *r)).collect(),
        }
    }

    fn invalidate_cache(&mut self) {
        self.rank_cache.clear();
    }
}

#[derive(Debug)]
pub struct WhaleAnalysis {
    pub total_units: usize,
    pub unique_units: usize,
    pub entropy: f64,
    pub zipf_fit: f64,
    pub top_units: Vec<(String, f64)>,
}

#[derive(Debug)]
pub struct DolphinAnalysis {
    pub total_whistles: usize,
    pub unique_signatures: usize,
    pub entropy: f64,
    pub signature_ranks: Vec<(String, f64)>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_zipf_analyzer_basic() {
        let mut analyzer = ZipfAnalyzer::new();
        analyzer.add_unit("moan");
        analyzer.add_unit("moan");
        analyzer.add_unit("cry");
        
        let ranks = analyzer.calculate_ranks();
        assert_eq!(ranks.len(), 2);
        assert!(ranks[0].1 > ranks[1].1); // Most frequent should rank higher
    }

    #[test]
    fn test_entropy_calculation() {
        let mut analyzer = ZipfAnalyzer::new();
        analyzer.add_units(&["a", "a", "a", "b"]);
        let entropy = analyzer.calculate_entropy();
        assert!(entropy > 0.0);
    }

    #[test]
    fn test_whale_song_analysis() {
        let mut analyzer = ZipfAnalyzer::new();
        let song = vec!["moan", "moan", "moan", "cry", "cry", "grumble"];
        let analysis = analyzer.analyze_whale_song(&song);
        
        assert_eq!(analysis.total_units, 6);
        assert_eq!(analysis.unique_units, 3);
        assert!(analysis.entropy > 0.0);
    }

    #[test]
    fn test_dolphin_comm_analysis() {
        let mut analyzer = ZipfAnalyzer::new();
        let whistles = vec!["sig_alpha", "sig_alpha", "sig_beta", "sig_gamma"];
        let analysis = analyzer.analyze_dolphin_comm(&whistles);
        
        assert_eq!(analysis.total_whistles, 4);
        assert_eq!(analysis.unique_signatures, 3);
    }
}
