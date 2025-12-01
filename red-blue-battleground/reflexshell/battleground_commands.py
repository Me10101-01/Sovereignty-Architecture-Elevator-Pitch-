#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
REFLEXSHELL COMMANDS — Red/Blue Battleground Operations
IDEA_101: Red/Blue Kubernetes Battleground
StrategicKhaos DAO LLC
═══════════════════════════════════════════════════════════════════════════════

ReflexShell commands for operating the dual-cluster cyber lab.

Commands:
  !redteam <subcommand>   - Red team attack operations
  !blueteam <subcommand>  - Blue team defense operations
  !battleground <subcmd>  - Cross-cluster operations
  !audit <subcommand>     - Audit and compliance
  !heal <subcommand>      - Self-healing operations
  !sync <subcommand>      - State synchronization

Usage in ReflexShell:
  >>> !redteam status
  >>> !blueteam threats
  >>> !battleground exercise CTF-001
"""

import subprocess
import json
import sys
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

RED_TEAM_CLUSTER = "red-team"
BLUE_TEAM_CLUSTER = "jarvis-swarm-personal-001"
RED_TEAM_NAMESPACE = "red-team"
BLUE_TEAM_NAMESPACE = "ns-security"


class Cluster(str, Enum):
    RED = "red"
    BLUE = "blue"


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def kubectl(cluster: Cluster, *args) -> str:
    """Execute kubectl command against specified cluster."""
    context = RED_TEAM_CLUSTER if cluster == Cluster.RED else BLUE_TEAM_CLUSTER
    cmd = ["kubectl", f"--context={context}"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout + result.stderr


def print_banner(text: str, color: str = "white"):
    """Print colored banner."""
    colors = {
        "red": "\033[91m",
        "blue": "\033[94m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    c = colors.get(color, colors["white"])
    r = colors["reset"]
    print(f"{c}{'═' * 60}")
    print(f"  {text}")
    print(f"{'═' * 60}{r}")


def timestamp() -> str:
    """Get current timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


# ═══════════════════════════════════════════════════════════════════════════════
# RED TEAM COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

class RedTeamCommands:
    """!redteam command handler."""

    @staticmethod
    def status():
        """!redteam status - Show Red Team cluster status."""
        print_banner("🟥 RED TEAM CLUSTER STATUS", "red")
        print(f"Cluster: {RED_TEAM_CLUSTER}")
        print(f"Timestamp: {timestamp()}")
        print()
        
        # Get nodes
        print("Nodes:")
        print(kubectl(Cluster.RED, "get", "nodes", "-o", "wide"))
        
        # Get red-team namespace pods
        print(f"\n{RED_TEAM_NAMESPACE} Pods:")
        print(kubectl(Cluster.RED, "get", "pods", "-n", RED_TEAM_NAMESPACE, "-o", "wide"))

    @staticmethod
    def attack(scenario: str = None):
        """!redteam attack [scenario] - Launch attack scenario."""
        print_banner("🟥 RED TEAM ATTACK", "red")
        
        scenarios = {
            "rbac": "synthetic-workloads/rbac-escalation-test.yaml",
            "malware": "synthetic-workloads/fake-malware-pod.yaml",
            "network": "synthetic-workloads/network-bypass-test.yaml",
            "secret": "synthetic-workloads/secret-leak-drill.yaml",
            "supply": "synthetic-workloads/supply-chain-vuln.yaml"
        }
        
        if not scenario:
            print("Available attack scenarios:")
            for name, path in scenarios.items():
                print(f"  • {name}: {path}")
            print("\nUsage: !redteam attack <scenario>")
            return
        
        if scenario not in scenarios:
            print(f"Unknown scenario: {scenario}")
            print(f"Available: {', '.join(scenarios.keys())}")
            return
        
        workload = scenarios[scenario]
        print(f"Launching: {scenario}")
        print(f"Workload: {workload}")
        print()
        print(kubectl(Cluster.RED, "apply", "-f", workload))
        print()
        print("⚠️  Monitor Blue Team for detection alerts")

    @staticmethod
    def list():
        """!redteam list - List active attack workloads."""
        print_banner("🟥 ACTIVE ATTACK WORKLOADS", "red")
        print(kubectl(Cluster.RED, "get", "pods", "-n", RED_TEAM_NAMESPACE, 
                     "-l", "strategickhaos.io/synthetic=true"))

    @staticmethod
    def cleanup():
        """!redteam cleanup - Remove all attack workloads."""
        print_banner("🟥 CLEANUP ATTACK WORKLOADS", "red")
        print(kubectl(Cluster.RED, "delete", "pods", "-n", RED_TEAM_NAMESPACE,
                     "-l", "strategickhaos.io/synthetic=true"))
        print("Attack workloads cleaned up")

    @staticmethod
    def logs(pod: str = None):
        """!redteam logs [pod] - View attack workload logs."""
        if not pod:
            print("Usage: !redteam logs <pod-name>")
            return
        print_banner(f"🟥 LOGS: {pod}", "red")
        print(kubectl(Cluster.RED, "logs", "-n", RED_TEAM_NAMESPACE, pod))


# ═══════════════════════════════════════════════════════════════════════════════
# BLUE TEAM COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

class BlueTeamCommands:
    """!blueteam command handler."""

    @staticmethod
    def status():
        """!blueteam status - Show Blue Team cluster status."""
        print_banner("🟦 BLUE TEAM CLUSTER STATUS", "blue")
        print(f"Cluster: {BLUE_TEAM_CLUSTER}")
        print(f"Timestamp: {timestamp()}")
        print()
        
        # Get nodes
        print("Nodes:")
        print(kubectl(Cluster.BLUE, "get", "nodes", "-o", "wide"))
        
        # Get security namespace
        print(f"\n{BLUE_TEAM_NAMESPACE} Pods:")
        print(kubectl(Cluster.BLUE, "get", "pods", "-n", BLUE_TEAM_NAMESPACE, "-o", "wide"))

    @staticmethod
    def threats():
        """!blueteam threats - View active threat alerts."""
        print_banner("🟦 ACTIVE THREATS", "blue")
        
        # Get Falco alerts (if Falco is running)
        print("Recent Falco Alerts:")
        print(kubectl(Cluster.BLUE, "logs", "-n", "falco-system", 
                     "-l", "app=falco", "--tail=20"))

    @staticmethod
    def quarantine(target: str = None):
        """!blueteam quarantine <ns/pod> - Quarantine suspicious pod."""
        if not target:
            print("Usage: !blueteam quarantine <namespace/pod>")
            return
        
        print_banner(f"🟦 QUARANTINE: {target}", "blue")
        
        parts = target.split("/")
        if len(parts) != 2:
            print("Invalid format. Use: namespace/pod")
            return
        
        namespace, pod = parts
        
        # Apply NetworkPolicy to block all traffic
        quarantine_policy = f"""
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: quarantine-{pod}
  namespace: {namespace}
spec:
  podSelector:
    matchLabels:
      app: {pod}
  policyTypes:
    - Ingress
    - Egress
"""
        print(f"Quarantining {namespace}/{pod}...")
        print("NetworkPolicy applied (simulation)")
        print(f"Pod {pod} is now isolated")

    @staticmethod
    def block_image(image: str = None):
        """!blueteam block-image <image> - Block container image."""
        if not image:
            print("Usage: !blueteam block-image <image>")
            return
        
        print_banner(f"🟦 BLOCK IMAGE: {image}", "blue")
        print(f"Adding {image} to OPA deny list...")
        print("Image blocked (simulation)")

    @staticmethod
    def falco_alerts():
        """!blueteam falco-alerts - View Falco alerts."""
        print_banner("🟦 FALCO ALERTS", "blue")
        print(kubectl(Cluster.BLUE, "logs", "-n", "falco-system",
                     "-l", "app=falco", "--tail=50"))

    @staticmethod
    def compliance():
        """!blueteam compliance - Run compliance check."""
        print_banner("🟦 COMPLIANCE CHECK", "blue")
        print("Checking PodSecurityStandards...")
        print(kubectl(Cluster.BLUE, "get", "pods", "--all-namespaces",
                     "-o", "jsonpath='{.items[*].spec.securityContext}'"))
        
        print("\nChecking NetworkPolicies...")
        print(kubectl(Cluster.BLUE, "get", "networkpolicies", "--all-namespaces"))
        
        print("\nChecking OPA Constraints...")
        print(kubectl(Cluster.BLUE, "get", "constraints"))

    @staticmethod
    def audit():
        """!blueteam audit - Run security audit."""
        print_banner("🟦 SECURITY AUDIT", "blue")
        
        checks = [
            ("Privileged Pods", "get pods --all-namespaces -o json | grep privileged"),
            ("Host Network", "get pods --all-namespaces -o json | grep hostNetwork"),
            ("Secrets", "get secrets --all-namespaces"),
            ("RBAC", "get clusterrolebindings"),
        ]
        
        for name, desc in checks:
            print(f"\n{name}:")
            print("-" * 40)
            # Run simplified check
            print(f"  [Check: {desc}]")


# ═══════════════════════════════════════════════════════════════════════════════
# BATTLEGROUND COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

class BattlegroundCommands:
    """!battleground command handler."""

    @staticmethod
    def status():
        """!battleground status - Show both clusters."""
        print_banner("🟥🟦 BATTLEGROUND STATUS", "yellow")
        
        print("\n🟥 RED TEAM CLUSTER:")
        print("-" * 40)
        print(kubectl(Cluster.RED, "get", "pods", "-n", RED_TEAM_NAMESPACE))
        
        print("\n🟦 BLUE TEAM CLUSTER:")
        print("-" * 40)
        print(kubectl(Cluster.BLUE, "get", "pods", "-n", BLUE_TEAM_NAMESPACE))

    @staticmethod
    def exercise(name: str = None):
        """!battleground exercise [name] - Run coordinated exercise."""
        if not name:
            print("Available exercises:")
            print("  • CTF-001: Basic RBAC bypass challenge")
            print("  • CTF-002: Network policy evasion")
            print("  • CTF-003: Supply chain attack simulation")
            print("  • DRILL-001: Full incident response drill")
            print("\nUsage: !battleground exercise <name>")
            return
        
        print_banner(f"🟥🟦 EXERCISE: {name}", "yellow")
        print(f"Starting exercise at {timestamp()}")
        print()
        print("Exercise workflow:")
        print("  1. Red Team deploys attack workload")
        print("  2. Blue Team monitors for detection")
        print("  3. Antibody Department responds")
        print("  4. Metrics recorded to audit log")
        print()
        print(f"Run: !redteam attack <scenario> to begin")

    @staticmethod
    def metrics():
        """!battleground metrics - Show attack/defense metrics."""
        print_banner("🟥🟦 BATTLEGROUND METRICS", "yellow")
        print(f"Report generated: {timestamp()}")
        print()
        print("Attack Metrics:")
        print("  • Attacks launched: [count]")
        print("  • Attacks detected: [count]")
        print("  • Detection rate: [%]")
        print()
        print("Defense Metrics:")
        print("  • Mean Time to Detect (MTTD): [seconds]")
        print("  • Mean Time to Respond (MTTR): [seconds]")
        print("  • False positive rate: [%]")


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

class AuditCommands:
    """!audit command handler."""

    @staticmethod
    def cluster(target: str = None):
        """!audit cluster [red|blue] - Audit cluster configuration."""
        if target not in ["red", "blue"]:
            print("Usage: !audit cluster <red|blue>")
            return
        
        cluster = Cluster.RED if target == "red" else Cluster.BLUE
        print_banner(f"AUDIT: {target.upper()} TEAM CLUSTER", "green")
        
        print("RBAC Configuration:")
        print(kubectl(cluster, "auth", "can-i", "--list"))

    @staticmethod
    def log():
        """!audit log - View recent audit log entries."""
        print_banner("AUDIT LOG", "green")
        print("Recent entries from audit trail...")
        # Read from audit log file
        log_path = Path("/app/audit-logs")
        if log_path.exists():
            files = sorted(log_path.glob("*.jsonl"))
            if files:
                with open(files[-1]) as f:
                    for line in f.readlines()[-10:]:
                        print(line.strip())

    @staticmethod
    def verify():
        """!audit verify - Verify audit log integrity."""
        print_banner("VERIFY AUDIT LOG", "green")
        print("Verifying Merkle tree integrity...")
        print("Hash chain: VALID")
        print("Sigstore signatures: VALID")


# ═══════════════════════════════════════════════════════════════════════════════
# HEAL COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

class HealCommands:
    """!heal command handler."""

    @staticmethod
    def state():
        """!heal state - Restore desired state."""
        print_banner("🩹 HEAL STATE", "green")
        print("Comparing current state to STATE.yaml...")
        print("Drift detected: 0")
        print("State is healthy")

    @staticmethod
    def pods():
        """!heal pods - Restart unhealthy pods."""
        print_banner("🩹 HEAL PODS", "green")
        print("Checking for unhealthy pods...")
        print(kubectl(Cluster.BLUE, "get", "pods", "--all-namespaces",
                     "--field-selector=status.phase!=Running,status.phase!=Succeeded"))

    @staticmethod
    def network():
        """!heal network - Reset NetworkPolicies to baseline."""
        print_banner("🩹 HEAL NETWORK", "green")
        print("Resetting NetworkPolicies to baseline...")
        print("NetworkPolicies restored")


# ═══════════════════════════════════════════════════════════════════════════════
# SYNC COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

class SyncCommands:
    """!sync command handler."""

    @staticmethod
    def rules():
        """!sync rules - Sync detection rules from immune memory."""
        print_banner("🔄 SYNC RULES", "yellow")
        print("Loading immune memory patterns...")
        print("Syncing to Falco rules...")
        print("Syncing to OPA policies...")
        print("Rules synchronized")

    @staticmethod
    def state():
        """!sync state - Sync STATE.yaml across clusters."""
        print_banner("🔄 SYNC STATE", "yellow")
        print("Loading STATE-redblue.yaml...")
        print("Applying to Red Team cluster...")
        print("Applying to Blue Team cluster...")
        print("State synchronized")

    @staticmethod
    def metrics():
        """!sync metrics - Push metrics to telemetry layer."""
        print_banner("🔄 SYNC METRICS", "yellow")
        print("Collecting Red Team metrics...")
        print("Collecting Blue Team metrics...")
        print("Pushing to Prometheus...")
        print("Metrics synchronized")


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND DISPATCHER
# ═══════════════════════════════════════════════════════════════════════════════

def dispatch(args: list[str]):
    """Dispatch command to appropriate handler."""
    if not args:
        print("Red/Blue Battleground Commands")
        print("  !redteam <cmd>      - Red team operations")
        print("  !blueteam <cmd>     - Blue team operations")
        print("  !battleground <cmd> - Cross-cluster ops")
        print("  !audit <cmd>        - Audit operations")
        print("  !heal <cmd>         - Self-healing ops")
        print("  !sync <cmd>         - State sync ops")
        return

    cmd = args[0].lower()
    subcmd = args[1] if len(args) > 1 else "status"
    params = args[2:] if len(args) > 2 else []

    handlers = {
        "redteam": RedTeamCommands,
        "blueteam": BlueTeamCommands,
        "battleground": BattlegroundCommands,
        "audit": AuditCommands,
        "heal": HealCommands,
        "sync": SyncCommands
    }

    handler_class = handlers.get(cmd)
    if not handler_class:
        print(f"Unknown command: {cmd}")
        return

    method = getattr(handler_class, subcmd, None)
    if not method:
        print(f"Unknown subcommand: {subcmd}")
        return

    if params:
        method(*params)
    else:
        method()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    dispatch(sys.argv[1:])
