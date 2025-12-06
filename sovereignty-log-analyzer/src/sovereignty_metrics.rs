//! Sovereignty Metrics Module
//!
//! Computes sovereignty-related metrics and provides a dashboard display.

use crate::analyzer::Analyzer;
use crate::log_parser::AuditLogEntry;
use chrono::Utc;
use colored::*;

/// Estimated latency for human-initiated decisions in milliseconds.
/// Based on typical response time for manual operations (approximately 1 minute).
const HUMAN_LATENCY_MS: f64 = 60000.0;

/// Estimated latency for automated decisions in milliseconds.
/// Automated systems can respond much faster than humans (~1000x improvement).
const AUTOMATED_LATENCY_MS: f64 = 60.0;

/// Sovereignty metrics computed from audit logs
#[derive(Debug, Clone)]
pub struct SovereigntyMetrics {
    /// Ratio of automated vs human-initiated operations (0.0 - 1.0)
    pub automation_ratio: f64,
    /// Number of operations per minute
    pub operations_per_minute: f64,
    /// Average decision latency in milliseconds (estimated)
    pub decision_latency_ms: f64,
    /// Cost efficiency score (0.0 - 100.0)
    pub cost_efficiency_score: f64,
    /// Number of clusters analyzed
    pub cluster_count: usize,
    /// Total number of operations
    pub total_operations: usize,
    /// Number of automated operations
    pub automated_operations: usize,
    /// Number of human operations
    pub human_operations: usize,
    /// Number of anomalies detected
    pub anomaly_count: usize,
    /// Time span of the logs analyzed (in minutes)
    pub time_span_minutes: f64,
}

impl SovereigntyMetrics {
    /// Calculate sovereignty metrics from log entries
    pub fn calculate(entries: &[AuditLogEntry]) -> Self {
        if entries.is_empty() {
            return Self::empty();
        }

        let total_operations = entries.len();
        let automated_operations = entries.iter().filter(|e| e.is_automated()).count();
        let human_operations = total_operations - automated_operations;

        // Calculate automation ratio
        let automation_ratio = if total_operations > 0 {
            automated_operations as f64 / total_operations as f64
        } else {
            0.0
        };

        // Calculate time span
        let mut timestamps: Vec<_> = entries.iter().map(|e| e.timestamp).collect();
        timestamps.sort();
        let time_span_minutes = match (timestamps.first(), timestamps.last()) {
            (Some(first), Some(last)) if timestamps.len() > 1 => {
                let duration = last.signed_duration_since(*first);
                duration.num_seconds() as f64 / 60.0
            }
            _ => 1.0, // Default to 1 minute if only one entry or empty
        };

        // Calculate operations per minute
        let operations_per_minute = if time_span_minutes > 0.0 {
            total_operations as f64 / time_span_minutes
        } else {
            total_operations as f64
        };

        // Calculate decision latency using defined constants
        let decision_latency_ms = if total_operations > 0 {
            (automated_operations as f64 * AUTOMATED_LATENCY_MS
                + human_operations as f64 * HUMAN_LATENCY_MS)
                / total_operations as f64
        } else {
            0.0
        };

        // Calculate cost efficiency score
        // Higher automation ratio = higher efficiency
        // Lower decision latency = higher efficiency
        // Formula: base score * automation bonus * latency bonus
        let base_score = 50.0;
        let automation_bonus = 1.0 + automation_ratio;
        let latency_factor = 1.0 - (decision_latency_ms / HUMAN_LATENCY_MS).min(1.0);
        let cost_efficiency_score = (base_score * automation_bonus * (1.0 + latency_factor)).min(100.0);

        // Count unique clusters
        let clusters: std::collections::HashSet<_> = entries.iter().map(|e| &e.cluster).collect();
        let cluster_count = clusters.len();

        // Count anomalies
        let analyzer = Analyzer::new(entries.to_vec());
        let anomaly_count = analyzer.detect_anomalies().len();

        Self {
            automation_ratio,
            operations_per_minute,
            decision_latency_ms,
            cost_efficiency_score,
            cluster_count,
            total_operations,
            automated_operations,
            human_operations,
            anomaly_count,
            time_span_minutes,
        }
    }

    /// Create empty metrics
    fn empty() -> Self {
        Self {
            automation_ratio: 0.0,
            operations_per_minute: 0.0,
            decision_latency_ms: 0.0,
            cost_efficiency_score: 0.0,
            cluster_count: 0,
            total_operations: 0,
            automated_operations: 0,
            human_operations: 0,
            anomaly_count: 0,
            time_span_minutes: 0.0,
        }
    }

    /// Calculate speed improvement factor
    pub fn speed_improvement(&self) -> f64 {
        if self.human_operations > 0 && self.automation_ratio > 0.0 {
            // Automated decisions are approximately 1000x faster
            1000.0 * self.automation_ratio
        } else if self.automated_operations > 0 {
            1000.0
        } else {
            1.0
        }
    }
}

/// Display sovereignty dashboard in the terminal
pub fn display_dashboard(metrics: &SovereigntyMetrics, cluster_metrics: &[(String, SovereigntyMetrics)]) {
    println!();
    println!("{}", "╔══════════════════════════════════════════════════════════════════╗".cyan());
    println!("{}", "║           🏛️  SOVEREIGNTY METRICS DASHBOARD  🏛️                   ║".cyan());
    println!("{}", "╚══════════════════════════════════════════════════════════════════╝".cyan());
    println!();

    // Overall metrics
    println!("{}", "📊 Overall Metrics".bold().yellow());
    println!("{}", "─".repeat(50).dimmed());
    
    println!(
        "  Total Operations:     {} ({} automated, {} human)",
        metrics.total_operations.to_string().green(),
        metrics.automated_operations.to_string().blue(),
        metrics.human_operations.to_string().yellow()
    );
    
    println!(
        "  Automation Ratio:     {:.1}%",
        format!("{:.1}", metrics.automation_ratio * 100.0).green()
    );
    
    println!(
        "  Ops/Minute:           {:.2}",
        format!("{:.2}", metrics.operations_per_minute).cyan()
    );
    
    println!(
        "  Decision Latency:     {:.0}ms avg",
        format!("{:.0}", metrics.decision_latency_ms).yellow()
    );
    
    println!(
        "  Cost Efficiency:      {:.1}/100",
        format!("{:.1}", metrics.cost_efficiency_score).green()
    );
    
    println!(
        "  Time Span:            {:.1} minutes",
        format!("{:.1}", metrics.time_span_minutes).dimmed()
    );
    
    println!(
        "  Anomalies Detected:   {}",
        if metrics.anomaly_count > 0 {
            metrics.anomaly_count.to_string().red()
        } else {
            "0".to_string().green()
        }
    );

    println!();

    // Speed improvement banner
    let speed = metrics.speed_improvement();
    if speed > 1.0 {
        println!("{}", "⚡ SOVEREIGNTY ACCELERATION ⚡".bold().magenta());
        println!("{}", "─".repeat(50).dimmed());
        println!(
            "  Speed Improvement:    {}x faster automated decisions",
            format!("{:.0}", speed).bright_green().bold()
        );
        println!();
    }

    // Cluster breakdown
    if !cluster_metrics.is_empty() {
        println!("{}", "🌐 Cluster Breakdown".bold().yellow());
        println!("{}", "─".repeat(50).dimmed());
        
        for (cluster, m) in cluster_metrics {
            let status = if m.anomaly_count > 0 {
                "⚠️".to_string()
            } else {
                "✅".to_string()
            };
            
            println!(
                "  {} {} | {} ops | {:.1}% automated | {:.1} efficiency",
                status,
                cluster.bright_white(),
                m.total_operations.to_string().cyan(),
                m.automation_ratio * 100.0,
                m.cost_efficiency_score
            );
        }
        println!();
    }

    // Footer
    println!("{}", "═".repeat(68).cyan());
    println!(
        "{}",
        format!(
            "  Analyzed at: {} | Clusters: {}",
            Utc::now().format("%Y-%m-%d %H:%M:%S UTC"),
            metrics.cluster_count
        )
        .dimmed()
    );
    println!("{}", "═".repeat(68).cyan());
    println!();
}

/// Generate a Markdown report
pub fn generate_report(
    metrics: &SovereigntyMetrics,
    cluster_metrics: &[(String, SovereigntyMetrics)],
    anomalies: &[crate::analyzer::Anomaly],
) -> String {
    let mut report = String::new();

    report.push_str("# 🏛️ Sovereignty Log Analysis Report\n\n");
    report.push_str(&format!(
        "**Generated:** {}\n\n",
        Utc::now().format("%Y-%m-%d %H:%M:%S UTC")
    ));

    // Executive Summary
    report.push_str("## 📊 Executive Summary\n\n");
    report.push_str("| Metric | Value |\n");
    report.push_str("|--------|-------|\n");
    report.push_str(&format!("| Total Operations | {} |\n", metrics.total_operations));
    report.push_str(&format!(
        "| Automation Ratio | {:.1}% |\n",
        metrics.automation_ratio * 100.0
    ));
    report.push_str(&format!(
        "| Operations/Minute | {:.2} |\n",
        metrics.operations_per_minute
    ));
    report.push_str(&format!(
        "| Decision Latency | {:.0}ms |\n",
        metrics.decision_latency_ms
    ));
    report.push_str(&format!(
        "| Cost Efficiency | {:.1}/100 |\n",
        metrics.cost_efficiency_score
    ));
    report.push_str(&format!("| Clusters Analyzed | {} |\n", metrics.cluster_count));
    report.push_str(&format!("| Anomalies Detected | {} |\n\n", metrics.anomaly_count));

    // Speed improvement
    let speed = metrics.speed_improvement();
    if speed > 1.0 {
        report.push_str("### ⚡ Sovereignty Acceleration\n\n");
        report.push_str(&format!(
            "**Speed Improvement:** {:.0}x faster automated decisions\n\n",
            speed
        ));
    }

    // Cluster breakdown
    if !cluster_metrics.is_empty() {
        report.push_str("## 🌐 Cluster Analysis\n\n");
        report.push_str("| Cluster | Operations | Automation | Efficiency | Status |\n");
        report.push_str("|---------|------------|------------|------------|--------|\n");

        for (cluster, m) in cluster_metrics {
            let status = if m.anomaly_count > 0 { "⚠️" } else { "✅" };
            report.push_str(&format!(
                "| {} | {} | {:.1}% | {:.1} | {} |\n",
                cluster,
                m.total_operations,
                m.automation_ratio * 100.0,
                m.cost_efficiency_score,
                status
            ));
        }
        report.push('\n');
    }

    // Anomalies
    if !anomalies.is_empty() {
        report.push_str("## ⚠️ Anomalies Detected\n\n");
        report.push_str("| Severity | Type | Description |\n");
        report.push_str("|----------|------|-------------|\n");

        for anomaly in anomalies {
            let severity_icon = match anomaly.severity {
                1..=3 => "🟢",
                4..=6 => "🟡",
                7..=8 => "🟠",
                _ => "🔴",
            };
            report.push_str(&format!(
                "| {} ({}) | {} | {} |\n",
                severity_icon, anomaly.severity, anomaly.anomaly_type, anomaly.description
            ));
        }
        report.push('\n');
    }

    // Recommendations
    report.push_str("## 💡 Recommendations\n\n");
    
    if metrics.automation_ratio < 0.8 {
        report.push_str("- **Increase Automation:** Current automation ratio is below 80%. Consider automating more routine operations.\n");
    }
    
    if metrics.anomaly_count > 0 {
        report.push_str("- **Review Anomalies:** Detected anomalies require attention. Review and address security concerns.\n");
    }
    
    if metrics.decision_latency_ms > 10000.0 {
        report.push_str("- **Reduce Latency:** High average decision latency. Consider implementing more automated decision-making.\n");
    }

    if metrics.automation_ratio >= 0.8 && metrics.anomaly_count == 0 {
        report.push_str("- **Maintain Excellence:** System is operating with high automation and no anomalies. Continue monitoring.\n");
    }

    report.push_str("\n---\n\n");
    report.push_str("*Generated by Sovereignty Log Analyzer*\n");

    report
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::{Duration, NaiveDate, NaiveDateTime, NaiveTime};

    fn create_test_entry(is_automated: bool, timestamp: chrono::DateTime<Utc>) -> AuditLogEntry {
        AuditLogEntry {
            timestamp,
            principal: if is_automated {
                "system:serviceaccount:kube-system:controller".to_string()
            } else {
                "user@example.com".to_string()
            },
            resource_type: "pods".to_string(),
            operation: "update".to_string(),
            namespace: "default".to_string(),
            resource_name: "test-pod".to_string(),
            cluster: "test-cluster".to_string(),
            is_system_operation: is_automated,
            status_code: 200,
            raw_data: None,
        }
    }

    #[test]
    fn test_calculate_metrics() {
        let naive_date = NaiveDate::from_ymd_opt(2024, 1, 15).unwrap();
        let naive_time = NaiveTime::from_hms_opt(10, 0, 0).unwrap();
        let naive_dt = NaiveDateTime::new(naive_date, naive_time);
        let base_time = naive_dt.and_utc();
        let entries: Vec<AuditLogEntry> = (0..10)
            .map(|i| {
                let is_automated = i < 8; // 80% automated
                let timestamp = base_time + Duration::seconds(i * 6); // 10 entries over 1 minute
                create_test_entry(is_automated, timestamp)
            })
            .collect();

        let metrics = SovereigntyMetrics::calculate(&entries);

        assert_eq!(metrics.total_operations, 10);
        assert_eq!(metrics.automated_operations, 8);
        assert_eq!(metrics.human_operations, 2);
        assert!((metrics.automation_ratio - 0.8).abs() < 0.001);
    }

    #[test]
    fn test_empty_metrics() {
        let entries: Vec<AuditLogEntry> = vec![];
        let metrics = SovereigntyMetrics::calculate(&entries);

        assert_eq!(metrics.total_operations, 0);
        assert_eq!(metrics.automation_ratio, 0.0);
    }

    #[test]
    fn test_speed_improvement() {
        let base_time = Utc::now();
        let entries: Vec<AuditLogEntry> = (0..10)
            .map(|i| {
                let is_automated = i < 5; // 50% automated
                create_test_entry(is_automated, base_time)
            })
            .collect();

        let metrics = SovereigntyMetrics::calculate(&entries);
        let speed = metrics.speed_improvement();

        assert!(speed > 1.0);
        assert!((speed - 500.0).abs() < 1.0); // 50% * 1000 = 500x
    }

    #[test]
    fn test_generate_report() {
        let base_time = Utc::now();
        let entries: Vec<AuditLogEntry> = (0..5)
            .map(|_| create_test_entry(true, base_time))
            .collect();

        let metrics = SovereigntyMetrics::calculate(&entries);
        let report = generate_report(&metrics, &[], &[]);

        assert!(report.contains("Sovereignty Log Analysis Report"));
        assert!(report.contains("Total Operations"));
        assert!(report.contains("Automation Ratio"));
    }
}
