#!/usr/bin/env python3
"""
State Sync CLI — Sovereign Truth Enforcer
Prevents AI nodes from making decisions based on wrong assumptions
"""
import yaml
import json
import hashlib
from datetime import datetime
from pathlib import Path
import subprocess

# Genesis constants
ARCHITECT_SNOWFLAKE = 1067614449693569044
GENESIS_INCREMENT = 3449

class SovereignStateSync:
    def __init__(self, state_file="STATE.yaml"):
        self.state_file = Path(state_file)
        self.state = self.load_state()
        
    def load_state(self):
        """Load current state from YAML"""
        if not self.state_file.exists():
            print(f"⚠️  State file not found: {self.state_file}")
            print("Creating default state file...")
            return self.create_default_state()
        
        with open(self.state_file, 'r') as f:
            return yaml.safe_load(f)
    
    def save_state(self):
        """Save state to YAML with cryptographic signature"""
        # Add metadata
        self.state['meta']['last_updated'] = datetime.now().isoformat()
        self.state['meta']['update_hash'] = self.calculate_hash()
        
        with open(self.state_file, 'w') as f:
            yaml.dump(self.state, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ State saved: {self.state_file}")
        print(f"🔐 Hash: {self.state['meta']['update_hash'][:16]}...")
    
    def calculate_hash(self):
        """Calculate SHA-256 hash of current state"""
        state_str = json.dumps(self.state, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()
    
    def verify_deployment(self, component):
        """Check if a component is actually deployed"""
        checks = {
            'kubectl': self.check_kubectl,
            'discord-bot': self.check_discord_bot,
            'wireguard': self.check_wireguard,
            'falco': self.check_falco
        }
        
        if component in checks:
            return checks[component]()
        else:
            return {"status": "unknown", "message": f"No check defined for {component}"}
    
    def check_kubectl(self):
        """Verify kubectl is working"""
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'nodes'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    "status": "working",
                    "message": "kubectl can reach cluster",
                    "output": result.stdout
                }
            else:
                return {
                    "status": "broken",
                    "message": "kubectl cannot reach cluster",
                    "error": result.stderr
                }
        except FileNotFoundError:
            return {
                "status": "not_installed",
                "message": "kubectl not found in PATH"
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "message": "kubectl command timed out"
            }
    
    def check_discord_bot(self):
        """Check if Discord bot is running in cluster"""
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'pods', '-n', 'legions-of-minds', '-l', 'app=neural-mesh'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and 'neural-mesh' in result.stdout:
                return {
                    "status": "deployed",
                    "message": "Discord bot found in cluster",
                    "location": "in-cluster",
                    "output": result.stdout
                }
            else:
                return {
                    "status": "not_deployed",
                    "message": "Discord bot NOT found in cluster",
                    "location": "external (Windows laptop?)"
                }
        except:
            return {
                "status": "cannot_verify",
                "message": "kubectl not working, can't check bot status"
            }
    
    def check_wireguard(self):
        """Check if WireGuard is running"""
        try:
            result = subprocess.run(
                ['wg', 'show'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout:
                return {
                    "status": "running",
                    "message": "WireGuard interfaces found",
                    "output": result.stdout
                }
            else:
                return {
                    "status": "not_running",
                    "message": "No WireGuard interfaces active"
                }
        except FileNotFoundError:
            return {
                "status": "not_installed",
                "message": "WireGuard not installed"
            }
    
    def check_falco(self):
        """Check if Falco is running"""
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'pods', '-n', 'falco', '-l', 'app=falco'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and 'falco' in result.stdout:
                return {
                    "status": "running",
                    "message": "Falco pods found in cluster"
                }
            else:
                return {
                    "status": "not_deployed",
                    "message": "Falco NOT deployed"
                }
        except:
            return {
                "status": "cannot_verify",
                "message": "kubectl not working"
            }
    
    def check_decision_gates(self, decision_type):
        """Check if decision gates allow an action"""
        gates = self.state.get('decision_gates', {}).get(decision_type, {})
        verifications = gates.get('required_verifications', [])
        
        blockers = []
        warnings = []
        
        for check in verifications:
            if not check.get('current_state', False):
                if check.get('block_if_false', False):
                    blockers.append(check)
                elif check.get('warn_if_false', False):
                    warnings.append(check)
        
        return {
            "allowed": len(blockers) == 0,
            "blockers": blockers,
            "warnings": warnings
        }
    
    def get_operator_state(self):
        """Get current operator physical/mental state"""
        return self.state.get('operator_state', {})
    
    def update_operator_state(self, **kwargs):
        """Update operator state"""
        if 'operator_state' not in self.state:
            self.state['operator_state'] = {}
        
        self.state['operator_state'].update(kwargs)
        self.save_state()
    
    def ai_query(self, query):
        """Process a query from an AI node"""
        print(f"\n🤖 AI Query: {query}\n")
        
        # Example queries
        if 'kubectl' in query.lower():
            result = self.verify_deployment('kubectl')
            print(f"📊 kubectl Status: {result['status']}")
            print(f"   {result['message']}")
            
        elif 'discord bot' in query.lower():
            result = self.verify_deployment('discord-bot')
            print(f"📊 Discord Bot Status: {result['status']}")
            print(f"   Location: {result.get('location', 'unknown')}")
            print(f"   {result['message']}")
            
        elif 'can i deploy' in query.lower():
            gates = self.check_decision_gates('pre_deployment_check')
            if gates['allowed']:
                print("✅ Deployment ALLOWED")
            else:
                print("❌ Deployment BLOCKED")
                for blocker in gates['blockers']:
                    print(f"   ⛔ {blocker['question']}")
                    print(f"      {blocker['message']}")
            
            if gates['warnings']:
                print("\n⚠️  Warnings:")
                for warning in gates['warnings']:
                    print(f"   ⚠️  {warning['question']}")
                    print(f"      {warning['message']}")
        
        elif 'operator ready' in query.lower():
            op_state = self.get_operator_state()
            hours_awake = op_state.get('hours_awake', 'unknown')
            
            if isinstance(hours_awake, str) and '+' in hours_awake:
                hours = int(hours_awake.replace('+', ''))
                if hours > 24:
                    print(f"❌ Operator NOT READY")
                    print(f"   Awake: {hours_awake} hours")
                    print(f"   Recommendation: REST before major decisions")
                else:
                    print(f"✅ Operator READY")
            else:
                print(f"⚠️  Operator state unknown")
    
    def create_default_state(self):
        """Create default state structure"""
        return {
            'meta': {
                'protocol_name': 'Claudify/Domify Sovereign State Sync',
                'version': '1.0.0',
                'genesis_lock': True,
                'architect_snowflake': ARCHITECT_SNOWFLAKE,
                'increment': GENESIS_INCREMENT
            },
            'infrastructure_state': {
                'deployed': {},
                'pending_deployment': []
            },
            'operator_state': {
                'hours_awake': '0',
                'last_meal': 'unknown',
                'cognitive_load': 'normal'
            },
            'decision_gates': {}
        }
    
    def snapshot(self):
        """Create immutable state snapshot"""
        snapshot_data = {
            'timestamp': datetime.now().isoformat(),
            'state': self.state,
            'hash': self.calculate_hash(),
            'architect': ARCHITECT_SNOWFLAKE
        }
        
        snapshot_file = self.state_file.parent / f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot_data, f, indent=2)
        
        print(f"📸 Snapshot saved: {snapshot_file}")
        print(f"🔐 Hash: {snapshot_data['hash'][:16]}...")
        
        return snapshot_file

def main():
    import sys
    
    sync = SovereignStateSync("STATE.yaml")
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python state_sync.py query 'is kubectl working?'")
        print("  python state_sync.py check kubectl")
        print("  python state_sync.py check discord-bot")
        print("  python state_sync.py gates pre_deployment_check")
        print("  python state_sync.py snapshot")
        print("  python state_sync.py update operator hours_awake 8")
        return
    
    command = sys.argv[1]
    
    if command == 'query':
        query = ' '.join(sys.argv[2:])
        sync.ai_query(query)
        
    elif command == 'check':
        if len(sys.argv) < 3:
            print("Specify component: kubectl, discord-bot, wireguard, falco")
            return
        component = sys.argv[2]
        result = sync.verify_deployment(component)
        print(json.dumps(result, indent=2))
        
    elif command == 'gates':
        if len(sys.argv) < 3:
            print("Specify gate type: pre_deployment_check, pre_financial_check, pre_education_check")
            return
        gate_type = sys.argv[2]
        result = sync.check_decision_gates(gate_type)
        print(json.dumps(result, indent=2))
        
    elif command == 'snapshot':
        sync.snapshot()
        
    elif command == 'update':
        if len(sys.argv) < 5:
            print("Usage: update <section> <key> <value>")
            return
        section = sys.argv[2]
        key = sys.argv[3]
        value = sys.argv[4]
        
        if section == 'operator':
            sync.update_operator_state(**{key: value})
            print(f"✅ Updated operator_state.{key} = {value}")
        else:
            print(f"Unknown section: {section}")

if __name__ == "__main__":
    main()
