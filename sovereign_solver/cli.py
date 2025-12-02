"""
CLI Interface for Sovereign Methodology Solver

Command-line interface for manual orchestration and interaction
with the autonomous methodology solver.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from .core import SovereignSolver, SolverConfig, SolverMode


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser"""
    parser = argparse.ArgumentParser(
        prog="sovereign",
        description="Sovereign Methodology Solver - Autonomous multi-agent orchestration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sovereign init                    Initialize the solver
  sovereign observe                 Observe current state
  sovereign analyze                 Analyze patterns
  sovereign ritual create my-flow   Create a new ritual
  sovereign ritual run my-flow      Run a ritual
  sovereign evolve                  Run self-improvement cycle
  sovereign status                  Show system status
        """
    )

    parser.add_argument(
        "--workspace", "-w",
        type=Path,
        default=Path.cwd(),
        help="Workspace root directory"
    )

    parser.add_argument(
        "--mode", "-m",
        choices=["manual", "supervised", "autonomous"],
        default="supervised",
        help="Operating mode"
    )

    parser.add_argument(
        "--output", "-o",
        choices=["json", "text"],
        default="text",
        help="Output format"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    subparsers.add_parser("init", help="Initialize the solver")

    # Observe command
    subparsers.add_parser("observe", help="Observe current state across all nodes")

    # Analyze command
    subparsers.add_parser("analyze", help="Analyze patterns in the system")

    # Status command
    subparsers.add_parser("status", help="Show system status")

    # Evolve command
    subparsers.add_parser("evolve", help="Run self-improvement cycle")

    # Ritual commands
    ritual_parser = subparsers.add_parser("ritual", help="Ritual management")
    ritual_subparsers = ritual_parser.add_subparsers(dest="ritual_command")

    # ritual list
    ritual_subparsers.add_parser("list", help="List all rituals")

    # ritual create
    ritual_create = ritual_subparsers.add_parser("create", help="Create a new ritual")
    ritual_create.add_argument("name", help="Ritual name")
    ritual_create.add_argument(
        "--trigger", "-t",
        default="manual",
        help="Trigger type"
    )
    ritual_create.add_argument(
        "--description", "-d",
        default="",
        help="Ritual description"
    )
    ritual_create.add_argument(
        "--template",
        help="Use a template"
    )
    ritual_create.add_argument(
        "--tags",
        nargs="*",
        default=[],
        help="Tags for the ritual"
    )

    # ritual run
    ritual_run = ritual_subparsers.add_parser("run", help="Run a ritual")
    ritual_run.add_argument("ritual_id", help="Ritual ID or name")

    # ritual show
    ritual_show = ritual_subparsers.add_parser("show", help="Show ritual details")
    ritual_show.add_argument("ritual_id", help="Ritual ID or name")

    # Reflex commands
    reflex_parser = subparsers.add_parser("reflex", help="Reflex management")
    reflex_subparsers = reflex_parser.add_subparsers(dest="reflex_command")

    # reflex list
    reflex_subparsers.add_parser("list", help="List all reflexes")

    # reflex create
    reflex_create = reflex_subparsers.add_parser("create", help="Create a new reflex")
    reflex_create.add_argument("name", help="Reflex name")
    reflex_create.add_argument("--pattern", "-p", required=True, help="Trigger pattern")
    reflex_create.add_argument(
        "--category", "-c",
        default="workflow",
        help="Reflex category"
    )
    reflex_create.add_argument(
        "--action", "-a",
        default="log",
        help="Action type"
    )

    # Knowledge commands
    knowledge_parser = subparsers.add_parser("knowledge", help="Knowledge management")
    knowledge_subparsers = knowledge_parser.add_subparsers(dest="knowledge_command")

    # knowledge store
    knowledge_store = knowledge_subparsers.add_parser("store", help="Store knowledge")
    knowledge_store.add_argument("key", help="Knowledge key")
    knowledge_store.add_argument("value", help="Knowledge value")

    # knowledge get
    knowledge_get = knowledge_subparsers.add_parser("get", help="Get knowledge")
    knowledge_get.add_argument("key", help="Knowledge key")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export system state")
    export_parser.add_argument(
        "--file", "-f",
        type=Path,
        help="Export to file"
    )

    return parser


def format_output(data: dict, format_type: str) -> str:
    """Format output based on type"""
    if format_type == "json":
        return json.dumps(data, indent=2, default=str)
    else:
        return format_text(data)


def format_text(data: dict, indent: int = 0) -> str:
    """Format data as readable text"""
    lines = []
    prefix = "  " * indent

    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(format_text(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}{key}:")
            for item in value:
                if isinstance(item, dict):
                    lines.append(format_text(item, indent + 1))
                else:
                    lines.append(f"{prefix}  - {item}")
        else:
            lines.append(f"{prefix}{key}: {value}")

    return "\n".join(lines)


def main(args: list[str] | None = None):
    """Main entry point for the CLI"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 0

    # Create config
    mode_map = {
        "manual": SolverMode.MANUAL,
        "supervised": SolverMode.SUPERVISED,
        "autonomous": SolverMode.AUTONOMOUS
    }

    config = SolverConfig(
        workspace_root=parsed_args.workspace,
        mode=mode_map[parsed_args.mode]
    )

    solver = SovereignSolver(config)

    output_format = parsed_args.output

    try:
        result = handle_command(solver, parsed_args)
        if result:
            print(format_output(result, output_format))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_command(solver: SovereignSolver, args) -> dict | None:
    """Handle a command and return result"""
    command = args.command

    if command == "init":
        solver.initialize()
        return {"status": "initialized", "session_id": solver.session_id}

    elif command == "observe":
        solver.initialize()
        return solver.observe()

    elif command == "analyze":
        solver.initialize()
        return solver.analyze()

    elif command == "status":
        solver.initialize()
        return solver.get_status()

    elif command == "evolve":
        solver.initialize()
        return solver.evolve()

    elif command == "ritual":
        return handle_ritual_command(solver, args)

    elif command == "reflex":
        return handle_reflex_command(solver, args)

    elif command == "knowledge":
        return handle_knowledge_command(solver, args)

    elif command == "export":
        solver.initialize()
        state = solver.export_state()
        if args.file:
            solver.save_state(args.file)
            return {"status": "exported", "file": str(args.file)}
        return state

    return None


def handle_ritual_command(solver: SovereignSolver, args) -> dict | None:
    """Handle ritual subcommands"""
    solver.initialize()
    ritual_cmd = args.ritual_command

    if ritual_cmd == "list":
        return {"rituals": solver.get_rituals()}

    elif ritual_cmd == "create":
        ritual = solver.generate_ritual(
            name=args.name,
            trigger=args.trigger,
            description=args.description,
            template=args.template,
            tags=args.tags
        )
        return {
            "status": "created",
            "ritual_id": ritual.ritual_id,
            "name": ritual.name
        }

    elif ritual_cmd == "run":
        return solver.run_ritual(args.ritual_id)

    elif ritual_cmd == "show":
        rituals = solver.get_rituals()
        for ritual in rituals:
            if ritual["ritual_id"] == args.ritual_id or ritual["name"] == args.ritual_id:
                return ritual
        return {"error": "Ritual not found"}

    return None


def handle_reflex_command(solver: SovereignSolver, args) -> dict | None:
    """Handle reflex subcommands"""
    solver.initialize()
    reflex_cmd = args.reflex_command

    if reflex_cmd == "list":
        return {"reflexes": solver.get_reflexes()}

    elif reflex_cmd == "create":
        reflex = solver._reflex_system.create_reflex(
            name=args.name,
            trigger_pattern=args.pattern,
            trigger_category=args.category,
            action_type=args.action
        )
        return {
            "status": "created",
            "reflex_id": reflex.reflex_id,
            "name": reflex.name
        }

    return None


def handle_knowledge_command(solver: SovereignSolver, args) -> dict | None:
    """Handle knowledge subcommands"""
    solver.initialize()
    knowledge_cmd = args.knowledge_command

    if knowledge_cmd == "store":
        success = solver.store_knowledge(args.key, args.value)
        return {"status": "stored" if success else "failed", "key": args.key}

    elif knowledge_cmd == "get":
        value = solver.retrieve_knowledge(args.key)
        if value:
            return {"key": args.key, "value": value}
        return {"error": "Key not found"}

    return None


if __name__ == "__main__":
    sys.exit(main())
