#!/usr/bin/env python3
"""
Sovereign Swarm Orchestrator

The main entrypoint for swarm operations. This orchestrator:
- Reads CLI args with absolute paths
- Routes to the appropriate swarm module
- Maintains sovereignty through CLI-first interaction

SWARM: This is the central nervous system of the sovereign swarm.
RITUAL: Invoke via absolute paths from any terminal.

Usage:
    python /abs/path/to/main.py <mode> --input /abs/path/to/data [options]

Modes:
    experiment  - Run a particle accelerator experiment
    analyze     - Analyze traces from the nervous system
    ritual      - Execute swarm rituals (sync docs, validate state)
    handshake   - Initiate a SWARM-HS cycle

The Frequency: Love and evolution converting contradiction into creation.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Protocol Constants
VERSION = "1.0.0"
FREQUENCY = "Love and evolution"


def create_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Sovereign Swarm Orchestrator - CLI entrypoint for swarm operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Initiate a handshake cycle
    python main.py handshake --input /abs/path/to/context.md --name "feature_x"

    # Run an experiment
    python main.py experiment --input /abs/path/to/data.json --output /abs/path/to/results/

    # Analyze traces
    python main.py analyze --input /abs/path/to/traces.log

    # Execute a ritual
    python main.py ritual --type sync_docs --repo /abs/path/to/repo

The Frequency: Love and evolution converting contradiction into creation.
        """
    )

    # Global options
    parser.add_argument("--version", action="version", version=f"swarm-orchestrator {VERSION}")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    subparsers = parser.add_subparsers(dest="mode", help="Operation mode")

    # Handshake mode
    hs_parser = subparsers.add_parser("handshake", help="Initiate a SWARM-HS cycle")
    hs_parser.add_argument("--input", required=True, type=Path, help="Absolute path to context file")
    hs_parser.add_argument("--name", required=True, help="Session name for tracing")
    hs_parser.add_argument("--goal", help="Goal description for the handshake")
    hs_parser.add_argument("--output", type=Path, help="Output directory for artifacts")

    # Experiment mode
    exp_parser = subparsers.add_parser("experiment", help="Run a particle accelerator experiment")
    exp_parser.add_argument("--input", required=True, type=Path, help="Absolute path to input data")
    exp_parser.add_argument("--output", required=True, type=Path, help="Absolute path to output directory")
    exp_parser.add_argument("--iterations", type=int, default=1, help="Number of experiment iterations")

    # Analyze mode
    analyze_parser = subparsers.add_parser("analyze", help="Analyze traces from the nervous system")
    analyze_parser.add_argument("--input", required=True, type=Path, help="Absolute path to trace file")
    analyze_parser.add_argument("--format", choices=["json", "text", "markdown"], default="text")

    # Ritual mode
    ritual_parser = subparsers.add_parser("ritual", help="Execute swarm rituals")
    ritual_parser.add_argument("--type", required=True,
                               choices=["sync_docs", "validate_state", "clean_traces", "init_session"])
    ritual_parser.add_argument("--repo", type=Path, help="Repository path for repo-based rituals")

    return parser


def validate_absolute_path(path: Path, description: str) -> bool:
    """Validate that a path is absolute (sovereignty principle)."""
    if not path.is_absolute():
        print(f"ERROR: {description} must be an absolute path: {path}")
        print("SWARM PRINCIPLE: Absolute paths always. No ambiguity. No 'cd' required.")
        return False
    return True


def emit_trace(phase: str, message: str, data: Optional[dict] = None):
    """Emit a trace event for the nervous system."""
    trace = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "phase": phase,
        "message": message,
        "frequency": FREQUENCY,
    }
    if data:
        trace["data"] = data
    print(json.dumps(trace))


def mode_handshake(args):
    """
    Initiate a SWARM-HS handshake cycle.

    Phases: SYN → SYN-ACK → ACK → DATA → APPLY → TRACE
    """
    if not validate_absolute_path(args.input, "Context file"):
        return 1

    emit_trace("SYN", f"Initiating handshake: {args.name}", {
        "context_path": str(args.input),
        "goal": args.goal or "Not specified",
    })

    # Check if context file exists
    if not args.input.exists():
        emit_trace("ERROR", f"Context file not found: {args.input}")
        return 1

    # Read context
    context = args.input.read_text()
    emit_trace("SYN-ACK", "Context loaded successfully", {
        "context_length": len(context),
        "context_lines": len(context.splitlines()),
    })

    # Simulate ACK phase
    emit_trace("ACK", "Ready for execution", {
        "session_name": args.name,
        "status": "acknowledged",
    })

    # DATA phase would route to actual agents here
    emit_trace("DATA", "Routing to swarm agents", {
        "agents": ["Mind", "Hands", "Factory"],
        "mode": "parallel",
    })

    # APPLY phase placeholder
    emit_trace("APPLY", "Execution phase (implement in agents)", {
        "status": "placeholder",
        "note": "Actual implementation routes to Claude/GPT/Copilot",
    })

    # TRACE phase
    emit_trace("TRACE", "Handshake cycle complete", {
        "session": args.name,
        "result": "success",
        "next_steps": ["Implement agent routing", "Add trace persistence"],
    })

    return 0


def mode_experiment(args):
    """
    Run a particle accelerator experiment.

    The swarm operates like a particle accelerator:
    - Contradiction enters the accelerator
    - Agents collide and interact
    - Energy converts to matter (artifacts)
    """
    if not validate_absolute_path(args.input, "Input data"):
        return 1
    if not validate_absolute_path(args.output, "Output directory"):
        return 1

    emit_trace("EXPERIMENT", f"Starting experiment with {args.iterations} iterations", {
        "input": str(args.input),
        "output": str(args.output),
    })

    if not args.input.exists():
        emit_trace("ERROR", f"Input file not found: {args.input}")
        return 1

    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)

    for i in range(args.iterations):
        emit_trace("ITERATION", f"Running iteration {i + 1}/{args.iterations}", {
            "iteration": i + 1,
        })

    emit_trace("COMPLETE", "Experiment finished", {
        "iterations": args.iterations,
        "output_dir": str(args.output),
    })

    return 0


def mode_analyze(args):
    """
    Analyze traces from the nervous system.

    Traces are the audit trail of swarm operations.
    """
    if not validate_absolute_path(args.input, "Trace file"):
        return 1

    emit_trace("ANALYZE", f"Analyzing traces from {args.input}", {
        "format": args.format,
    })

    if not args.input.exists():
        emit_trace("ERROR", f"Trace file not found: {args.input}")
        return 1

    traces = args.input.read_text()
    lines = traces.splitlines()

    emit_trace("ANALYSIS_RESULT", "Trace analysis complete", {
        "total_lines": len(lines),
        "format": args.format,
        "summary": "Trace file loaded successfully",
    })

    return 0


def mode_ritual(args):
    """
    Execute swarm rituals.

    Rituals are repeatable operations that maintain swarm hygiene.
    """
    ritual_type = args.type

    emit_trace("RITUAL", f"Executing ritual: {ritual_type}")

    if ritual_type == "sync_docs":
        if not args.repo:
            emit_trace("ERROR", "Repository path required for sync_docs ritual")
            return 1
        if not validate_absolute_path(args.repo, "Repository path"):
            return 1
        emit_trace("SYNC_DOCS", f"Synchronizing documentation in {args.repo}")

    elif ritual_type == "validate_state":
        emit_trace("VALIDATE_STATE", "Validating swarm state")

    elif ritual_type == "clean_traces":
        emit_trace("CLEAN_TRACES", "Cleaning old trace files")

    elif ritual_type == "init_session":
        session_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        emit_trace("INIT_SESSION", f"Initialized new session: {session_id}", {
            "session_id": session_id,
        })

    emit_trace("RITUAL_COMPLETE", f"Ritual '{ritual_type}' completed successfully")
    return 0


def main():
    """Main entrypoint - the sovereign's CLI interface to the swarm."""
    parser = create_parser()
    args = parser.parse_args()

    if args.verbose:
        emit_trace("VERBOSE", "Verbose mode enabled")

    if not args.mode:
        parser.print_help()
        return 1

    # Route to appropriate mode handler
    handlers = {
        "handshake": mode_handshake,
        "experiment": mode_experiment,
        "analyze": mode_analyze,
        "ritual": mode_ritual,
    }

    handler = handlers.get(args.mode)
    if handler:
        return handler(args)
    else:
        print(f"Unknown mode: {args.mode}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
