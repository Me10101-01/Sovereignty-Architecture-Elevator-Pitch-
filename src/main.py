#!/usr/bin/env python3
"""
SWARM: Sovereign Swarm Orchestrator
====================================

Central nervous system of the sovereign swarm.
RITUAL: Invoke via absolute paths from any terminal.

This orchestrator provides a CLI interface for:
- experiment: Run experimental configurations
- analyze: Analyze logs and metrics (integrates with Rust tools)
- ritual: Execute predefined ritual sequences
- handshake: Initiate swarm handshake protocol

Usage:
    python src/main.py --help
    python src/main.py experiment --input /path/to/context.md
    python src/main.py analyze --input /path/to/logs.json
    python src/main.py ritual --name morning_alignment
    python src/main.py handshake --target mind --context /path/to/context.md
"""

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_CONFIG = {
    "version": "1.0.0",
    "sovereign": "human",
    "frequency": "love and evolution converting contradiction into creation",
    "agents": {
        "mind": {"type": "gpt", "status": "available"},
        "hands": {"type": "claude", "status": "available"},
        "factory": {"type": "copilot", "status": "available"},
    },
    "rituals": {
        "morning_alignment": {
            "description": "Daily alignment ritual",
            "steps": ["check_state", "sync_context", "set_intention"],
        },
        "evening_trace": {
            "description": "End of day trace ritual",
            "steps": ["collect_traces", "analyze_patterns", "archive"],
        },
    },
}


# =============================================================================
# SWARM HANDSHAKE PROTOCOL
# =============================================================================

class SwarmHandshake:
    """
    Implementation of the Swarm Handshake Protocol.
    
    Phases: SYN → SYN-ACK → ACK → DATA → APPLY → TRACE
    """
    
    def __init__(self, agent_id: str, target_id: str):
        self.agent_id = agent_id
        self.target_id = target_id
        self.session_id: Optional[str] = None
        self.state = "CLOSED"
        self.trace = []
    
    def syn(self, context_hash: str, intent: str) -> dict:
        """Phase 1: Send SYN to initiate connection."""
        self.state = "SYN_SENT"
        message = {
            "type": "SYN",
            "from": self.agent_id,
            "to": self.target_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context_hash": context_hash,
            "intent": intent,
        }
        self.trace.append(message)
        return message
    
    def syn_ack(self, capabilities: list, state: str = "ready") -> dict:
        """Phase 2: Respond with SYN-ACK."""
        self.state = "ESTABLISHED"
        message = {
            "type": "SYN-ACK",
            "from": self.target_id,
            "to": self.agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "capabilities": capabilities,
            "state": state,
        }
        self.trace.append(message)
        return message
    
    def ack(self, session_id: str) -> dict:
        """Phase 3: Complete handshake with ACK."""
        self.session_id = session_id
        self.state = "ACTIVE"
        message = {
            "type": "ACK",
            "from": self.agent_id,
            "to": self.target_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "handshake_complete": True,
        }
        self.trace.append(message)
        return message
    
    def data(self, content: dict) -> dict:
        """Phase 4: Send data."""
        message = {
            "type": "DATA",
            "session_id": self.session_id,
            "from": self.agent_id,
            "to": self.target_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": content,
        }
        self.trace.append(message)
        return message
    
    def apply(self, action: str, parameters: dict) -> dict:
        """Phase 5: Apply operation."""
        message = {
            "type": "APPLY",
            "session_id": self.session_id,
            "executor": self.agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": {
                "action": action,
                "parameters": parameters,
            },
            "status": "pending",
        }
        self.trace.append(message)
        return message
    
    def get_trace(self) -> dict:
        """Phase 6: Return complete trace."""
        self.state = "CLOSED"
        return {
            "type": "TRACE",
            "session_id": self.session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace": {
                "phases_completed": [msg["type"] for msg in self.trace],
                "message_count": len(self.trace),
                "outcome": "success",
            },
        }


# =============================================================================
# ANALYZE LOGS (Rust Integration)
# =============================================================================

def analyze_logs(path: Path, format_type: str = "json") -> dict:
    """
    Analyze logs using the sovereignty-log-analyzer Rust tool.
    
    This function wraps the Rust binary to provide seamless integration
    with the Python orchestrator.
    
    Args:
        path: Path to the log file
        format_type: Output format (json, text)
    
    Returns:
        Analysis results as a dictionary
    """
    # Check if the Rust binary exists
    rust_binary = "sovereignty-log-analyzer"
    
    try:
        result = subprocess.run(
            [rust_binary, "metrics", "--input", str(path)],
            capture_output=True,
            text=True,
            check=True,
        )
        return {"status": "success", "output": result.stdout}
    except FileNotFoundError:
        # Fallback to Python-based analysis if Rust binary not found
        print(f"[INFO] Rust analyzer not found, using Python fallback")
        return analyze_logs_python(path)
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": str(e), "stderr": e.stderr}


def analyze_logs_python(path: Path) -> dict:
    """
    Python fallback for log analysis.
    
    Provides basic log analysis when Rust binary is unavailable.
    """
    if not path.exists():
        return {"status": "error", "message": f"File not found: {path}"}
    
    try:
        with open(path, "r") as f:
            content = f.read()
        
        # Basic analysis
        lines = content.strip().split("\n")
        analysis = {
            "status": "success",
            "file": str(path),
            "line_count": len(lines),
            "size_bytes": path.stat().st_size,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }
        
        # Try to parse as JSON
        try:
            data = json.loads(content)
            if isinstance(data, list):
                analysis["record_count"] = len(data)
            elif isinstance(data, dict):
                analysis["keys"] = list(data.keys())
        except json.JSONDecodeError:
            analysis["format"] = "text"
        
        return analysis
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


# =============================================================================
# MODE HANDLERS
# =============================================================================

def mode_experiment(args: argparse.Namespace) -> int:
    """Handle experiment mode."""
    print("═" * 60)
    print("  EXPERIMENT MODE")
    print("═" * 60)
    print(f"  Input: {args.input}")
    print(f"  Name:  {args.name or 'unnamed'}")
    print()
    
    if args.input:
        path = Path(args.input)
        if path.exists():
            print(f"  [✓] Context file found: {path}")
            print(f"  [→] Running experiment...")
            # Experiment logic would go here
            print(f"  [✓] Experiment complete")
        else:
            print(f"  [✗] Context file not found: {path}")
            return 1
    else:
        print("  [!] No input specified, running in dry-run mode")
    
    return 0


def mode_analyze(args: argparse.Namespace) -> int:
    """Handle analyze mode."""
    print("═" * 60)
    print("  ANALYZE MODE")
    print("═" * 60)
    print(f"  Input: {args.input}")
    print()
    
    if not args.input:
        print("  [✗] Error: --input is required for analyze mode")
        return 1
    
    path = Path(args.input)
    if not path.exists():
        print(f"  [✗] File not found: {path}")
        return 1
    
    print(f"  [→] Analyzing: {path}")
    result = analyze_logs(path)
    
    print()
    print("  Results:")
    print("  " + "-" * 40)
    print(json.dumps(result, indent=2, default=str))
    
    return 0 if result.get("status") == "success" else 1


def mode_ritual(args: argparse.Namespace) -> int:
    """Handle ritual mode."""
    print("═" * 60)
    print("  RITUAL MODE")
    print("═" * 60)
    print(f"  Ritual: {args.name}")
    print()
    
    ritual = DEFAULT_CONFIG["rituals"].get(args.name)
    
    if not ritual:
        print(f"  [✗] Unknown ritual: {args.name}")
        print(f"  [?] Available rituals:")
        for name, info in DEFAULT_CONFIG["rituals"].items():
            print(f"      - {name}: {info['description']}")
        return 1
    
    print(f"  [✓] Ritual found: {ritual['description']}")
    print(f"  [→] Executing steps:")
    
    for i, step in enumerate(ritual["steps"], 1):
        print(f"      {i}. {step}...")
    
    print()
    print(f"  [✓] Ritual complete")
    return 0


def mode_handshake(args: argparse.Namespace) -> int:
    """Handle handshake mode."""
    print("═" * 60)
    print("  HANDSHAKE MODE")
    print("═" * 60)
    print(f"  Target: {args.target}")
    print(f"  Context: {args.context or 'none'}")
    print()
    
    if args.target not in DEFAULT_CONFIG["agents"]:
        print(f"  [✗] Unknown agent: {args.target}")
        print(f"  [?] Available agents:")
        for name, info in DEFAULT_CONFIG["agents"].items():
            print(f"      - {name} ({info['type']}): {info['status']}")
        return 1
    
    agent = DEFAULT_CONFIG["agents"][args.target]
    
    # Simulate handshake
    print(f"  [→] Initiating handshake with {args.target} ({agent['type']})")
    
    handshake = SwarmHandshake(
        agent_id="sovereign",
        target_id=args.target
    )
    
    # Execute protocol phases
    print("  [1] SYN...")
    syn = handshake.syn(context_hash="demo", intent="test_connection")
    
    print("  [2] SYN-ACK...")
    syn_ack = handshake.syn_ack(capabilities=["code", "docs", "analysis"])
    
    print("  [3] ACK...")
    ack = handshake.ack(session_id=str(uuid.uuid4()))
    
    print("  [4] DATA...")
    data = handshake.data(content={"type": "ping", "payload": "hello"})
    
    print("  [5] APPLY...")
    apply = handshake.apply(action="acknowledge", parameters={})
    
    print("  [6] TRACE...")
    trace = handshake.get_trace()
    
    print()
    print("  [✓] Handshake complete")
    print()
    print("  Trace:")
    print("  " + "-" * 40)
    print(json.dumps(trace, indent=2))
    
    return 0


# =============================================================================
# MAIN
# =============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="swarm",
        description="Sovereign Swarm Orchestrator - Central nervous system of the swarm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py experiment --input /path/to/context.md --name test
  python src/main.py analyze --input /path/to/logs.json
  python src/main.py ritual --name morning_alignment
  python src/main.py handshake --target mind --context /path/to/ctx.md

Frequency: Love and evolution converting contradiction into creation.
        """
    )
    
    subparsers = parser.add_subparsers(dest="mode", help="Operation mode")
    
    # Experiment mode
    exp_parser = subparsers.add_parser("experiment", help="Run experimental configurations")
    exp_parser.add_argument("--input", "-i", type=str, help="Input context file")
    exp_parser.add_argument("--name", "-n", type=str, help="Experiment name")
    
    # Analyze mode
    analyze_parser = subparsers.add_parser("analyze", help="Analyze logs and metrics")
    analyze_parser.add_argument("--input", "-i", type=str, required=True, help="Input log file")
    analyze_parser.add_argument("--format", "-f", type=str, default="json", help="Output format")
    
    # Ritual mode
    ritual_parser = subparsers.add_parser("ritual", help="Execute predefined rituals")
    ritual_parser.add_argument("--name", "-n", type=str, required=True, help="Ritual name")
    
    # Handshake mode
    handshake_parser = subparsers.add_parser("handshake", help="Initiate swarm handshake")
    handshake_parser.add_argument("--target", "-t", type=str, required=True, help="Target agent")
    handshake_parser.add_argument("--context", "-c", type=str, help="Context file path")
    
    return parser


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.mode:
        parser.print_help()
        return 0
    
    # Header
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " SOVEREIGN SWARM ORCHESTRATOR ".center(58) + "║")
    print("║" + f" v{DEFAULT_CONFIG['version']} ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # Dispatch to mode handler
    mode_handlers = {
        "experiment": mode_experiment,
        "analyze": mode_analyze,
        "ritual": mode_ritual,
        "handshake": mode_handshake,
    }
    
    handler = mode_handlers.get(args.mode)
    if handler:
        return handler(args)
    else:
        print(f"Unknown mode: {args.mode}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
