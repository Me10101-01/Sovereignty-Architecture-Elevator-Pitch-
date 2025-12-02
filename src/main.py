#!/usr/bin/env python3
"""
Sovereignty Orchestrator - Main Entry Point
The sovereign orchestrator for the Strategickhaos swarm architecture.

This orchestrator coordinates:
- Differential Engine (House M.D. style debates)
- Session management
- Experiment mode for interactive diagnosis
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime

# Add src to path for imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from differential_engine import DifferentialEngine, SessionManager
from differential_engine.engine import EngineConfig, create_engine


def print_header():
    """Print the sovereignty orchestrator header."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🏛️  SOVEREIGNTY ORCHESTRATOR                                                ║
║  Multi-Agent Differential Diagnosis Engine                                   ║
║  "The swarm doesn't just execute - it thinks, debates, and learns."          ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


def experiment_mode(
    prompt: str,
    symptoms: Optional[List[str]] = None,
    domain: str = "architecture",
    output_dir: str = None,
    context: dict = None,
    verbose: bool = False
) -> dict:
    """
    Run an experiment - a differential diagnosis session.
    
    Args:
        prompt: The problem/question to diagnose
        symptoms: List of symptoms or evidence
        domain: Problem domain
        output_dir: Directory to save session output
        context: Additional context
        verbose: Enable verbose output
        
    Returns:
        Session results as a dictionary
    """
    print_header()
    
    print(f"🔬 Starting differential diagnosis experiment...")
    print(f"📋 Domain: {domain}")
    print(f"❓ Problem: {prompt[:100]}..." if len(prompt) > 100 else f"❓ Problem: {prompt}")
    print()
    
    # Determine sessions directory
    if output_dir:
        sessions_dir = output_dir
    else:
        project_root = Path(__file__).parent.parent
        sessions_dir = project_root / "data" / "sessions"
    
    # Create engine
    engine = create_engine(sessions_dir=str(sessions_dir))
    
    # Run diagnosis
    print("🧠 Invoking differential engine...")
    print("👥 Agents: House, Wilson, Foreman, Cameron, Chase, Cuddy")
    print()
    print("─" * 60)
    
    session = engine.diagnose(
        problem=prompt,
        symptoms=symptoms or [],
        domain=domain,
        context=context or {}
    )
    
    print("─" * 60)
    print()
    
    # Display results
    if verbose:
        print("📜 FULL TRANSCRIPT:")
        print(session.to_markdown())
        print()
    
    # Display summary
    print("═" * 60)
    print("📊 DIAGNOSIS SUMMARY")
    print("═" * 60)
    print()
    
    if session.diagnosis:
        print(f"🎯 Primary Diagnosis:")
        print(f"   {session.diagnosis.primary}")
        print()
        print(f"📈 Confidence: {session.diagnosis.confidence * 100:.0f}%")
        print(f"🔍 Root Cause: {session.diagnosis.root_cause or 'Not determined'}")
        print()
        
        if session.diagnosis.supporting_agents:
            print(f"✅ Supporting Agents: {', '.join(session.diagnosis.supporting_agents)}")
        
        if session.diagnosis.dissenting_views:
            print()
            print("⚠️  Dissenting Views:")
            for view in session.diagnosis.dissenting_views:
                print(f"   - {view['agent']}: {view['view'][:80]}...")
        
        if session.diagnosis.actions:
            print()
            print("📋 Recommended Actions:")
            for i, action in enumerate(session.diagnosis.actions, 1):
                print(f"   {i}. [{action.get('priority', 'NORMAL')}] {action['description']}")
    else:
        print("❌ No diagnosis reached")
    
    print()
    print("═" * 60)
    print()
    print(f"📁 Session saved to: {sessions_dir}")
    print(f"🆔 Session ID: {session.session_id}")
    print(f"⏱️  Duration: {session.duration_seconds:.2f} seconds")
    print()
    
    return session.to_dict()


def list_sessions(
    domain: str = None,
    status: str = None,
    limit: int = 20,
    output_dir: str = None
):
    """List previous diagnosis sessions."""
    print_header()
    
    # Determine sessions directory
    if output_dir:
        sessions_dir = output_dir
    else:
        project_root = Path(__file__).parent.parent
        sessions_dir = project_root / "data" / "sessions"
    
    manager = SessionManager(str(sessions_dir))
    sessions = manager.list_sessions(domain=domain, status=status, limit=limit)
    
    if not sessions:
        print("📭 No sessions found")
        return
    
    print(f"📋 Found {len(sessions)} sessions:")
    print()
    
    for session in sessions:
        status_icon = "✅" if session.get("consensus_reached") else "⚠️"
        confidence = session.get("confidence", 0) or 0
        print(f"  {status_icon} [{session['session_id']}]")
        print(f"     Domain: {session['domain']} | Confidence: {confidence*100:.0f}%")
        print(f"     Problem: {session['problem'][:60]}...")
        print()


def show_session(session_id: str, output_dir: str = None):
    """Show details of a specific session."""
    print_header()
    
    # Determine sessions directory
    if output_dir:
        sessions_dir = output_dir
    else:
        project_root = Path(__file__).parent.parent
        sessions_dir = project_root / "data" / "sessions"
    
    manager = SessionManager(str(sessions_dir))
    session = manager.load_session(session_id)
    
    if not session:
        print(f"❌ Session not found: {session_id}")
        return
    
    print(session.to_markdown())


def get_stats(output_dir: str = None):
    """Get session statistics."""
    print_header()
    
    # Determine sessions directory
    if output_dir:
        sessions_dir = output_dir
    else:
        project_root = Path(__file__).parent.parent
        sessions_dir = project_root / "data" / "sessions"
    
    manager = SessionManager(str(sessions_dir))
    stats = manager.get_session_stats()
    
    print("📊 Session Statistics")
    print("─" * 40)
    print(f"Total Sessions: {stats['total_sessions']}")
    print(f"Average Confidence: {stats['avg_confidence']*100:.1f}%")
    print(f"Consensus Rate: {stats['consensus_rate']*100:.1f}%")
    print()
    
    if stats['by_domain']:
        print("By Domain:")
        for domain, count in stats['by_domain'].items():
            print(f"  - {domain}: {count}")
    print()
    
    if stats['by_status']:
        print("By Status:")
        for status, count in stats['by_status'].items():
            print(f"  - {status}: {count}")


def main():
    """Main entry point for the sovereignty orchestrator."""
    parser = argparse.ArgumentParser(
        description="Sovereignty Orchestrator - Multi-Agent Differential Diagnosis Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run an experiment (differential diagnosis)
  python main.py experiment --prompt "Why is the API slow?" --domain architecture

  # With symptoms/evidence
  python main.py experiment --prompt "Why is the API slow?" \\
    --symptom "Latency spikes to 3s" \\
    --symptom "Memory usage up 40%" \\
    --domain performance

  # List previous sessions
  python main.py sessions list --domain architecture --limit 10

  # Show a specific session
  python main.py sessions show SESSION_ID

  # Get statistics
  python main.py stats
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Experiment command
    exp_parser = subparsers.add_parser("experiment", help="Run a differential diagnosis experiment")
    exp_parser.add_argument("--prompt", "-p", required=True, help="The problem/question to diagnose")
    exp_parser.add_argument("--symptom", "-s", action="append", dest="symptoms", help="Symptom or evidence (can be repeated)")
    exp_parser.add_argument("--domain", "-d", default="architecture", help="Problem domain (default: architecture)")
    exp_parser.add_argument("--output", "-o", dest="output_dir", help="Output directory for session files")
    exp_parser.add_argument("--context", "-c", type=json.loads, help="Additional context as JSON")
    exp_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    exp_parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    # Sessions command
    sess_parser = subparsers.add_parser("sessions", help="Manage diagnosis sessions")
    sess_subparsers = sess_parser.add_subparsers(dest="session_command")
    
    list_parser = sess_subparsers.add_parser("list", help="List sessions")
    list_parser.add_argument("--domain", help="Filter by domain")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--limit", type=int, default=20, help="Maximum sessions to show")
    list_parser.add_argument("--output", dest="output_dir", help="Sessions directory")
    
    show_parser = sess_subparsers.add_parser("show", help="Show a specific session")
    show_parser.add_argument("session_id", help="Session ID to show")
    show_parser.add_argument("--output", dest="output_dir", help="Sessions directory")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show session statistics")
    stats_parser.add_argument("--output", dest="output_dir", help="Sessions directory")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "experiment":
        result = experiment_mode(
            prompt=args.prompt,
            symptoms=args.symptoms,
            domain=args.domain,
            output_dir=args.output_dir,
            context=args.context,
            verbose=args.verbose
        )
        
        if args.json:
            print(json.dumps(result, indent=2, default=str))
            
    elif args.command == "sessions":
        if args.session_command == "list":
            list_sessions(
                domain=args.domain,
                status=args.status,
                limit=args.limit,
                output_dir=args.output_dir
            )
        elif args.session_command == "show":
            show_session(
                session_id=args.session_id,
                output_dir=args.output_dir
            )
        else:
            sess_parser.print_help()
            
    elif args.command == "stats":
        get_stats(output_dir=args.output_dir)


if __name__ == "__main__":
    main()
