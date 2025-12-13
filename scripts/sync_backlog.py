#!/usr/bin/env python3
"""
Backlog Sync - ADHD-Friendly Task Focus
Strategickhaos DAO LLC — Swarm Intelligence Backlog Sync

Reads board_meeting.yaml and extracts incomplete tasks from left/right hemispheres.
Respects max_parallel_tracks (default: 2) so your brain doesn't get swarmed.
"""

import sys
import re
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    print("❌ PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)


def find_board_meeting_yaml(repo_root: Path) -> Path | None:
    """Find the latest board_meeting YAML file in the repo."""
    yamls = sorted(repo_root.glob("board_meeting*.yaml"), reverse=True)
    return yamls[0] if yamls else None


def extract_incomplete_tasks(checkboxes: list[str]) -> list[str]:
    """Extract incomplete tasks ([ ]) from a checkbox list.
    
    Matches checkbox patterns like:
    - [ ] Task description
    - "[ ] Task description"
    - '[ ] Task description'
    """
    incomplete = []
    # Pattern: optional quotes, opening bracket, optional space, closing bracket
    unchecked_pattern = r'^\s*[\"\']?\[\s*\]'
    for item in checkboxes:
        if re.match(unchecked_pattern, item):
            # Remove the checkbox prefix and clean up
            task = re.sub(unchecked_pattern + r'\s*', '', item)
            task = task.strip('"\'')
            incomplete.append(task)
    return incomplete


def load_board_meeting(yaml_path: Path) -> dict:
    """Load and parse the board meeting YAML."""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_adhd_rules(board: dict) -> dict:
    """Extract ADHD sanity rules from the board meeting."""
    default_rules = {
        "max_parallel_tracks": 2,
        "sprint_minutes": [25, 50, 90],
        "hemisphere_balance": "Left 50% — Right 50%"
    }
    
    meeting = board.get("board_meeting", {})
    rules = meeting.get("adhd_sanity_rules", {})
    
    return {
        "max_parallel_tracks": rules.get("max_parallel_tracks", default_rules["max_parallel_tracks"]),
        "sprint_minutes": rules.get("sprint_minutes", default_rules["sprint_minutes"]),
        "hemisphere_balance": rules.get("hemisphere_balance", default_rules["hemisphere_balance"])
    }


def get_hemisphere_tasks(board: dict) -> dict:
    """Extract incomplete tasks from left and right hemispheres."""
    meeting = board.get("board_meeting", {})
    tracks = meeting.get("tracks", {})
    
    hemispheres = {}
    
    # Left hemisphere (precision)
    left = tracks.get("left_hemisphere", {})
    hemispheres["left"] = {
        "name": "Left Hemisphere (Precision)",
        "label": left.get("label", "Tax, Treasury, Compliance"),
        "status_pct": left.get("status_pct", 0),
        "owner": left.get("owner", "Unknown"),
        "tasks": extract_incomplete_tasks(left.get("checkboxes", []))
    }
    
    # Right hemisphere (chaos)
    right = tracks.get("right_hemisphere", {})
    hemispheres["right"] = {
        "name": "Right Hemisphere (Chaos)",
        "label": right.get("label", "Agents, NFTs, experimental"),
        "status_pct": right.get("status_pct", 0),
        "owner": right.get("owner", "Unknown"),
        "tasks": extract_incomplete_tasks(right.get("checkboxes", []))
    }
    
    return hemispheres


def get_immediate_actions(board: dict) -> list[dict]:
    """Extract immediate next actions from the board meeting."""
    meeting = board.get("board_meeting", {})
    next_actions = meeting.get("next_actions", {})
    immediate = next_actions.get("immediate", [])
    
    return [
        {
            "action": item.get("action", "Unknown"),
            "owner": item.get("owner", "Unknown"),
            "time": item.get("time", "Unknown")
        }
        for item in immediate
    ]


def get_blockers(board: dict) -> list[str]:
    """Extract blockers from the board meeting summary."""
    meeting = board.get("board_meeting", {})
    summary = meeting.get("summary", {})
    return summary.get("blockers", [])


def print_focus_view(yaml_path: Path, max_tasks: int = 2):
    """Print the ADHD-friendly focus view."""
    board = load_board_meeting(yaml_path)
    rules = get_adhd_rules(board)
    hemispheres = get_hemisphere_tasks(board)
    immediate = get_immediate_actions(board)
    blockers = get_blockers(board)
    
    meeting = board.get("board_meeting", {})
    theme = meeting.get("theme", "Unknown Session")
    date = meeting.get("date", "Unknown Date")
    frequency = meeting.get("frequency", "432 Hz")
    
    # Calculate total incomplete tasks
    left_tasks = hemispheres["left"]["tasks"]
    right_tasks = hemispheres["right"]["tasks"]
    
    # Print the focus view
    print("=" * 70)
    print("🧠 STRATEGICKHAOS SWARM INTELLIGENCE — FOCUS MODE")
    print("=" * 70)
    print(f"📅 Session: {date}")
    print(f"🎯 Theme: {theme}")
    print(f"📡 Frequency: {frequency}")
    print(f"⚡ Max Parallel Tracks: {rules['max_parallel_tracks']}")
    print()
    
    # === DO THESE TODAY ===
    print("┌" + "─" * 68 + "┐")
    print("│" + f" 🔥 DO THESE {max_tasks} THINGS TODAY".center(68) + "│")
    print("└" + "─" * 68 + "┘")
    print()
    
    focus_tasks = []
    
    # Prioritize immediate actions first
    for action in immediate[:max_tasks]:
        focus_tasks.append({
            "source": "🚀 IMMEDIATE",
            "task": action["action"],
            "time": action["time"],
            "owner": action["owner"]
        })
    
    # If we need more, pull from hemispheres (alternating left/right)
    if len(focus_tasks) < max_tasks:
        remaining = max_tasks - len(focus_tasks)
        combined = []
        # Interleave tasks from left and right hemispheres, limit iterations
        for i in range(min(remaining, max(len(left_tasks), len(right_tasks)))):
            if i < len(left_tasks):
                combined.append(("🔷 LEFT", left_tasks[i]))
            if i < len(right_tasks):
                combined.append(("🔶 RIGHT", right_tasks[i]))
        
        for source, task in combined[:remaining]:
            focus_tasks.append({
                "source": source,
                "task": task,
                "time": "~",
                "owner": "You"
            })
    
    # Print focus tasks
    for i, item in enumerate(focus_tasks[:max_tasks], 1):
        print(f"  {i}. {item['source']}")
        print(f"     📋 {item['task']}")
        print(f"     ⏱️  Est: {item['time']} | 👤 {item['owner']}")
        print()
    
    # === HEMISPHERE STATUS ===
    print("┌" + "─" * 68 + "┐")
    print("│" + " 🧠 HEMISPHERE STATUS".center(68) + "│")
    print("└" + "─" * 68 + "┘")
    print()
    
    for key in ["left", "right"]:
        h = hemispheres[key]
        emoji = "🔷" if key == "left" else "🔶"
        # Clamp percentage between 0 and 100 to prevent bar overflow
        pct = min(100, max(0, int(h["status_pct"] * 100)))
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        print(f"  {emoji} {h['name']}")
        print(f"     {h['label']}")
        print(f"     [{bar}] {pct}%")
        print(f"     📋 {len(h['tasks'])} tasks remaining")
        print()
    
    # === BLOCKERS ===
    if blockers:
        print("┌" + "─" * 68 + "┐")
        print("│" + " ⛔ BLOCKERS".center(68) + "│")
        print("└" + "─" * 68 + "┘")
        print()
        for blocker in blockers:
            print(f"  ⚠️  {blocker}")
        print()
    
    # === BACKLOG SUMMARY ===
    total_remaining = len(left_tasks) + len(right_tasks)
    print("┌" + "─" * 68 + "┐")
    print("│" + " 📊 BACKLOG SUMMARY".center(68) + "│")
    print("└" + "─" * 68 + "┘")
    print()
    print(f"  🔷 Left Hemisphere:  {len(left_tasks)} incomplete tasks")
    print(f"  🔶 Right Hemisphere: {len(right_tasks)} incomplete tasks")
    print(f"  📦 Total Backlog:    {total_remaining} tasks")
    print()
    
    # === ADHD RULES ===
    print("┌" + "─" * 68 + "┐")
    print("│" + " 🎮 ADHD SANITY RULES (ACTIVE)".center(68) + "│")
    print("└" + "─" * 68 + "┘")
    print()
    print(f"  ⚡ Max Parallel Tracks: {rules['max_parallel_tracks']}")
    print(f"  ⏱️  Sprint Options: {rules['sprint_minutes']} min")
    print(f"  ⚖️  Balance: {rules['hemisphere_balance']}")
    print()
    
    print("=" * 70)
    print("🌟 Focus on the top 2. Everything else can wait.")
    print("=" * 70)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Strategickhaos Backlog Sync — ADHD-Friendly Focus Mode"
    )
    parser.add_argument(
        "--yaml", "-y",
        type=Path,
        help="Path to board_meeting.yaml (auto-detected if not provided)"
    )
    parser.add_argument(
        "--max-tasks", "-n",
        type=int,
        default=2,
        help="Maximum tasks to show in focus mode (default: 2)"
    )
    parser.add_argument(
        "--repo-root", "-r",
        type=Path,
        default=Path("."),
        help="Repository root directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    # Find the YAML file
    if args.yaml:
        yaml_path = args.yaml
    else:
        yaml_path = find_board_meeting_yaml(args.repo_root)
    
    if yaml_path is None or not yaml_path.exists():
        print("❌ No board_meeting*.yaml found!")
        print("   Provide one with --yaml or run from the repo root.")
        sys.exit(1)
    
    print(f"📂 Loading: {yaml_path}")
    print()
    
    try:
        print_focus_view(yaml_path, max_tasks=args.max_tasks)
    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
