/// sagco_bubble — SAGCO-Core Bubble State Machine CLI
///
/// Usage:
///   sagco-bubble "RB-001 4 27 1 0 N E UP"
///   sagco-bubble RB-001 4 27 1 0 N E UP
///   sagco-bubble --help
///
/// Output:
///   linear_feet, square_feet, state (000/101/111), next_action

use sagco_core::bubble::{BubbleRecord, print_bubble_result};

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();

    if args.is_empty() || args[0] == "--help" || args[0] == "-h" {
        println!("sagco-bubble — Rope Access Bubble State Machine");
        println!("Usage:");
        println!("  sagco-bubble \"RB-001 4 27 1 0 N E UP\"");
        println!("  sagco-bubble RB-001 4 27 1 0 N E UP");
        println!();
        println!("Fields:");
        println!("  <id>               bubble identifier (e.g. RB-001)");
        println!("  <pipe_dia_in>      pipe diameter in inches");
        println!("  <band_count>       number of inspection bands recorded");
        println!("  <rope_access>      1=rope access required, 0=no");
        println!("  <ground_access>    1=ground accessible, 0=no");
        println!("  <dir_h>            horizontal direction (N/S/E/W/NE...)");
        println!("  <dir_v>            vertical orientation (UP/DOWN)");
        println!();
        println!("States: 000_IDLE | 101_ACTIVE | 111_VERIFIED");
        return;
    }

    // Accept either a single quoted string or individual args
    let input = if args.len() == 1 {
        args[0].clone()
    } else {
        args.join(" ")
    };

    match BubbleRecord::parse(&input) {
        Ok(rec) => {
            let m = rec.measure();
            print_bubble_result(&rec, &m);
        }
        Err(e) => {
            eprintln!("BUBBLE_PARSE_ERROR: {}", e);
            eprintln!("Example: sagco-bubble RB-001 4 27 1 0 N E UP");
            std::process::exit(1);
        }
    }
}
