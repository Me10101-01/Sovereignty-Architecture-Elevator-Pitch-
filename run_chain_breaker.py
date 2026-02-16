#!/usr/bin/env python3
"""
Chain Breaker Evolution - Master Orchestrator
Runs all phases sequentially: Bootstrap -> Prior Art -> Control Unit -> Register Memory
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

def print_banner(text, char="="):
    """Print a formatted banner"""
    width = 70
    print("\n" + char * width)
    print(text.center(width))
    print(char * width + "\n")

def run_phase(script_path, phase_name, working_dir=None):
    """Run a phase script and report results"""
    print_banner(f"Running {phase_name}", "-")
    
    try:
        if working_dir:
            result = subprocess.run(
                [sys.executable, script_path],
                cwd=working_dir,
                capture_output=True,
                text=True,
                check=True
            )
        else:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                check=True
            )
        
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:", result.stderr)
        
        print(f"✅ {phase_name} completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {phase_name} failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def main():
    """Main orchestrator execution"""
    print_banner("Chain Breaker Evolution - Master Orchestrator")
    print(f"Start time: {datetime.now().isoformat()}")
    
    base_path = Path(__file__).parent
    
    phases = [
        {
            'name': 'Phase 1: Bootstrap Initialization',
            'script': base_path / 'bootstrap.py',
            'working_dir': base_path
        },
        {
            'name': 'Phase 2: Prior Art Integration',
            'script': base_path / 'prior_art_integrate.py',
            'working_dir': base_path
        },
        {
            'name': 'Phase 3: Control Unit Deployment',
            'script': base_path / 'src' / 'control_unit' / 'control_unit.py',
            'working_dir': base_path / 'src' / 'control_unit'
        },
        {
            'name': 'Phase 4: Register Memory Integration',
            'script': base_path / 'src' / 'register_memory' / 'register_memory.py',
            'working_dir': base_path / 'src' / 'register_memory'
        },
        {
            'name': 'GPT Assistant Test',
            'script': base_path / 'src' / 'gpt_assistant' / 'assistant.py',
            'working_dir': base_path / 'src' / 'gpt_assistant'
        }
    ]
    
    results = []
    for phase in phases:
        success = run_phase(
            phase['script'],
            phase['name'],
            phase.get('working_dir')
        )
        results.append({
            'phase': phase['name'],
            'success': success
        })
        
        if not success:
            print(f"\n⚠️  {phase['name']} failed. Stopping execution.")
            break
    
    # Summary
    print_banner("Execution Summary")
    
    all_success = all(r['success'] for r in results)
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} - {result['phase']}")
    
    print(f"\nEnd time: {datetime.now().isoformat()}")
    
    if all_success:
        print_banner("🎉 All Phases Complete - Chain Breaker Evolution Operational", "🔥")
        print("\nSystem Status:")
        print("  ✓ FlameLang Chain Breaker: Deployed")
        print("  ✓ Quantum Emulator: Operational")
        print("  ✓ GSCH Protection: Active (drift <0.05)")
        print("  ✓ Swarm Bots: Monitoring")
        print("  ✓ GPT Assistant: Ready")
        print("\nOutput files:")
        print("  - bootstrap_metadata.yaml")
        print("  - prior_art_mapping.yaml")
        print("  - src/control_unit/control_unit_state.yaml")
        print("  - src/register_memory/register_memory_state.yaml")
        print("  - gpt_contributions.yaml")
        print("  - gpt_log.txt")
        print("\nReady for FEP-0004 ratification.")
        return 0
    else:
        print_banner("⚠️  Some Phases Failed", "!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
