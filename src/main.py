#!/usr/bin/env python3
"""
SOVEREIGN SWARM ORCHESTRATOR
============================
Central nervous system of the sovereignty architecture.

RITUAL: Invoke via absolute paths from any terminal.
PROTOCOL: TCP-handshake style multi-agent coordination.
SOVEREIGN: You are the router. This is your control plane.

Usage:
    python /abs/path/to/repo/src/main.py experiment --input /abs/path/to/context.md --name "my_experiment"
    python /abs/path/to/repo/src/main.py analyze --input /abs/path/to/logs.json
    python /abs/path/to/repo/src/main.py ritual --input /abs/path/to/docs/
    python /abs/path/to/repo/src/main.py handshake --input /abs/path/to/context.md --name "swarm_sync"

The swarm lives *inside* this tree. LLMs read this file as their constitution.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Ensure src directory is in path for direct script execution
# This is needed when running as: python src/main.py (not as a package)
_src_dir = Path(__file__).parent
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

from swarm import (
    run_experiment,
    analyze_logs,
    execute_ritual,
    handshake_protocol,
    SwarmOrchestrator,
    SWARM_VERSION,
)


def log_operation(operation: str, details: dict, verbose: bool = False) -> None:
    """
    Log operation to stdout and optionally to file.
    
    LLM DIRECTIVE: All operations should be logged for traceability.
    """
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "operation": operation,
        "details": details,
    }
    
    if verbose:
        print(json.dumps(log_entry, indent=2))
    else:
        print(f"[{timestamp}] {operation}: {details.get('status', 'started')}")


def cmd_experiment(args: argparse.Namespace) -> int:
    """
    Execute an experiment.
    
    LLM DIRECTIVE: Experiments are the particle accelerator of the swarm.
    Each experiment collides ideas and produces artifacts.
    """
    log_operation("experiment", {"name": args.name, "input": args.input}, args.verbose)
    
    result = run_experiment(
        name=args.name,
        input_path=args.input,
        config={"verbose": args.verbose},
    )
    
    log_operation("experiment", result, args.verbose)
    print(json.dumps(result, indent=2))
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    """
    Analyze logs.
    
    LLM DIRECTIVE: Analysis converts raw telemetry into actionable insight.
    """
    log_operation("analyze", {"input": args.input, "name": args.name}, args.verbose)
    
    result = analyze_logs(
        input_path=args.input,
        output_path=args.output,
        analyzers=args.analyzers.split(",") if args.analyzers else None,
    )
    
    log_operation("analyze", result, args.verbose)
    print(json.dumps(result, indent=2))
    return 0


def cmd_ritual(args: argparse.Namespace) -> int:
    """
    Execute a ritual.
    
    LLM DIRECTIVE: Rituals are ceremonial operations that establish shared context.
    """
    log_operation("ritual", {"input": args.input, "type": args.type}, args.verbose)
    
    result = execute_ritual(
        input_path=args.input,
        ritual_type=args.type,
    )
    
    log_operation("ritual", result, args.verbose)
    print(json.dumps(result, indent=2))
    return 0


def cmd_handshake(args: argparse.Namespace) -> int:
    """
    Execute the handshake protocol.
    
    LLM DIRECTIVE: The handshake is the TCP of AI coordination.
    SYN -> SYN-ACK -> ACK -> DATA -> APPLY -> TRACE
    """
    log_operation("handshake", {"input": args.input, "name": args.name}, args.verbose)
    
    agents = args.agents.split(",") if args.agents else None
    result = handshake_protocol(
        input_path=args.input,
        agents=agents,
    )
    
    log_operation("handshake", result, args.verbose)
    print(json.dumps(result, indent=2))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """
    Get swarm status.
    
    LLM DIRECTIVE: Status provides visibility into the swarm state.
    """
    orchestrator = SwarmOrchestrator()
    status = orchestrator.get_status()
    
    print(json.dumps(status, indent=2))
    return 0


def main() -> int:
    """
    Main entry point for the Sovereign Swarm Orchestrator.
    
    LLM DIRECTIVE: This is your control plane. Extend with new subcommands as needed.
    """
    parser = argparse.ArgumentParser(
        description="Sovereign Swarm Orchestrator - Control plane for LLM-driven swarm development",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python src/main.py experiment --input /path/to/context.md --name "particle_collider_001"
    python src/main.py analyze --input /path/to/logs.json --name "cluster_analysis"
    python src/main.py ritual --input /path/to/docs/ --type sync
    python src/main.py handshake --input /path/to/context.md --name "swarm_sync"
    python src/main.py status

Protocol: TCP-handshake style multi-agent coordination
Version: {version}
        """.format(version=SWARM_VERSION),
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Experiment command
    exp_parser = subparsers.add_parser(
        "experiment",
        help="Run a swarm experiment",
    )
    exp_parser.add_argument(
        "--input", "-i",
        required=True,
        help="Absolute path to input context file",
    )
    exp_parser.add_argument(
        "--name", "-n",
        required=True,
        help="Experiment name (will be augmented with timestamp)",
    )
    exp_parser.set_defaults(func=cmd_experiment)
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze log files",
    )
    analyze_parser.add_argument(
        "--input", "-i",
        required=True,
        help="Absolute path to log file or directory",
    )
    analyze_parser.add_argument(
        "--name", "-n",
        default="analysis",
        help="Analysis name",
    )
    analyze_parser.add_argument(
        "--output", "-o",
        help="Output path for analysis results",
    )
    analyze_parser.add_argument(
        "--analyzers", "-a",
        help="Comma-separated list of analyzers to run",
    )
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # Ritual command
    ritual_parser = subparsers.add_parser(
        "ritual",
        help="Execute a synchronization ritual",
    )
    ritual_parser.add_argument(
        "--input", "-i",
        required=True,
        help="Absolute path to ritual context files",
    )
    ritual_parser.add_argument(
        "--type", "-t",
        default="sync",
        choices=["sync", "bootstrap", "checkpoint", "handoff"],
        help="Type of ritual to execute",
    )
    ritual_parser.set_defaults(func=cmd_ritual)
    
    # Handshake command
    handshake_parser = subparsers.add_parser(
        "handshake",
        help="Execute the TCP-style handshake protocol",
    )
    handshake_parser.add_argument(
        "--input", "-i",
        required=True,
        help="Absolute path to context file for handshake",
    )
    handshake_parser.add_argument(
        "--name", "-n",
        default="handshake",
        help="Handshake name",
    )
    handshake_parser.add_argument(
        "--agents", "-a",
        help="Comma-separated list of agents to include",
    )
    handshake_parser.set_defaults(func=cmd_handshake)
    
    # Status command
    status_parser = subparsers.add_parser(
        "status",
        help="Get swarm status",
    )
    status_parser.set_defaults(func=cmd_status)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
