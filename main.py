#!/usr/bin/env python3
"""
Sovereign Swarm CLI – Absolute-Path / Vim-Only Edition
=======================================================

This is the main orchestrator entrypoint for the Sovereignty Architecture.
It reads CLI args + absolute paths, chooses the right module/experiment,
and hands off to the swarm logic.

LLM Hint: This file serves as the **Swarm Orchestrator** that:
- Reads your CLI args + absolute paths
- Chooses the right module / experiment
- Hands off to the swarm logic

Your Vim + absolute-path CLI ritual is:
    python /abs/path/to/repo/main.py <mode> --input /abs/path/to/data

The swarm lives *inside* this tree and can extend any module.

Usage Examples:
    # Run an experiment
    python main.py experiment --input /abs/path/to/input.json --name my_experiment

    # Analyze logs
    python main.py analyze --input /abs/path/to/logs.json

    # Render/update rituals
    python main.py ritual --name swarm_handshake
"""

import argparse
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("swarm_orchestrator")


def main() -> int:
    """
    Main entrypoint for the Sovereign Swarm CLI.

    This orchestrator:
    - Parses CLI arguments
    - Validates absolute paths
    - Dispatches to swarm modules
    - Returns exit codes for shell integration
    """
    parser = argparse.ArgumentParser(
        description="Sovereign Swarm CLI – absolute-path / vim-only edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py experiment --input /path/to/input.json --name my_experiment
  python main.py analyze --input /path/to/logs.json
  python main.py ritual --name swarm_handshake --update

For more info, see docs/SWARM_METHODOLOGY.md
        """,
    )

    parser.add_argument(
        "mode",
        choices=["experiment", "analyze", "ritual"],
        help="Operation mode: experiment (run), analyze (logs), ritual (docs)",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Absolute path to input file or directory",
    )
    parser.add_argument(
        "--name",
        help="Dynamic name (experiment name or ritual name)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output directory (defaults to logs/ or data/)",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="For ritual mode: update ritual index",
    )
    parser.add_argument(
        "--analysis-type",
        choices=["summary", "deep", "pattern"],
        default="summary",
        help="For analyze mode: type of analysis to perform",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Import swarm modules (delayed import for faster CLI startup)
    from swarm import run_experiment, analyze_logs, render_ritual

    try:
        if args.mode == "experiment":
            return _run_experiment(args, run_experiment)
        elif args.mode == "analyze":
            return _run_analyze(args, analyze_logs)
        elif args.mode == "ritual":
            return _run_ritual(args, render_ritual)
        else:
            logger.error(f"Unknown mode: {args.mode}")
            return 1

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Error during {args.mode}: {e}")
        return 1


def _run_experiment(args, run_experiment):
    """
    Execute experiment mode.

    LLM Hint: Experiments capture traces to logs/ directory.
    The swarm can extend with new experiment types.
    """
    if not args.input:
        logger.error("--input is required for experiment mode")
        return 1

    input_path = args.input.resolve()
    logger.info(f"Running experiment with input: {input_path}")

    result = run_experiment(
        input_path=input_path,
        name=args.name,
        output_dir=args.output.resolve() if args.output else None,
    )

    logger.info(f"Experiment completed: {result['experiment_name']}")
    logger.info(f"Trace saved to: {result['trace_path']}")
    print(f"\n✓ Experiment: {result['experiment_name']}")
    print(f"  Trace: {result['trace_path']}")
    print(f"  Status: {result['status']}")

    return 0


def _run_analyze(args, analyze_logs):
    """
    Execute analyze mode.

    LLM Hint: Analysis outputs structured insights to data/ directory.
    The swarm can extend with specialized analyzers.
    """
    if not args.input:
        logger.error("--input is required for analyze mode")
        return 1

    input_path = args.input.resolve()
    logger.info(f"Analyzing logs from: {input_path}")

    result = analyze_logs(
        input_path=input_path,
        output_dir=args.output.resolve() if args.output else None,
        analysis_type=args.analysis_type,
    )

    logger.info(f"Analysis completed: {result['analysis_type']}")
    logger.info(f"Results saved to: {result['output_path']}")
    print(f"\n✓ Analysis: {result['analysis_type']}")
    print(f"  Input: {result['input_path']}")
    print(f"  Output: {result['output_path']}")
    print(f"  Status: {result['status']}")

    return 0


def _run_ritual(args, render_ritual):
    """
    Execute ritual mode.

    LLM Hint: Rituals are methodology documentation in docs/.
    The swarm can extend with new rituals and protocols.
    """
    logger.info(f"Rendering rituals: {args.name or 'all'}")

    result = render_ritual(
        ritual_name=args.name,
        docs_dir=args.output.resolve() if args.output else None,
        update=args.update,
    )

    if result.get("created"):
        print(f"\n✓ Created new ritual: {result['ritual_name']}")
        print(f"  Path: {result['path']}")
    elif result.get("total_rituals") is not None:
        print(f"\n✓ Found {result['total_rituals']} rituals in {result['docs_dir']}")
        for ritual in result.get("rituals", []):
            print(f"  - {ritual['name']} ({ritual['lines']} lines)")
        if result.get("updated"):
            print("  Index updated")
    else:
        print(f"\n✓ Ritual: {result['ritual_name']}")
        print(f"  Path: {result['path']}")
        print(f"  Content: {result['content_length']} bytes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
