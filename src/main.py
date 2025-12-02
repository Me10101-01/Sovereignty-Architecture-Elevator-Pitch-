#!/usr/bin/env python3
"""
Sovereignty Architecture: Sovereign Swarm Orchestrator

The main entry point for the Sovereign Swarm system.

Modes:
    diagnose   - Run the Differential Engine (House M.D. psychoanalysis)
    handshake  - Execute a SWARM handshake protocol
    experiment - Run a controlled experiment in the particle accelerator

Usage:
    python src/main.py diagnose --input "your raw thoughts"
    python src/main.py diagnose --file path/to/thoughts.txt
    python src/main.py handshake --context path/to/context.md
    python src/main.py experiment --name "experiment_name"
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from differential_engine import DifferentialEngine
from differential_engine.engine import mock_llm_callback


def cmd_diagnose(args: argparse.Namespace) -> int:
    """Run a differential diagnosis on input."""
    # Get input
    if args.file:
        input_path = Path(args.file)
        if not input_path.exists():
            print(f"Error: File not found: {args.file}")
            return 1
        raw_input = input_path.read_text(encoding="utf-8")
    elif args.input:
        raw_input = args.input
    else:
        print("Reading from stdin (Ctrl+D to end)...")
        raw_input = sys.stdin.read()
    
    if not raw_input.strip():
        print("Error: No input provided")
        return 1
    
    # Initialize engine
    engine = DifferentialEngine(
        data_dir=Path(args.output_dir) if args.output_dir else None,
        auto_save=not args.no_save,
    )
    
    # Set up LLM callback
    if args.mock:
        print("Using mock LLM callback (for testing)")
        engine.set_llm_callback(mock_llm_callback)
    else:
        # In production, you'd set up real LLM callback here
        # For now, use mock
        print("Note: No LLM callback configured. Using mock responses.")
        print("To use real LLM, implement and set your callback:")
        print("  engine.set_llm_callback(your_llm_function)")
        print()
        engine.set_llm_callback(mock_llm_callback)
    
    # Run diagnosis
    print("=" * 60)
    print("DIFFERENTIAL ENGINE: Starting diagnosis...")
    print("=" * 60)
    print()
    
    result = engine.diagnose(raw_input, interactive=args.interactive)
    
    # Output result
    if args.json:
        import json
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(result.to_markdown())
    
    if not args.no_save:
        sessions_dir = engine.data_dir
        print()
        print(f"Session saved to: {sessions_dir}")
    
    return 0


def cmd_list_sessions(args: argparse.Namespace) -> int:
    """List all saved diagnosis sessions."""
    engine = DifferentialEngine(
        data_dir=Path(args.output_dir) if args.output_dir else None,
    )
    
    sessions = engine.list_sessions()
    
    if not sessions:
        print("No saved sessions found.")
        return 0
    
    print("Saved Sessions:")
    print("-" * 40)
    for session_id in sessions:
        print(f"  {session_id}")
    
    return 0


def cmd_show_session(args: argparse.Namespace) -> int:
    """Show a specific saved session."""
    engine = DifferentialEngine(
        data_dir=Path(args.output_dir) if args.output_dir else None,
    )
    
    result = engine.load_session(args.session_id)
    
    if not result:
        print(f"Session not found: {args.session_id}")
        return 1
    
    if args.json:
        import json
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(result.to_markdown())
    
    return 0


def cmd_handshake(args: argparse.Namespace) -> int:
    """Execute a SWARM handshake protocol (placeholder)."""
    print("SWARM Handshake Protocol")
    print("-" * 40)
    print("This feature is under development.")
    print()
    print("The handshake protocol will:")
    print("1. Exchange cognitive signatures between agents")
    print("2. Establish shared context and goals")
    print("3. Negotiate communication patterns")
    print("4. Initialize collaborative session")
    
    if args.context:
        print()
        print(f"Context file specified: {args.context}")
        context_path = Path(args.context)
        if context_path.exists():
            print(f"Context loaded ({context_path.stat().st_size} bytes)")
        else:
            print("Warning: Context file not found")
    
    return 0


def cmd_experiment(args: argparse.Namespace) -> int:
    """Run a controlled experiment (placeholder)."""
    print("Particle Accelerator: Experiment Mode")
    print("-" * 40)
    print("This feature is under development.")
    print()
    print(f"Experiment name: {args.name}")
    print()
    print("The experiment mode will:")
    print("1. Set up controlled conditions")
    print("2. Run multiple iterations")
    print("3. Collect metrics and outputs")
    print("4. Generate comparative analysis")
    
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Sovereignty Architecture: Sovereign Swarm Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run diagnosis on input text
  python src/main.py diagnose --input "I want to build a system that..."
  
  # Run diagnosis on a file
  python src/main.py diagnose --file thoughts.txt
  
  # Interactive mode with mock LLM
  python src/main.py diagnose --input "my idea" --mock --interactive
  
  # List saved sessions
  python src/main.py sessions list
  
  # Show a specific session
  python src/main.py sessions show 20231215_143022
""",
    )
    
    # Global options
    parser.add_argument(
        "--output-dir",
        "-o",
        help="Directory for saving sessions (default: data/sessions)",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Diagnose command
    diagnose_parser = subparsers.add_parser(
        "diagnose",
        help="Run differential diagnosis on input",
    )
    diagnose_parser.add_argument(
        "--input",
        "-i",
        help="Raw input text to diagnose",
    )
    diagnose_parser.add_argument(
        "--file",
        "-f",
        help="File containing input to diagnose",
    )
    diagnose_parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode (pause between phases)",
    )
    diagnose_parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock LLM callback for testing",
    )
    diagnose_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of markdown",
    )
    diagnose_parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save the session",
    )
    diagnose_parser.set_defaults(func=cmd_diagnose)
    
    # Sessions command
    sessions_parser = subparsers.add_parser(
        "sessions",
        help="Manage saved sessions",
    )
    sessions_subparsers = sessions_parser.add_subparsers(dest="sessions_cmd")
    
    list_parser = sessions_subparsers.add_parser("list", help="List sessions")
    list_parser.set_defaults(func=cmd_list_sessions)
    
    show_parser = sessions_subparsers.add_parser("show", help="Show a session")
    show_parser.add_argument("session_id", help="Session ID to show")
    show_parser.add_argument("--json", action="store_true", help="Output as JSON")
    show_parser.set_defaults(func=cmd_show_session)
    
    # Handshake command
    handshake_parser = subparsers.add_parser(
        "handshake",
        help="Execute SWARM handshake protocol",
    )
    handshake_parser.add_argument(
        "--context",
        "-c",
        help="Context file for handshake",
    )
    handshake_parser.set_defaults(func=cmd_handshake)
    
    # Experiment command
    experiment_parser = subparsers.add_parser(
        "experiment",
        help="Run a controlled experiment",
    )
    experiment_parser.add_argument(
        "--name",
        "-n",
        required=True,
        help="Name of the experiment",
    )
    experiment_parser.set_defaults(func=cmd_experiment)
    
    # Parse args
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    if hasattr(args, "func"):
        return args.func(args)
    else:
        # Handle sessions subcommand without subsubcommand
        if args.command == "sessions" and not args.sessions_cmd:
            return cmd_list_sessions(args)
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
