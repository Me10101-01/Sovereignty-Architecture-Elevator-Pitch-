// CLI Recon Module - 36 Commands for Offline Internet Wave Reconnaissance
pub mod recon_cmds;

use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "skhaos")]
#[command(about = "Quantum-addressed offline reconnaissance via UDAP", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Execute a reconnaissance command
    Recon {
        /// Command ID (1-36)
        #[arg(short, long)]
        id: u8,
        
        /// UDAP URI to probe
        #[arg(short, long)]
        uri: String,
        
        /// Frequency in Hz (optional)
        #[arg(short, long)]
        hz: Option<f64>,
    },
    
    /// List all available recon commands
    List,
    
    /// Validate a UDAP URI against schema
    Validate {
        /// UDAP URI to validate
        uri: String,
    },
}

pub fn run_cli() {
    let cli = Cli::parse();
    
    match cli.command {
        Commands::Recon { id, uri, hz } => {
            let frequency = hz.unwrap_or(20.0);
            println!("Executing recon command {}...", id);
            recon_cmds::execute_command(id, &uri, frequency);
        },
        Commands::List => {
            recon_cmds::list_commands();
        },
        Commands::Validate { uri } => {
            println!("Validating UDAP URI: {}", uri);
            recon_cmds::validate_udap_uri(&uri);
        },
    }
}
