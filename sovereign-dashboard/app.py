#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
SOVEREIGN CONTROL DECK v2.0
StrategicKhaos DAO LLC

Flask-based dashboard for dual-cluster Kubernetes cyber lab operations.
Provides real-time visibility into Blue Team and Red Team clusters.
═══════════════════════════════════════════════════════════════════════════════
"""

import yaml
from flask import Flask, render_template, jsonify
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

# Configuration
STATE_PATH = Path(__file__).parent / "STATE.yaml"
BLUE_TEAM_CLUSTER = "jarvis-swarm-personal-001"
RED_TEAM_CLUSTER = "red-team"


def load_state():
    """Load state configuration from STATE.yaml."""
    if not STATE_PATH.exists():
        return {
            "error": "STATE.yaml not found",
            "clusters": {
                "blue_team": {"name": BLUE_TEAM_CLUSTER, "status": "unknown"},
                "red_team": {"name": RED_TEAM_CLUSTER, "status": "unknown"}
            }
        }
    with open(STATE_PATH) as f:
        return yaml.safe_load(f)


def print_banner():
    """Print startup banner."""
    print("═" * 60)
    print("  SOVEREIGN CONTROL DECK v2.0")
    print("  StrategicKhaos DAO LLC")
    print("═" * 60)
    print(f"  Blue Team: {BLUE_TEAM_CLUSTER}")
    print(f"  Red Team: {RED_TEAM_CLUSTER}")
    print("═" * 60)


@app.route("/")
def index():
    """Main dashboard view."""
    state = load_state()
    return render_template("index.html", state=state)


@app.route("/api/status")
def api_status():
    """API endpoint for cluster status."""
    state = load_state()
    return jsonify({
        "timestamp": datetime.utcnow().isoformat(),
        "clusters": state.get("clusters", {}),
        "version": "2.0"
    })


@app.route("/api/health")
def api_health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})


if __name__ == "__main__":
    print_banner()
    app.run(host="0.0.0.0", port=8080, debug=True)
