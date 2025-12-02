//! Sovereignty Log Analyzer
//!
//! A CLI tool for analyzing GKE audit logs and computing sovereignty metrics.
//!
//! # Usage
//!
//! ```bash
//! # Analyze logs and show summary
//! sovereignty-log-analyzer analyze --input logs.json
//!
//! # Show sovereignty metrics dashboard
//! sovereignty-log-analyzer metrics --input logs.json
//!
//! # Watch logs in real-time (from stdin)
//! sovereignty-log-analyzer watch --input -
//!
//! # Generate a Markdown report
//! sovereignty-log-analyzer report --input logs.json --output report.md
//! ```

mod analyzer;
mod log_parser;
mod sovereignty_metrics;

use analyzer::Analyzer;
use clap::{Parser, Subcommand};
use log_parser::LogParser;
use sovereignty_metrics::{display_dashboard, generate_report, SovereigntyMetrics};
use std::fs;
use std::io::{self, BufRead, Read};
use std::path::PathBuf;

/// Sovereignty Log Analyzer - Analyze GKE audit logs for sovereignty metrics
#[derive(Parser)]
#[command(name = "sovereignty-log-analyzer")]
#[command(author = "Strategickhaos Swarm Intelligence")]
#[command(version = "0.1.0")]
#[command(about = "Analyze GKE audit logs and compute sovereignty metrics", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Analyze audit logs and show activity summary
    Analyze {
        /// Input file path (use '-' for stdin)
        #[arg(short, long)]
        input: String,

        /// Filter by cluster name
        #[arg(short, long)]
        cluster: Option<String>,

        /// Filter by namespace
        #[arg(short, long)]
        namespace: Option<String>,

        /// Show only anomalies
        #[arg(long)]
        anomalies_only: bool,
    },

    /// Display sovereignty metrics dashboard
    Metrics {
        /// Input file path (use '-' for stdin)
        #[arg(short, long)]
        input: String,

        /// Output metrics as JSON
        #[arg(long)]
        json: bool,
    },

    /// Watch logs in real-time and display metrics
    Watch {
        /// Input source (use '-' for stdin)
        #[arg(short, long)]
        input: String,

        /// Refresh interval in seconds
        #[arg(short, long, default_value = "5")]
        refresh: u64,
    },

    /// Generate a Markdown report
    Report {
        /// Input file path
        #[arg(short, long)]
        input: String,

        /// Output file path
        #[arg(short, long)]
        output: PathBuf,
    },
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Analyze {
            input,
            cluster,
            namespace,
            anomalies_only,
        } => {
            if let Err(e) = run_analyze(&input, cluster.as_deref(), namespace.as_deref(), anomalies_only) {
                eprintln!("Error: {}", e);
                std::process::exit(1);
            }
        }
        Commands::Metrics { input, json } => {
            if let Err(e) = run_metrics(&input, json) {
                eprintln!("Error: {}", e);
                std::process::exit(1);
            }
        }
        Commands::Watch { input, refresh } => {
            if let Err(e) = run_watch(&input, refresh) {
                eprintln!("Error: {}", e);
                std::process::exit(1);
            }
        }
        Commands::Report { input, output } => {
            if let Err(e) = run_report(&input, &output) {
                eprintln!("Error: {}", e);
                std::process::exit(1);
            }
        }
    }
}

fn read_input(input: &str) -> Result<String, Box<dyn std::error::Error>> {
    if input == "-" {
        let mut buffer = String::new();
        io::stdin().read_to_string(&mut buffer)?;
        Ok(buffer)
    } else {
        Ok(fs::read_to_string(input)?)
    }
}

fn run_analyze(
    input: &str,
    cluster: Option<&str>,
    namespace: Option<&str>,
    anomalies_only: bool,
) -> Result<(), Box<dyn std::error::Error>> {
    let content = read_input(input)?;
    let entries = LogParser::parse_logs(&content)?;
    let analyzer = Analyzer::new(entries);

    println!("\n📋 Audit Log Analysis\n");
    println!("═══════════════════════════════════════════════════════════\n");

    // Apply filters
    let filtered_entries: Vec<_> = analyzer
        .entries()
        .iter()
        .filter(|e| cluster.is_none() || e.cluster == cluster.unwrap())
        .filter(|e| namespace.is_none() || e.namespace == namespace.unwrap())
        .collect();

    println!("Total entries: {}", filtered_entries.len());
    println!();

    // Show clusters
    let clusters = analyzer.get_clusters();
    println!("🌐 Clusters: {}", clusters.join(", "));

    // Show namespaces
    let namespaces = analyzer.get_namespaces();
    println!("📁 Namespaces: {}", namespaces.join(", "));
    println!();

    // Resource summary
    println!("📊 Operations by Resource Type:");
    let resource_summary = analyzer.get_resource_summary();
    for (resource, count) in resource_summary {
        println!("  {}: {}", resource, count);
    }
    println!();

    // Operation summary
    println!("🔧 Operations by Type:");
    let op_summary = analyzer.get_operation_summary();
    for (op, count) in op_summary {
        println!("  {}: {}", op, count);
    }
    println!();

    // Anomalies
    let anomalies = analyzer.detect_anomalies();
    if !anomalies.is_empty() {
        println!("⚠️  Anomalies Detected ({}):\n", anomalies.len());
        for anomaly in &anomalies {
            let severity_icon = match anomaly.severity {
                1..=3 => "🟢",
                4..=6 => "🟡",
                7..=8 => "🟠",
                _ => "🔴",
            };
            println!(
                "  {} [{}] {}: {}",
                severity_icon, anomaly.severity, anomaly.anomaly_type, anomaly.description
            );
        }
        println!();
    } else if anomalies_only {
        println!("✅ No anomalies detected.\n");
    }

    // Recent activity (last 10 entries)
    if !anomalies_only && !filtered_entries.is_empty() {
        println!("📝 Recent Activity (up to 10 entries):\n");
        for entry in filtered_entries.iter().take(10) {
            println!(
                "  {} | {} | {} | {} | {}",
                entry.timestamp.format("%H:%M:%S"),
                entry.cluster,
                entry.namespace,
                entry.operation,
                entry.resource_name
            );
        }
        println!();
    }

    Ok(())
}

fn run_metrics(input: &str, json_output: bool) -> Result<(), Box<dyn std::error::Error>> {
    let content = read_input(input)?;
    let entries = LogParser::parse_logs(&content)?;

    // Calculate overall metrics
    let metrics = SovereigntyMetrics::calculate(&entries);

    // Calculate per-cluster metrics
    let analyzer = Analyzer::new(entries.clone());
    let clusters = analyzer.get_clusters();
    let cluster_metrics: Vec<_> = clusters
        .iter()
        .map(|c| {
            let cluster_entries: Vec<_> = entries.iter().filter(|e| &e.cluster == c).cloned().collect();
            (c.clone(), SovereigntyMetrics::calculate(&cluster_entries))
        })
        .collect();

    if json_output {
        // Output as JSON
        let output = serde_json::json!({
            "overall": {
                "total_operations": metrics.total_operations,
                "automated_operations": metrics.automated_operations,
                "human_operations": metrics.human_operations,
                "automation_ratio": metrics.automation_ratio,
                "operations_per_minute": metrics.operations_per_minute,
                "decision_latency_ms": metrics.decision_latency_ms,
                "cost_efficiency_score": metrics.cost_efficiency_score,
                "cluster_count": metrics.cluster_count,
                "anomaly_count": metrics.anomaly_count,
                "speed_improvement": metrics.speed_improvement(),
            },
            "clusters": cluster_metrics.iter().map(|(name, m)| {
                serde_json::json!({
                    "name": name,
                    "total_operations": m.total_operations,
                    "automation_ratio": m.automation_ratio,
                    "cost_efficiency_score": m.cost_efficiency_score,
                    "anomaly_count": m.anomaly_count,
                })
            }).collect::<Vec<_>>(),
        });
        println!("{}", serde_json::to_string_pretty(&output)?);
    } else {
        // Display dashboard
        display_dashboard(&metrics, &cluster_metrics);
    }

    Ok(())
}

fn run_watch(input: &str, refresh: u64) -> Result<(), Box<dyn std::error::Error>> {
    if input != "-" {
        return Err("Watch mode only supports stdin input (use --input -)".into());
    }

    println!("🔍 Watching for audit log entries... (Ctrl+C to stop)\n");

    let mut all_entries = Vec::new();
    let stdin = io::stdin();
    let mut last_display = std::time::Instant::now();

    for line in stdin.lock().lines() {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }

        // Try to parse each line as a log entry
        if let Ok(mut entries) = LogParser::parse_logs(&line) {
            all_entries.append(&mut entries);
        }

        // Refresh display periodically
        if last_display.elapsed() >= std::time::Duration::from_secs(refresh) {
            // Clear screen (basic ANSI escape)
            print!("\x1B[2J\x1B[1;1H");

            if !all_entries.is_empty() {
                let metrics = SovereigntyMetrics::calculate(&all_entries);
                let analyzer = Analyzer::new(all_entries.clone());
                let clusters = analyzer.get_clusters();
                let cluster_metrics: Vec<_> = clusters
                    .iter()
                    .map(|c| {
                        let cluster_entries: Vec<_> =
                            all_entries.iter().filter(|e| &e.cluster == c).cloned().collect();
                        (c.clone(), SovereigntyMetrics::calculate(&cluster_entries))
                    })
                    .collect();

                display_dashboard(&metrics, &cluster_metrics);
            }

            last_display = std::time::Instant::now();
        }
    }

    Ok(())
}

fn run_report(input: &str, output: &PathBuf) -> Result<(), Box<dyn std::error::Error>> {
    let content = read_input(input)?;
    let entries = LogParser::parse_logs(&content)?;

    // Calculate metrics
    let metrics = SovereigntyMetrics::calculate(&entries);

    // Get per-cluster metrics
    let analyzer = Analyzer::new(entries.clone());
    let clusters = analyzer.get_clusters();
    let cluster_metrics: Vec<_> = clusters
        .iter()
        .map(|c| {
            let cluster_entries: Vec<_> = entries.iter().filter(|e| &e.cluster == c).cloned().collect();
            (c.clone(), SovereigntyMetrics::calculate(&cluster_entries))
        })
        .collect();

    // Get anomalies
    let anomalies = analyzer.detect_anomalies();

    // Generate report
    let report = generate_report(&metrics, &cluster_metrics, &anomalies);

    // Write to file
    fs::write(output, &report)?;
    println!("✅ Report generated: {}", output.display());

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    fn create_test_log_file() -> NamedTempFile {
        let mut file = NamedTempFile::new().unwrap();
        let log_content = r#"[
            {
                "timestamp": "2024-01-15T10:30:00Z",
                "protoPayload": {
                    "authenticationInfo": {
                        "principalEmail": "system:serviceaccount:kube-system:controller"
                    },
                    "methodName": "io.k8s.core.v1.pods.update",
                    "resourceName": "projects/test/zones/us-central1-a/clusters/red-team/namespaces/default/pods/test-pod"
                },
                "resource": {
                    "labels": {
                        "cluster_name": "red-team"
                    }
                }
            },
            {
                "timestamp": "2024-01-15T10:31:00Z",
                "protoPayload": {
                    "authenticationInfo": {
                        "principalEmail": "user@example.com"
                    },
                    "methodName": "io.k8s.core.v1.configmaps.create",
                    "resourceName": "projects/test/zones/us-central1-a/clusters/jarvis-swarm-personal-001/namespaces/kube-system/configmaps/test-config"
                },
                "resource": {
                    "labels": {
                        "cluster_name": "jarvis-swarm-personal-001"
                    }
                }
            }
        ]"#;
        file.write_all(log_content.as_bytes()).unwrap();
        file
    }

    #[test]
    fn test_read_input_from_file() {
        let file = create_test_log_file();
        let content = read_input(file.path().to_str().unwrap()).unwrap();
        assert!(content.contains("red-team"));
    }

    #[test]
    fn test_analyze_command() {
        let file = create_test_log_file();
        let result = run_analyze(file.path().to_str().unwrap(), None, None, false);
        assert!(result.is_ok());
    }

    #[test]
    fn test_metrics_command() {
        let file = create_test_log_file();
        let result = run_metrics(file.path().to_str().unwrap(), false);
        assert!(result.is_ok());
    }

    #[test]
    fn test_report_command() {
        let file = create_test_log_file();
        let output = NamedTempFile::new().unwrap();
        let result = run_report(file.path().to_str().unwrap(), &output.path().to_path_buf());
        assert!(result.is_ok());

        let report_content = fs::read_to_string(output.path()).unwrap();
        assert!(report_content.contains("Sovereignty Log Analysis Report"));
    }
}
