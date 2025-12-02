//! Analyzer Module
//!
//! Provides filtering and anomaly detection logic for GKE audit logs.

use crate::log_parser::AuditLogEntry;
use chrono::{DateTime, Duration, Utc};

/// Threshold for detecting high-frequency operations (operations per minute).
/// Operations exceeding this threshold from a single principal trigger an anomaly.
const HIGH_FREQUENCY_THRESHOLD: usize = 100;

/// Anomaly detection results
#[derive(Debug, Clone)]
pub struct Anomaly {
    /// The log entry that triggered the anomaly
    pub entry: AuditLogEntry,
    /// Type of anomaly detected
    pub anomaly_type: AnomalyType,
    /// Severity level (1-10, 10 being most severe)
    pub severity: u8,
    /// Human-readable description
    pub description: String,
}

/// Types of anomalies that can be detected
#[derive(Debug, Clone, PartialEq)]
pub enum AnomalyType {
    /// User-initiated mutation in sensitive namespace
    SensitiveNamespaceMutation,
    /// Unusual operation frequency
    HighFrequencyOperations,
    /// Operation during unusual hours
    UnusualTimeOperation,
    /// Failed authentication or authorization
    AuthenticationFailure,
    /// Deletion of critical resources
    CriticalResourceDeletion,
    /// Unknown principal performing operations
    UnknownPrincipal,
}

impl std::fmt::Display for AnomalyType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            AnomalyType::SensitiveNamespaceMutation => write!(f, "Sensitive Namespace Mutation"),
            AnomalyType::HighFrequencyOperations => write!(f, "High Frequency Operations"),
            AnomalyType::UnusualTimeOperation => write!(f, "Unusual Time Operation"),
            AnomalyType::AuthenticationFailure => write!(f, "Authentication Failure"),
            AnomalyType::CriticalResourceDeletion => write!(f, "Critical Resource Deletion"),
            AnomalyType::UnknownPrincipal => write!(f, "Unknown Principal"),
        }
    }
}

/// Analyzer for audit log entries
pub struct Analyzer {
    /// Entries to analyze
    entries: Vec<AuditLogEntry>,
}

impl Analyzer {
    /// Create a new analyzer with the given entries
    pub fn new(entries: Vec<AuditLogEntry>) -> Self {
        Self { entries }
    }

    /// Filter entries by cluster
    pub fn filter_by_cluster(&self, cluster: &str) -> Vec<&AuditLogEntry> {
        self.entries
            .iter()
            .filter(|e| e.cluster == cluster)
            .collect()
    }

    /// Filter entries by namespace
    pub fn filter_by_namespace(&self, namespace: &str) -> Vec<&AuditLogEntry> {
        self.entries
            .iter()
            .filter(|e| e.namespace == namespace)
            .collect()
    }

    /// Filter entries by time range
    pub fn filter_by_time_range(
        &self,
        start: DateTime<Utc>,
        end: DateTime<Utc>,
    ) -> Vec<&AuditLogEntry> {
        self.entries
            .iter()
            .filter(|e| e.timestamp >= start && e.timestamp <= end)
            .collect()
    }

    /// Get all mutation operations
    pub fn get_mutations(&self) -> Vec<&AuditLogEntry> {
        self.entries.iter().filter(|e| e.is_mutation()).collect()
    }

    /// Get operations by principal
    pub fn get_by_principal(&self, principal: &str) -> Vec<&AuditLogEntry> {
        self.entries
            .iter()
            .filter(|e| e.principal.contains(principal))
            .collect()
    }

    /// Get unique clusters in the log entries
    pub fn get_clusters(&self) -> Vec<String> {
        let mut clusters: Vec<String> = self
            .entries
            .iter()
            .map(|e| e.cluster.clone())
            .collect::<std::collections::HashSet<_>>()
            .into_iter()
            .collect();
        clusters.sort();
        clusters
    }

    /// Get unique namespaces in the log entries
    pub fn get_namespaces(&self) -> Vec<String> {
        let mut namespaces: Vec<String> = self
            .entries
            .iter()
            .map(|e| e.namespace.clone())
            .collect::<std::collections::HashSet<_>>()
            .into_iter()
            .collect();
        namespaces.sort();
        namespaces
    }

    /// Detect anomalies in the log entries
    pub fn detect_anomalies(&self) -> Vec<Anomaly> {
        let mut anomalies = Vec::new();

        for entry in &self.entries {
            // Check for user mutations in sensitive namespaces
            if entry.is_mutation() && entry.is_sensitive_namespace() && !entry.is_automated() {
                anomalies.push(Anomaly {
                    entry: entry.clone(),
                    anomaly_type: AnomalyType::SensitiveNamespaceMutation,
                    severity: 7,
                    description: format!(
                        "User '{}' performed {} on {} in sensitive namespace '{}'",
                        entry.principal, entry.operation, entry.resource_name, entry.namespace
                    ),
                });
            }

            // Check for authentication failures
            if entry.status_code == 401 || entry.status_code == 403 {
                anomalies.push(Anomaly {
                    entry: entry.clone(),
                    anomaly_type: AnomalyType::AuthenticationFailure,
                    severity: 8,
                    description: format!(
                        "Authentication/authorization failure for '{}' on {} (status: {})",
                        entry.principal, entry.resource_name, entry.status_code
                    ),
                });
            }

            // Check for critical resource deletions
            if entry.operation == "delete" && entry.is_sensitive_namespace() {
                anomalies.push(Anomaly {
                    entry: entry.clone(),
                    anomaly_type: AnomalyType::CriticalResourceDeletion,
                    severity: 9,
                    description: format!(
                        "Deletion of '{}' in namespace '{}' by '{}'",
                        entry.resource_name, entry.namespace, entry.principal
                    ),
                });
            }

            // Check for unknown principals
            if entry.principal == "unknown" || entry.principal.is_empty() {
                anomalies.push(Anomaly {
                    entry: entry.clone(),
                    anomaly_type: AnomalyType::UnknownPrincipal,
                    severity: 6,
                    description: format!(
                        "Unknown principal performed {} on {}",
                        entry.operation, entry.resource_name
                    ),
                });
            }
        }

        // Check for high frequency operations (more than 100 ops per minute from same principal)
        anomalies.extend(self.detect_high_frequency_operations());

        anomalies
    }

    /// Detect high-frequency operations by the same principal
    fn detect_high_frequency_operations(&self) -> Vec<Anomaly> {
        let mut anomalies = Vec::new();
        let mut principal_windows: std::collections::HashMap<String, Vec<DateTime<Utc>>> =
            std::collections::HashMap::new();

        // Group entries by principal and check for bursts
        for entry in &self.entries {
            principal_windows
                .entry(entry.principal.clone())
                .or_default()
                .push(entry.timestamp);
        }

        for (principal, mut timestamps) in principal_windows {
            if timestamps.len() < HIGH_FREQUENCY_THRESHOLD {
                continue;
            }

            // Check for bursts exceeding threshold in any 1-minute window
            timestamps.sort();

            for window_start in &timestamps {
                let window_end = *window_start + Duration::minutes(1);
                let count = timestamps
                    .iter()
                    .filter(|t| **t >= *window_start && **t < window_end)
                    .count();

                if count >= HIGH_FREQUENCY_THRESHOLD {
                    // Create a synthetic entry for the anomaly
                    if let Some(entry) = self.entries.iter().find(|e| e.principal == principal) {
                        anomalies.push(Anomaly {
                            entry: entry.clone(),
                            anomaly_type: AnomalyType::HighFrequencyOperations,
                            severity: 5,
                            description: format!(
                                "Principal '{}' performed {} operations in 1 minute",
                                principal, count
                            ),
                        });
                        break; // Only report once per principal
                    }
                }
            }
        }

        anomalies
    }

    /// Get a summary of operations by resource type
    pub fn get_resource_summary(&self) -> std::collections::HashMap<String, usize> {
        let mut summary = std::collections::HashMap::new();
        for entry in &self.entries {
            *summary.entry(entry.resource_type.clone()).or_insert(0) += 1;
        }
        summary
    }

    /// Get a summary of operations by operation type
    pub fn get_operation_summary(&self) -> std::collections::HashMap<String, usize> {
        let mut summary = std::collections::HashMap::new();
        for entry in &self.entries {
            *summary.entry(entry.operation.clone()).or_insert(0) += 1;
        }
        summary
    }

    /// Get all entries
    pub fn entries(&self) -> &[AuditLogEntry] {
        &self.entries
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn create_test_entry(
        principal: &str,
        namespace: &str,
        operation: &str,
        is_system: bool,
    ) -> AuditLogEntry {
        AuditLogEntry {
            timestamp: Utc::now(),
            principal: principal.to_string(),
            resource_type: "pods".to_string(),
            operation: operation.to_string(),
            namespace: namespace.to_string(),
            resource_name: "test-resource".to_string(),
            cluster: "test-cluster".to_string(),
            is_system_operation: is_system,
            status_code: 200,
            raw_data: None,
        }
    }

    #[test]
    fn test_detect_sensitive_namespace_mutation() {
        let entries = vec![create_test_entry(
            "user@example.com",
            "kube-system",
            "update",
            false,
        )];

        let analyzer = Analyzer::new(entries);
        let anomalies = analyzer.detect_anomalies();

        assert_eq!(anomalies.len(), 1);
        assert_eq!(
            anomalies[0].anomaly_type,
            AnomalyType::SensitiveNamespaceMutation
        );
    }

    #[test]
    fn test_no_anomaly_for_system_operations() {
        let entries = vec![create_test_entry(
            "system:serviceaccount:kube-system:scheduler",
            "kube-system",
            "update",
            true,
        )];

        let analyzer = Analyzer::new(entries);
        let anomalies = analyzer.detect_anomalies();

        // System operations in kube-system shouldn't trigger sensitive namespace mutation
        assert!(anomalies
            .iter()
            .all(|a| a.anomaly_type != AnomalyType::SensitiveNamespaceMutation));
    }

    #[test]
    fn test_filter_by_cluster() {
        let entries = vec![
            AuditLogEntry {
                cluster: "red-team".to_string(),
                ..create_test_entry("user1", "default", "create", false)
            },
            AuditLogEntry {
                cluster: "jarvis-swarm-personal-001".to_string(),
                ..create_test_entry("user2", "default", "create", false)
            },
        ];

        let analyzer = Analyzer::new(entries);
        let red_team = analyzer.filter_by_cluster("red-team");

        assert_eq!(red_team.len(), 1);
        assert_eq!(red_team[0].principal, "user1");
    }

    #[test]
    fn test_get_clusters() {
        let entries = vec![
            AuditLogEntry {
                cluster: "red-team".to_string(),
                ..create_test_entry("user1", "default", "create", false)
            },
            AuditLogEntry {
                cluster: "jarvis-swarm-personal-001".to_string(),
                ..create_test_entry("user2", "default", "create", false)
            },
            AuditLogEntry {
                cluster: "red-team".to_string(),
                ..create_test_entry("user3", "default", "create", false)
            },
        ];

        let analyzer = Analyzer::new(entries);
        let clusters = analyzer.get_clusters();

        assert_eq!(clusters.len(), 2);
        assert!(clusters.contains(&"red-team".to_string()));
        assert!(clusters.contains(&"jarvis-swarm-personal-001".to_string()));
    }
}
