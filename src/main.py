#!/usr/bin/env python3
"""
Sovereign Swarm Orchestrator

The main entry point for the Sovereignty Architecture. This orchestrator provides
three primary modes of operation:

1. handshake - Analyze input context and suggest target modules using SWARM-HS
2. analyze - Run sovereignty log analysis and generate reports
3. experiment - Create and manage Black Ops Lab experiments

Usage:
    python src/main.py handshake --input <context_file>
    python src/main.py analyze --input <log_file>
    python src/main.py experiment --name <name> --context <context_file>
    python src/main.py experiment --list
    python src/main.py experiment --status <experiment_id>

For more information, see docs/SOVEREIGNTY_DOCTRINE.md
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add src directory to path for imports
SRC_DIR = Path(__file__).parent
sys.path.insert(0, str(SRC_DIR))

from swarm import SwarmGrammar
from analyzers import SovereigntyLogAnalyzer
from experiments import ParticleCollider


def cmd_handshake(args: argparse.Namespace) -> int:
    """
    Execute handshake mode: analyze input and suggest module targets.
    
    This mode loads the Sovereign Pattern Language from docs/ and uses it
    to analyze the provided input file, suggesting which module should
    receive new code based on the content's intent.
    
    Args:
        args: Parsed arguments containing input path
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1
    
    print("=" * 60)
    print("SWARM-HS Handshake Mode")
    print("=" * 60)
    print(f"\nAnalyzing: {input_path}")
    
    # Load grammar from docs
    docs_dir = SRC_DIR.parent / "docs"
    grammar = SwarmGrammar.from_markdown(docs_dir)
    
    print(f"\nLoaded {len(grammar.patterns)} sovereignty patterns from docs/")
    
    # Read input content
    content = input_path.read_text()
    
    # Suggest module targets
    suggestions = grammar.suggest_module_targets(content)
    
    print("\n" + "-" * 60)
    print("Module Target Suggestions")
    print("-" * 60)
    
    for module, confidence, reason in suggestions:
        bar = "█" * int(confidence * 20)
        print(f"\n  {module}/")
        print(f"    Confidence: [{bar:<20}] {confidence:.0%}")
        print(f"    Reason: {reason}")
    
    print("\n" + "=" * 60)
    print("Handshake complete. Use the suggested module(s) for new code.")
    print("=" * 60)
    
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    """
    Execute analyze mode: run sovereignty log analysis and generate reports.
    
    This mode uses the SovereigntyLogAnalyzer to process GKE audit logs,
    compute sovereignty metrics, and generate a markdown report.
    
    Args:
        args: Parsed arguments containing input path
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    input_path = Path(args.input).resolve()
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1
    
    print("=" * 60)
    print("Sovereignty Log Analyzer Mode")
    print("=" * 60)
    print(f"\nAnalyzing: {input_path}")
    
    # Initialize analyzer
    analyzer = SovereigntyLogAnalyzer()
    
    # Check if Rust binary is available
    if not analyzer.binary_available():
        print("\nWarning: sovereignty-log-analyzer binary not found.")
        print("Using fallback Python analysis...")
    
    # Run analysis
    try:
        metrics = analyzer.analyze(input_path)
    except Exception as e:
        print(f"\nError during analysis: {e}", file=sys.stderr)
        return 1
    
    # Pretty-print metrics
    print("\n" + "-" * 60)
    print("Sovereignty Metrics")
    print("-" * 60)
    
    analyzer.print_metrics(metrics)
    
    # Generate report
    logs_dir = SRC_DIR.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_path = logs_dir / f"sovereignty_report_{timestamp}.md"
    
    analyzer.write_report(metrics, report_path, input_path)
    
    print(f"\n✓ Report written to: {report_path}")
    print("\n" + "=" * 60)
    
    return 0


def cmd_experiment(args: argparse.Namespace) -> int:
    """
    Execute experiment mode: create and manage Black Ops Lab experiments.
    
    This mode handles experiment lifecycle operations:
    - Creating new experiments with --name and --context
    - Listing all experiments with --list
    - Checking experiment status with --status
    - Archiving completed experiments with --archive
    
    Args:
        args: Parsed arguments containing experiment options
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    collider = ParticleCollider()
    
    # Handle --list
    if args.list:
        print("=" * 60)
        print("Black Ops Lab - Experiment Registry")
        print("=" * 60)
        
        experiments = collider.list_experiments()
        
        if not experiments:
            print("\nNo experiments found.")
        else:
            for exp in experiments:
                status_icon = "✓" if exp["completed"] else "⋯"
                print(f"\n  {status_icon} {exp['id']}")
                print(f"      Status: {exp['status']}")
                print(f"      Created: {exp['created']}")
        
        return 0
    
    # Handle --status
    if args.status:
        print("=" * 60)
        print(f"Experiment Status: {args.status}")
        print("=" * 60)
        
        status = collider.get_experiment_status(args.status)
        
        if status is None:
            print(f"\nExperiment not found: {args.status}", file=sys.stderr)
            return 1
        
        print(f"\n  ID: {status['id']}")
        print(f"  Status: {status['status']}")
        print(f"  Created: {status['created']}")
        print(f"  Phases Completed: {status['phases_completed']}")
        print(f"  Directory: {status['directory']}")
        
        return 0
    
    # Handle --archive
    if args.archive:
        print(f"Archiving experiment: {args.archive}")
        
        success = collider.archive_experiment(args.archive)
        
        if not success:
            print(f"Error: Could not archive experiment: {args.archive}", file=sys.stderr)
            return 1
        
        print(f"✓ Experiment archived successfully")
        return 0
    
    # Handle --name + --context (create new experiment)
    if args.name:
        if not args.context:
            print("Error: --context required when creating experiment", file=sys.stderr)
            return 1
        
        context_path = Path(args.context)
        
        if not context_path.exists():
            print(f"Error: Context file not found: {context_path}", file=sys.stderr)
            return 1
        
        print("=" * 60)
        print("Black Ops Lab - Creating Experiment")
        print("=" * 60)
        
        experiment = collider.create_experiment(
            name=args.name,
            context_file=context_path
        )
        
        print(f"\n✓ Experiment created: {experiment.experiment_id}")
        print(f"  Directory: {experiment.experiment_dir}")
        print("\n  Files created:")
        print("    - context.md (input context)")
        print("    - experiment_log.md (phase log template)")
        print("    - results.yaml (result template)")
        
        print("\n" + "-" * 60)
        print("Next steps:")
        print("-" * 60)
        print("  1. Review the experiment_log.md template")
        print("  2. Run agents to fill in each phase")
        print("  3. Record results in results.yaml")
        print("  4. Write conclusions in conclusions.md")
        print("  5. Archive with: python src/main.py experiment --archive " + experiment.experiment_id)
        
        return 0
    
    # No valid operation specified
    print("Error: Must specify --name/--context, --list, --status, or --archive", file=sys.stderr)
    return 1


def main() -> int:
    """
    Main entry point for the Sovereign Swarm Orchestrator.
    
    Parses command line arguments and dispatches to the appropriate
    mode handler (handshake, analyze, or experiment).
    
    Returns:
        Exit code to return to the shell
    """
    parser = argparse.ArgumentParser(
        description="Sovereign Swarm Orchestrator - Coordinate agents under sovereignty constraints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze input and suggest modules
  python src/main.py handshake --input my_idea.md

  # Analyze GKE audit logs
  python src/main.py analyze --input /path/to/audit.json

  # Create a new experiment
  python src/main.py experiment --name "my-test" --context input.md

  # List all experiments
  python src/main.py experiment --list

For more information, see docs/SOVEREIGNTY_DOCTRINE.md
        """
    )
    
    subparsers = parser.add_subparsers(dest="mode", help="Operating mode")
    
    # Handshake mode
    handshake_parser = subparsers.add_parser(
        "handshake",
        help="Analyze input context and suggest module targets"
    )
    handshake_parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to input context file (markdown or text)"
    )
    
    # Analyze mode
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Run sovereignty log analysis and generate reports"
    )
    analyze_parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to GKE audit log JSON file"
    )
    
    # Experiment mode
    experiment_parser = subparsers.add_parser(
        "experiment",
        help="Create and manage Black Ops Lab experiments"
    )
    experiment_parser.add_argument(
        "--name", "-n",
        help="Name for new experiment"
    )
    experiment_parser.add_argument(
        "--context", "-c",
        help="Path to context file for new experiment"
    )
    experiment_parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all experiments"
    )
    experiment_parser.add_argument(
        "--status", "-s",
        help="Show status of specific experiment"
    )
    experiment_parser.add_argument(
        "--archive", "-a",
        help="Archive completed experiment"
    )
    
    args = parser.parse_args()
    
    if args.mode is None:
        parser.print_help()
        return 1
    
    # Dispatch to mode handler
    if args.mode == "handshake":
        return cmd_handshake(args)
    elif args.mode == "analyze":
        return cmd_analyze(args)
    elif args.mode == "experiment":
        return cmd_experiment(args)
    else:
        print(f"Unknown mode: {args.mode}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
