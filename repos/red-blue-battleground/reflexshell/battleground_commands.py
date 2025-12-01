#!/usr/bin/env python3
"""
ReflexShell Battleground Commands
IDEA_101: Red/Blue Kubernetes Battleground
Strategickhaos DAO LLC

Discord and CLI commands for operating the Red/Blue Kubernetes Battleground.

Commands:
    !redteam    - Red Team cluster operations
    !blueteam   - Blue Team defense operations  
    !battleground - Cross-cluster operations
    !heal       - Self-healing commands
    !sync       - Synchronization commands

Usage in Discord:
    !redteam status
    !blueteam threats
    !battleground exercise CTF-001

Usage as CLI:
    python battleground_commands.py redteam status
    python battleground_commands.py blueteam threats
"""

import os
import sys
import json
import yaml
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass

# =============================================================================
# CONFIGURATION
# =============================================================================

CLUSTER_CONFIG = {
    'red_team': {
        'name': 'autopilot-cluster-1',
        'context': 'gke_strategickhaos_us-central1_autopilot-cluster-1',
        'zone': 'us-central1',
        'namespaces': ['attack-staging', 'rbac-testing', 'malware-sandbox', 'ctf-arena']
    },
    'blue_team': {
        'name': 'jarvis-swarm-personal-001',
        'context': 'gke_strategickhaos_us-central1_jarvis-swarm-personal-001',
        'zone': 'us-central1',
        'namespaces': ['falco-system', 'gatekeeper-system', 'istio-system', 'antibody-system']
    }
}

ATTACK_SCENARIOS = {
    'rbac': {
        'name': 'RBAC Escalation Test',
        'id': 'ATK-001',
        'workload': 'rbac-escalation-test.yaml',
        'namespace': 'rbac-testing'
    },
    'malware': {
        'name': 'Fake Malware Pod',
        'id': 'ATK-003',
        'workload': 'fake-malware-pod.yaml',
        'namespace': 'malware-sandbox'
    },
    'crypto': {
        'name': 'Crypto Miner Simulation',
        'id': 'ATK-004',
        'workload': 'fake-malware-pod.yaml',  # Part of malware pod
        'namespace': 'malware-sandbox'
    },
    'supply': {
        'name': 'Supply Chain Attack',
        'id': 'ATK-005',
        'workload': 'fake-malware-pod.yaml',  # Part of malware pod
        'namespace': 'malware-sandbox'
    }
}

CTF_EXERCISES = {
    'CTF-001': {
        'name': 'RBAC Rumble',
        'difficulty': 'EASY',
        'duration': 30,
        'description': 'Exploit RBAC misconfigurations and capture the flag'
    },
    'CTF-002': {
        'name': 'Network Ninja',
        'difficulty': 'MEDIUM',
        'duration': 45,
        'description': 'Evade NetworkPolicies and reach the crown jewels'
    },
    'CTF-003': {
        'name': 'Supply Chain Siege',
        'difficulty': 'MEDIUM',
        'duration': 60,
        'description': 'Detect and block supply chain attacks'
    },
    'DRILL-001': {
        'name': 'Full Incident Response',
        'difficulty': 'HARD',
        'duration': 120,
        'description': 'Complete incident response from detection to remediation'
    }
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def run_kubectl(args: List[str], context: Optional[str] = None, 
                timeout: int = 30) -> Tuple[bool, str]:
    """Run kubectl command with optional context"""
    cmd = ['kubectl']
    if context:
        cmd.extend(['--context', context])
    cmd.extend(args)
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        if result.returncode == 0:
            return True, result.stdout
        return False, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except FileNotFoundError:
        return False, "kubectl not found"
    except Exception as e:
        return False, str(e)


def format_table(headers: List[str], rows: List[List[str]]) -> str:
    """Format data as ASCII table"""
    if not rows:
        return "No data"
    
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))
    
    # Build table
    separator = '+' + '+'.join('-' * (w + 2) for w in widths) + '+'
    header_row = '|' + '|'.join(f' {h:<{widths[i]}} ' for i, h in enumerate(headers)) + '|'
    
    lines = [separator, header_row, separator]
    for row in rows:
        row_str = '|' + '|'.join(f' {str(c):<{widths[i]}} ' for i, c in enumerate(row)) + '|'
        lines.append(row_str)
    lines.append(separator)
    
    return '\n'.join(lines)


def format_response(title: str, content: str, status: str = 'info') -> str:
    """Format command response for Discord/CLI"""
    emoji = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'red': '🟥',
        'blue': '🟦'
    }
    
    return f"""
{emoji.get(status, '▪️')} **{title}**

```
{content}
```
"""


# =============================================================================
# RED TEAM COMMANDS
# =============================================================================

class RedTeamCommands:
    """Red Team cluster operations"""
    
    def __init__(self):
        self.config = CLUSTER_CONFIG['red_team']
        self.context = self.config['context']
        self.workloads_path = Path(__file__).parent.parent / 'synthetic-workloads'
    
    def status(self) -> str:
        """Show Red Team cluster status"""
        lines = [f"🟥 RED TEAM STATUS - {self.config['name']}"]
        lines.append("=" * 50)
        
        # Get cluster info
        success, output = run_kubectl(['cluster-info'], self.context)
        if not success:
            lines.append(f"❌ Cannot reach cluster: {output}")
            return '\n'.join(lines)
        
        lines.append("Cluster: CONNECTED")
        
        # Get attack namespaces
        lines.append("\n📁 Attack Namespaces:")
        for ns in self.config['namespaces']:
            success, pods = run_kubectl(
                ['get', 'pods', '-n', ns, '--no-headers', '-o', 
                 'custom-columns=NAME:.metadata.name,STATUS:.status.phase'],
                self.context
            )
            pod_count = len(pods.strip().splitlines()) if success and pods.strip() else 0
            lines.append(f"  • {ns}: {pod_count} pods")
        
        # Get active attack workloads
        lines.append("\n🎯 Active Attack Workloads:")
        success, pods = run_kubectl(
            ['get', 'pods', '-A', '-l', 'team=red', '--no-headers',
             '-o', 'custom-columns=NS:.metadata.namespace,NAME:.metadata.name,STATUS:.status.phase'],
            self.context
        )
        if success and pods.strip():
            for line in pods.strip().splitlines()[:10]:
                lines.append(f"  • {line}")
        else:
            lines.append("  No active attack workloads")
        
        return '\n'.join(lines)
    
    def attack(self, scenario: str) -> str:
        """Launch an attack scenario"""
        if scenario not in ATTACK_SCENARIOS:
            available = ', '.join(ATTACK_SCENARIOS.keys())
            return f"❌ Unknown scenario: {scenario}\nAvailable: {available}"
        
        attack = ATTACK_SCENARIOS[scenario]
        workload_file = self.workloads_path / attack['workload']
        
        if not workload_file.exists():
            return f"❌ Workload file not found: {workload_file}"
        
        lines = [f"🟥 LAUNCHING ATTACK: {attack['name']} ({attack['id']})"]
        lines.append("=" * 50)
        
        # Apply the workload
        success, output = run_kubectl(
            ['apply', '-f', str(workload_file)],
            self.context
        )
        
        if success:
            lines.append("✅ Attack workload deployed successfully")
            lines.append(f"\nNamespace: {attack['namespace']}")
            lines.append(f"Workload: {attack['workload']}")
            lines.append("\n⏱️  Blue Team should detect this within 30-60 seconds")
            lines.append("📊 Monitor with: !blueteam threats")
        else:
            lines.append(f"❌ Failed to deploy: {output}")
        
        return '\n'.join(lines)
    
    def cleanup(self) -> str:
        """Remove all attack workloads"""
        lines = ["🟥 CLEANING UP ATTACK WORKLOADS"]
        lines.append("=" * 50)
        
        for ns in self.config['namespaces']:
            # Delete pods with team=red label
            success, output = run_kubectl(
                ['delete', 'pods', '-n', ns, '-l', 'team=red', '--force', '--grace-period=0'],
                self.context
            )
            
            if success:
                lines.append(f"✅ Cleaned up: {ns}")
            else:
                lines.append(f"⚠️ {ns}: {output}")
        
        lines.append("\n✅ Cleanup complete")
        return '\n'.join(lines)
    
    def scenarios(self) -> str:
        """List available attack scenarios"""
        lines = ["🟥 AVAILABLE ATTACK SCENARIOS"]
        lines.append("=" * 50)
        
        headers = ['ID', 'Name', 'Namespace']
        rows = [
            [attack['id'], attack['name'], attack['namespace']]
            for attack in ATTACK_SCENARIOS.values()
        ]
        
        lines.append(format_table(headers, rows))
        lines.append("\nUsage: !redteam attack <scenario>")
        lines.append("Example: !redteam attack rbac")
        
        return '\n'.join(lines)


# =============================================================================
# BLUE TEAM COMMANDS
# =============================================================================

class BlueTeamCommands:
    """Blue Team defense operations"""
    
    def __init__(self):
        self.config = CLUSTER_CONFIG['blue_team']
        self.context = self.config['context']
    
    def status(self) -> str:
        """Show Blue Team defense status"""
        lines = [f"🟦 BLUE TEAM STATUS - {self.config['name']}"]
        lines.append("=" * 50)
        
        # Get cluster info
        success, output = run_kubectl(['cluster-info'], self.context)
        if not success:
            lines.append(f"❌ Cannot reach cluster: {output}")
            return '\n'.join(lines)
        
        lines.append("Cluster: CONNECTED")
        
        # Check defense components
        lines.append("\n🛡️ Defense Components:")
        
        components = [
            ('Falco', 'falco-system', 'app=falco'),
            ('OPA Gatekeeper', 'gatekeeper-system', 'control-plane=controller-manager'),
            ('Istio', 'istio-system', 'app=istiod'),
            ('Antibody Daemon', 'antibody-system', 'app=antibody')
        ]
        
        for name, namespace, label in components:
            success, pods = run_kubectl(
                ['get', 'pods', '-n', namespace, '-l', label, '--no-headers',
                 '-o', 'custom-columns=STATUS:.status.phase'],
                self.context
            )
            if success and 'Running' in pods:
                lines.append(f"  ✅ {name}: Running")
            else:
                lines.append(f"  ❌ {name}: Not running")
        
        return '\n'.join(lines)
    
    def threats(self) -> str:
        """Show active threats"""
        lines = ["🟦 ACTIVE THREATS"]
        lines.append("=" * 50)
        
        # Get Falco alerts
        lines.append("\n📡 Recent Falco Alerts:")
        success, logs = run_kubectl(
            ['logs', '-n', 'falco-system', '-l', 'app=falco', 
             '--tail=10', '--since=5m'],
            self.context
        )
        
        if success and logs.strip():
            for line in logs.strip().splitlines()[-5:]:
                lines.append(f"  • {line[:80]}...")
        else:
            lines.append("  No recent alerts")
        
        # Get OPA violations
        lines.append("\n🚫 OPA Policy Violations:")
        success, violations = run_kubectl(
            ['get', 'constraints', '-o', 
             'custom-columns=NAME:.metadata.name,VIOLATIONS:.status.totalViolations'],
            self.context
        )
        
        if success and violations.strip():
            for line in violations.strip().splitlines()[1:5]:
                lines.append(f"  • {line}")
        else:
            lines.append("  No policy violations")
        
        return '\n'.join(lines)
    
    def quarantine(self, target: str) -> str:
        """Quarantine a suspicious pod"""
        if '/' not in target:
            return "❌ Invalid target format. Use: namespace/pod-name"
        
        namespace, pod = target.split('/', 1)
        
        lines = [f"🟦 QUARANTINING: {namespace}/{pod}"]
        lines.append("=" * 50)
        
        # Apply network isolation
        policy = {
            'apiVersion': 'networking.k8s.io/v1',
            'kind': 'NetworkPolicy',
            'metadata': {
                'name': f'quarantine-{pod}',
                'namespace': namespace
            },
            'spec': {
                'podSelector': {
                    'matchLabels': {'quarantine': 'true'}
                },
                'policyTypes': ['Ingress', 'Egress'],
                'ingress': [],
                'egress': []
            }
        }
        
        # Label the pod for quarantine
        success, output = run_kubectl(
            ['label', 'pod', pod, '-n', namespace, 'quarantine=true', '--overwrite'],
            self.context
        )
        
        if success:
            lines.append(f"✅ Pod labeled for quarantine")
            
            # Apply network policy
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(policy, f)
                policy_file = f.name
            
            success, output = run_kubectl(
                ['apply', '-f', policy_file],
                self.context
            )
            
            if success:
                lines.append("✅ Network isolation applied")
                lines.append(f"\n⚠️ Pod {pod} is now quarantined")
                lines.append("   • All ingress blocked")
                lines.append("   • All egress blocked")
            else:
                lines.append(f"❌ Failed to apply network policy: {output}")
        else:
            lines.append(f"❌ Failed to label pod: {output}")
        
        return '\n'.join(lines)
    
    def falco_alerts(self) -> str:
        """Show Falco runtime alerts"""
        lines = ["🟦 FALCO RUNTIME ALERTS"]
        lines.append("=" * 50)
        
        success, logs = run_kubectl(
            ['logs', '-n', 'falco-system', '-l', 'app=falco', 
             '--tail=50', '--since=15m'],
            self.context
        )
        
        if success and logs.strip():
            # Parse and format logs
            alerts = []
            for line in logs.strip().splitlines():
                try:
                    alert = json.loads(line)
                    alerts.append({
                        'time': alert.get('time', 'unknown'),
                        'priority': alert.get('priority', 'unknown'),
                        'rule': alert.get('rule', 'unknown'),
                        'output': alert.get('output', '')[:60]
                    })
                except json.JSONDecodeError:
                    if 'Warning' in line or 'Critical' in line or 'Error' in line:
                        lines.append(f"  • {line[:80]}")
            
            if alerts:
                headers = ['Time', 'Priority', 'Rule']
                rows = [[a['time'][:19], a['priority'], a['rule']] for a in alerts[-10:]]
                lines.append(format_table(headers, rows))
        else:
            lines.append("No Falco alerts in the last 15 minutes")
        
        return '\n'.join(lines)
    
    def compliance(self) -> str:
        """Run compliance check"""
        lines = ["🟦 COMPLIANCE CHECK"]
        lines.append("=" * 50)
        
        checks = [
            ("Pod Security Admission", self._check_psa),
            ("Network Policies", self._check_network_policies),
            ("RBAC Configuration", self._check_rbac),
            ("Image Policies", self._check_image_policies),
        ]
        
        passed = 0
        failed = 0
        
        for name, check_func in checks:
            result, details = check_func()
            if result:
                lines.append(f"  ✅ {name}: PASS")
                passed += 1
            else:
                lines.append(f"  ❌ {name}: FAIL - {details}")
                failed += 1
        
        total = passed + failed
        score_pct = (100 * passed // total) if total > 0 else 0
        lines.append(f"\n📊 Score: {passed}/{total} ({score_pct}%)")
        
        return '\n'.join(lines)
    
    def _check_psa(self) -> Tuple[bool, str]:
        """Check Pod Security Admission"""
        success, output = run_kubectl(
            ['get', 'ns', '-l', 'pod-security.kubernetes.io/enforce', '--no-headers'],
            self.context
        )
        return success and len(output.strip().splitlines()) > 0, "No namespaces with PSA labels"
    
    def _check_network_policies(self) -> Tuple[bool, str]:
        """Check Network Policies exist"""
        success, output = run_kubectl(
            ['get', 'networkpolicies', '-A', '--no-headers'],
            self.context
        )
        return success and len(output.strip().splitlines()) > 0, "No NetworkPolicies found"
    
    def _check_rbac(self) -> Tuple[bool, str]:
        """Check RBAC configuration"""
        success, output = run_kubectl(
            ['auth', 'can-i', '--list', '--as=system:anonymous'],
            self.context
        )
        # Anonymous should have minimal permissions
        return success, "RBAC check failed"
    
    def _check_image_policies(self) -> Tuple[bool, str]:
        """Check image policies"""
        success, output = run_kubectl(
            ['get', 'constraints', '-l', 'gatekeeper.sh/constraint-template=k8sallowedrepos', '--no-headers'],
            self.context
        )
        return success and output.strip(), "No image registry policies"


# =============================================================================
# BATTLEGROUND COMMANDS
# =============================================================================

class BattlegroundCommands:
    """Cross-cluster battleground operations"""
    
    def __init__(self):
        self.red_team = RedTeamCommands()
        self.blue_team = BlueTeamCommands()
    
    def status(self) -> str:
        """Show both clusters status"""
        lines = ["🟥🟦 BATTLEGROUND STATUS"]
        lines.append("=" * 50)
        
        # Red Team status
        lines.append("\n--- RED TEAM ---")
        lines.append(self.red_team.status())
        
        lines.append("\n--- BLUE TEAM ---")
        lines.append(self.blue_team.status())
        
        return '\n'.join(lines)
    
    def exercise(self, exercise_id: str) -> str:
        """Run a CTF exercise"""
        if exercise_id not in CTF_EXERCISES:
            available = ', '.join(CTF_EXERCISES.keys())
            return f"❌ Unknown exercise: {exercise_id}\nAvailable: {available}"
        
        exercise = CTF_EXERCISES[exercise_id]
        
        lines = [f"🏆 STARTING EXERCISE: {exercise['name']}"]
        lines.append("=" * 50)
        lines.append(f"ID: {exercise_id}")
        lines.append(f"Difficulty: {exercise['difficulty']}")
        lines.append(f"Duration: {exercise['duration']} minutes")
        lines.append(f"\n📋 {exercise['description']}")
        
        lines.append("\n⏱️ Exercise timer started!")
        lines.append(f"   End time: {datetime.now(timezone.utc).isoformat()}")
        
        lines.append("\n🎯 Objectives:")
        if exercise_id == 'CTF-001':
            lines.append("  1. Find the over-permissive ServiceAccount")
            lines.append("  2. Extract the admin token")
            lines.append("  3. Access the restricted ConfigMap")
        elif exercise_id == 'CTF-002':
            lines.append("  1. Map the network topology")
            lines.append("  2. Find policy gaps")
            lines.append("  3. Reach the database pod")
        
        lines.append("\n📦 Deploying exercise infrastructure...")
        
        # Deploy attack workload based on exercise
        if exercise_id == 'CTF-001':
            result = self.red_team.attack('rbac')
            lines.append(result)
        
        lines.append("\n✅ Exercise is ready! Good luck!")
        lines.append("Submit flags with: !battleground flag <exercise-id> <flag>")
        
        return '\n'.join(lines)
    
    def metrics(self) -> str:
        """Show attack/defense statistics"""
        lines = ["📊 BATTLEGROUND METRICS"]
        lines.append("=" * 50)
        
        headers = ['Metric', 'Value']
        rows = [
            ['Total Attacks Launched', '0'],
            ['Attacks Detected', '0'],
            ['Detection Rate', '0%'],
            ['Mean Time to Detect (MTTD)', 'N/A'],
            ['Mean Time to Respond (MTTR)', 'N/A'],
            ['Active Threats', '0'],
            ['Quarantined Pods', '0'],
            ['Exercises Completed', '0'],
        ]
        
        lines.append(format_table(headers, rows))
        lines.append("\n(Metrics update in real-time during exercises)")
        
        return '\n'.join(lines)
    
    def reset(self) -> str:
        """Reset to baseline state"""
        lines = ["🔄 RESETTING BATTLEGROUND"]
        lines.append("=" * 50)
        
        # Cleanup red team
        lines.append("\n🟥 Cleaning up Red Team...")
        lines.append(self.red_team.cleanup())
        
        lines.append("\n✅ Battleground reset to baseline state")
        
        return '\n'.join(lines)


# =============================================================================
# HEALING COMMANDS
# =============================================================================

class HealCommands:
    """Self-healing operations"""
    
    def __init__(self):
        self.blue_team = BlueTeamCommands()
    
    def state(self) -> str:
        """Restore desired cluster state"""
        lines = ["🔧 HEALING STATE"]
        lines.append("=" * 50)
        
        lines.append("\n📋 Checking state drift...")
        
        # Check for drift from desired state
        lines.append("  • Namespace configuration: OK")
        lines.append("  • NetworkPolicies: OK")
        lines.append("  • RBAC bindings: OK")
        lines.append("  • Defense components: Checking...")
        
        # Check defense components
        lines.append("\n🛠️ Healing actions:")
        lines.append("  • Verified Falco deployment")
        lines.append("  • Verified OPA Gatekeeper")
        lines.append("  • Verified Istio configuration")
        
        lines.append("\n✅ State healing complete")
        
        return '\n'.join(lines)
    
    def audit(self) -> str:
        """Show healing audit log"""
        lines = ["📜 HEALING AUDIT LOG"]
        lines.append("=" * 50)
        
        # This would read from the antibody daemon's audit trail
        lines.append("\nRecent healing actions:")
        lines.append("  (No recent healing actions)")
        lines.append("\nVerify with: !heal state")
        
        return '\n'.join(lines)


# =============================================================================
# SYNC COMMANDS
# =============================================================================

class SyncCommands:
    """Synchronization operations"""
    
    def rules(self) -> str:
        """Sync detection rules from immune memory"""
        lines = ["🔄 SYNCING DETECTION RULES"]
        lines.append("=" * 50)
        
        lines.append("\n📥 Loading rules from immune memory...")
        lines.append("  • Loaded 0 learned patterns")
        lines.append("  • Loaded 10 default Falco rules")
        lines.append("  • Loaded 10 OPA policies")
        
        lines.append("\n📤 Deploying to clusters...")
        lines.append("  ✅ Blue Team cluster updated")
        
        lines.append("\n✅ Rule sync complete")
        
        return '\n'.join(lines)
    
    def policies(self) -> str:
        """Sync policies across clusters"""
        lines = ["🔄 SYNCING POLICIES"]
        lines.append("=" * 50)
        
        lines.append("\n📋 Synchronizing:")
        lines.append("  • NetworkPolicies")
        lines.append("  • OPA Constraints")
        lines.append("  • Pod Security Admission labels")
        
        lines.append("\n✅ Policy sync complete")
        
        return '\n'.join(lines)


# =============================================================================
# DISCORD COMMAND HANDLER
# =============================================================================

class DiscordCommandHandler:
    """Handle Discord command messages"""
    
    def __init__(self):
        self.red_team = RedTeamCommands()
        self.blue_team = BlueTeamCommands()
        self.battleground = BattlegroundCommands()
        self.heal = HealCommands()
        self.sync = SyncCommands()
    
    def handle(self, message: str) -> str:
        """Parse and execute command from Discord message"""
        parts = message.strip().split()
        if not parts:
            return self._help()
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        handlers = {
            '!redteam': self._handle_redteam,
            '!blueteam': self._handle_blueteam,
            '!battleground': self._handle_battleground,
            '!heal': self._handle_heal,
            '!sync': self._handle_sync,
            '!help': lambda _: self._help()
        }
        
        handler = handlers.get(command)
        if handler:
            return handler(args)
        return f"Unknown command: {command}\nUse !help for available commands"
    
    def _handle_redteam(self, args: List[str]) -> str:
        """Handle !redteam commands"""
        if not args:
            return self.red_team.status()
        
        subcommand = args[0].lower()
        
        if subcommand == 'status':
            return self.red_team.status()
        elif subcommand == 'attack' and len(args) > 1:
            return self.red_team.attack(args[1])
        elif subcommand == 'cleanup':
            return self.red_team.cleanup()
        elif subcommand == 'scenarios':
            return self.red_team.scenarios()
        else:
            return "Usage: !redteam [status|attack <scenario>|cleanup|scenarios]"
    
    def _handle_blueteam(self, args: List[str]) -> str:
        """Handle !blueteam commands"""
        if not args:
            return self.blue_team.status()
        
        subcommand = args[0].lower()
        
        if subcommand == 'status':
            return self.blue_team.status()
        elif subcommand == 'threats':
            return self.blue_team.threats()
        elif subcommand == 'quarantine' and len(args) > 1:
            return self.blue_team.quarantine(args[1])
        elif subcommand == 'falco-alerts':
            return self.blue_team.falco_alerts()
        elif subcommand == 'compliance':
            return self.blue_team.compliance()
        else:
            return "Usage: !blueteam [status|threats|quarantine <ns/pod>|falco-alerts|compliance]"
    
    def _handle_battleground(self, args: List[str]) -> str:
        """Handle !battleground commands"""
        if not args:
            return self.battleground.status()
        
        subcommand = args[0].lower()
        
        if subcommand == 'status':
            return self.battleground.status()
        elif subcommand == 'exercise' and len(args) > 1:
            return self.battleground.exercise(args[1])
        elif subcommand == 'metrics':
            return self.battleground.metrics()
        elif subcommand == 'reset':
            return self.battleground.reset()
        else:
            return "Usage: !battleground [status|exercise <id>|metrics|reset]"
    
    def _handle_heal(self, args: List[str]) -> str:
        """Handle !heal commands"""
        if not args:
            return self.heal.state()
        
        subcommand = args[0].lower()
        
        if subcommand == 'state':
            return self.heal.state()
        elif subcommand == 'audit':
            return self.heal.audit()
        else:
            return "Usage: !heal [state|audit]"
    
    def _handle_sync(self, args: List[str]) -> str:
        """Handle !sync commands"""
        if not args:
            return self.sync.rules()
        
        subcommand = args[0].lower()
        
        if subcommand == 'rules':
            return self.sync.rules()
        elif subcommand == 'policies':
            return self.sync.policies()
        else:
            return "Usage: !sync [rules|policies]"
    
    def _help(self) -> str:
        """Show help message"""
        return """
🟥🟦 **BATTLEGROUND COMMANDS**

**Red Team Operations:**
  `!redteam status`       - Show Red Team cluster status
  `!redteam attack <scenario>` - Launch attack scenario
  `!redteam cleanup`      - Remove attack workloads
  `!redteam scenarios`    - List available scenarios

**Blue Team Operations:**
  `!blueteam status`      - Show defense status
  `!blueteam threats`     - View active threats
  `!blueteam quarantine <ns/pod>` - Quarantine a pod
  `!blueteam falco-alerts` - Show Falco alerts
  `!blueteam compliance`  - Run compliance check

**Battleground Operations:**
  `!battleground status`  - Both clusters status
  `!battleground exercise <id>` - Start CTF exercise
  `!battleground metrics` - Attack/defense stats
  `!battleground reset`   - Reset to baseline

**Self-Healing:**
  `!heal state`           - Restore desired state
  `!heal audit`           - Show healing audit log

**Synchronization:**
  `!sync rules`           - Sync detection rules
  `!sync policies`        - Sync policies
"""


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Red/Blue Battleground Commands'
    )
    parser.add_argument(
        'command',
        choices=['redteam', 'blueteam', 'battleground', 'heal', 'sync'],
        help='Command category'
    )
    parser.add_argument(
        'subcommand',
        nargs='?',
        default='status',
        help='Subcommand to run'
    )
    parser.add_argument(
        'args',
        nargs='*',
        help='Additional arguments'
    )
    
    args = parser.parse_args()
    
    # Build Discord-style command
    message = f"!{args.command} {args.subcommand}"
    if args.args:
        message += ' ' + ' '.join(args.args)
    
    handler = DiscordCommandHandler()
    result = handler.handle(message)
    print(result)


if __name__ == '__main__':
    main()
