use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "sagco-sync", about = "Field EVM + Productivity Dashboard")]
pub struct Cli {
    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Subcommand)]
pub enum Commands {
    /// EVM productivity report — CPI/SPI/EAC per circuit
    Productivity {
        /// RA sheet CSV file (omit for demo data)
        #[arg(value_name = "FILE")]
        file: Option<String>,
        /// Output JSON instead of terminal report
        #[arg(long)]
        json: bool,
    },
    /// Extract implied difficulty rates from RA sheet estimates
    Rates {
        /// RA sheet CSV file (omit for demo data)
        #[arg(value_name = "FILE")]
        file: Option<String>,
    },
    /// Monte Carlo EAC simulation
    Simulate {
        /// RA sheet CSV file (omit for demo data)
        #[arg(value_name = "FILE")]
        file: Option<String>,
        /// Number of simulations (default: 10000)
        #[arg(long, default_value = "10000")]
        n: usize,
    },
    /// Export Excel workbook with charts
    Export {
        /// RA sheet CSV file (omit for demo data)
        #[arg(value_name = "FILE")]
        file: Option<String>,
        /// Output file path
        #[arg(short, long, default_value = "sagco-sync-report.xlsx")]
        out: String,
    },
    /// Parse a .sagcoplan DSL file and print AST
    Parse {
        /// .sagcoplan file to parse
        file: String,
    },
    /// Show version and module status
    Status,
}
