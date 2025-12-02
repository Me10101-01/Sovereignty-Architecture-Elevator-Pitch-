//! Lease Churn Analyzer
//!
//! Analyzes lease activity patterns to detect abnormal churn,
//! leader election issues, and coordination problems.

use std::collections::HashMap;

/// Represents a lease event for analysis
#[derive(Debug, Clone)]
pub struct LeaseEvent {
    pub timestamp: String,
    pub namespace: String,
    pub lease_name: String,
    pub action: LeaseAction,
    pub holder: Option<String>,
    pub duration_ms: u64,
}

/// Types of lease actions
#[derive(Debug, Clone, PartialEq)]
pub enum LeaseAction {
    Acquire,
    Renew,
    Release,
    Expire,
}

/// Detected anomaly in lease patterns
#[derive(Debug, Clone)]
pub struct ChurnAnomaly {
    pub anomaly_type: AnomalyType,
    pub namespace: String,
    pub lease_name: String,
    pub severity: Severity,
    pub details: String,
    pub start_time: String,
    pub end_time: String,
    pub event_count: usize,
}

/// Types of churn anomalies
#[derive(Debug, Clone, PartialEq)]
pub enum AnomalyType {
    /// Rapid acquire/release cycles
    HighChurn,
    /// Multiple holders competing
    SplitBrain,
    /// Lease never renewed
    AbandonedLease,
    /// Renewals faster than expected
    AggressiveRenewal,
}

/// Severity levels for anomalies
#[derive(Debug, Clone, PartialEq)]
pub enum Severity {
    Low,
    Medium,
    High,
    Critical,
}

/// Configuration for the churn analyzer
#[derive(Debug, Clone)]
pub struct AnalyzerConfig {
    /// Window size for churn detection in seconds
    pub churn_window_secs: u64,
    /// Threshold for high churn (events per window)
    pub churn_threshold: usize,
    /// Expected renewal interval in seconds
    pub expected_renewal_secs: u64,
    /// Threshold for abandoned lease detection in seconds
    pub abandon_threshold_secs: u64,
}

impl Default for AnalyzerConfig {
    fn default() -> Self {
        Self {
            churn_window_secs: 60,
            churn_threshold: 10,
            expected_renewal_secs: 15,
            abandon_threshold_secs: 300,
        }
    }
}

/// Analyzer for detecting lease churn patterns
pub struct LeaseChurnAnalyzer {
    config: AnalyzerConfig,
    events: Vec<LeaseEvent>,
}

impl LeaseChurnAnalyzer {
    /// Create a new analyzer with default configuration
    pub fn new() -> Self {
        Self {
            config: AnalyzerConfig::default(),
            events: Vec::new(),
        }
    }

    /// Create analyzer with custom configuration
    pub fn with_config(config: AnalyzerConfig) -> Self {
        Self {
            config,
            events: Vec::new(),
        }
    }

    /// Load events for analysis
    pub fn load_events(&mut self, events: Vec<LeaseEvent>) {
        self.events = events;
        // Sort by timestamp for analysis
        self.events.sort_by(|a, b| a.timestamp.cmp(&b.timestamp));
    }

    /// Run all anomaly detection algorithms
    pub fn analyze(&self) -> Vec<ChurnAnomaly> {
        let mut anomalies = Vec::new();
        
        anomalies.extend(self.detect_high_churn());
        anomalies.extend(self.detect_split_brain());
        anomalies.extend(self.detect_abandoned_leases());
        
        anomalies
    }

    /// Detect high churn patterns (rapid acquire/release)
    fn detect_high_churn(&self) -> Vec<ChurnAnomaly> {
        let mut anomalies = Vec::new();
        
        // Group events by namespace/lease
        let grouped = self.group_by_lease();
        
        for ((namespace, lease_name), events) in grouped {
            // Sliding window analysis
            let window_size = self.config.churn_window_secs;
            let threshold = self.config.churn_threshold;
            
            // TODO: Implement sliding window with actual timestamp parsing
            // For now, check total events against threshold
            if events.len() > threshold * 10 {
                anomalies.push(ChurnAnomaly {
                    anomaly_type: AnomalyType::HighChurn,
                    namespace: namespace.clone(),
                    lease_name: lease_name.clone(),
                    severity: Severity::High,
                    details: format!(
                        "{} events detected (threshold: {} per {}s window)",
                        events.len(), threshold, window_size
                    ),
                    start_time: events.first().map(|e| e.timestamp.clone()).unwrap_or_default(),
                    end_time: events.last().map(|e| e.timestamp.clone()).unwrap_or_default(),
                    event_count: events.len(),
                });
            }
        }
        
        anomalies
    }

    /// Detect split-brain scenarios (multiple holders)
    fn detect_split_brain(&self) -> Vec<ChurnAnomaly> {
        let mut anomalies = Vec::new();
        
        let grouped = self.group_by_lease();
        
        for ((namespace, lease_name), events) in grouped {
            // Find concurrent holders
            let holders: Vec<&str> = events.iter()
                .filter(|e| e.action == LeaseAction::Acquire)
                .filter_map(|e| e.holder.as_deref())
                .collect();
            
            // Check for multiple distinct holders in short time
            let unique_holders: std::collections::HashSet<_> = holders.iter().collect();
            if unique_holders.len() > 2 {
                anomalies.push(ChurnAnomaly {
                    anomaly_type: AnomalyType::SplitBrain,
                    namespace: namespace.clone(),
                    lease_name: lease_name.clone(),
                    severity: Severity::Critical,
                    details: format!(
                        "{} distinct holders detected: {:?}",
                        unique_holders.len(), unique_holders
                    ),
                    start_time: events.first().map(|e| e.timestamp.clone()).unwrap_or_default(),
                    end_time: events.last().map(|e| e.timestamp.clone()).unwrap_or_default(),
                    event_count: events.len(),
                });
            }
        }
        
        anomalies
    }

    /// Detect abandoned leases (no renewals)
    fn detect_abandoned_leases(&self) -> Vec<ChurnAnomaly> {
        // TODO: Implement with actual timestamp comparison
        Vec::new()
    }

    /// Group events by (namespace, lease_name)
    fn group_by_lease(&self) -> HashMap<(String, String), Vec<&LeaseEvent>> {
        let mut groups: HashMap<(String, String), Vec<&LeaseEvent>> = HashMap::new();
        
        for event in &self.events {
            let key = (event.namespace.clone(), event.lease_name.clone());
            groups.entry(key).or_default().push(event);
        }
        
        groups
    }

    /// Generate summary statistics
    pub fn summary(&self) -> AnalysisSummary {
        let grouped = self.group_by_lease();
        
        let mut actions = HashMap::new();
        for event in &self.events {
            *actions.entry(event.action.clone()).or_insert(0) += 1;
        }
        
        AnalysisSummary {
            total_events: self.events.len(),
            unique_leases: grouped.len(),
            events_by_action: actions,
        }
    }
}

impl Default for LeaseChurnAnalyzer {
    fn default() -> Self {
        Self::new()
    }
}

/// Summary of analysis results
#[derive(Debug)]
pub struct AnalysisSummary {
    pub total_events: usize,
    pub unique_leases: usize,
    pub events_by_action: HashMap<LeaseAction, usize>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_analyzer_creation() {
        let analyzer = LeaseChurnAnalyzer::new();
        assert_eq!(analyzer.config.churn_window_secs, 60);
    }

    #[test]
    fn test_custom_config() {
        let config = AnalyzerConfig {
            churn_window_secs: 120,
            churn_threshold: 20,
            ..Default::default()
        };
        let analyzer = LeaseChurnAnalyzer::with_config(config);
        assert_eq!(analyzer.config.churn_window_secs, 120);
        assert_eq!(analyzer.config.churn_threshold, 20);
    }

    #[test]
    fn test_empty_analysis() {
        let analyzer = LeaseChurnAnalyzer::new();
        let anomalies = analyzer.analyze();
        assert!(anomalies.is_empty());
    }

    #[test]
    fn test_summary() {
        let mut analyzer = LeaseChurnAnalyzer::new();
        analyzer.load_events(vec![
            LeaseEvent {
                timestamp: "2024-01-15T10:00:00Z".to_string(),
                namespace: "kube-system".to_string(),
                lease_name: "test-lease".to_string(),
                action: LeaseAction::Acquire,
                holder: Some("node-1".to_string()),
                duration_ms: 100,
            },
        ]);
        
        let summary = analyzer.summary();
        assert_eq!(summary.total_events, 1);
        assert_eq!(summary.unique_leases, 1);
    }
}
