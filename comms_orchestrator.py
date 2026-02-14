#!/usr/bin/env python3
"""
Comms Orchestrator v1 - Sensory Cortex for REFLEXSHELL BRAIN
Strategickhaos DAO LLC | Node 137
Unified communication stream ingestion and neural pathway activation
"""

import os
import json
import time
import requests
import yaml
from pathlib import Path
from datetime import datetime, timezone
import argparse

# API Endpoints
API_GITHUB = "https://api.github.com"

def load_config(config_path):
    """Load YAML configuration file"""
    return yaml.safe_load(open(config_path))

def now_iso():
    """Current timestamp in ISO format"""
    return datetime.now(timezone.utc).isoformat()

def log_event(message):
    """Log with timestamp"""
    print(f"[{now_iso()}] SENSORY_CORTEX: {message}")

def github_headers():
    """GitHub API headers with authentication"""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

def fetch_github_notifications():
    """Fetch GitHub notifications and convert to unified event format"""
    events = []
    try:
        response = requests.get(f"{API_GITHUB}/notifications", headers=github_headers())
        response.raise_for_status()
        
        for notification in response.json():
            event = {
                "timestamp": notification["updated_at"],
                "source": "github",
                "event_type": "notification",
                "kind": notification["subject"]["type"],
                "title": notification["subject"]["title"],
                "repository": notification["repository"]["full_name"],
                "url": notification["subject"]["url"],
                "read": notification["unread"] == False,
                "reason": notification["reason"]
            }
            events.append(event)
            
    except Exception as e:
        log_event(f"GitHub fetch error: {e}")
        
    return events

def fetch_github_events():
    """Fetch GitHub user events"""
    events = []
    try:
        response = requests.get(f"{API_GITHUB}/users/Strategickhaos/events", headers=github_headers())
        response.raise_for_status()
        
        for event in response.json():
            unified_event = {
                "timestamp": event["created_at"],
                "source": "github", 
                "event_type": "activity",
                "kind": event["type"],
                "repository": event["repo"]["name"] if "repo" in event else None,
                "actor": event["actor"]["login"],
                "public": event["public"],
                "payload": event.get("payload", {})
            }
            events.append(unified_event)
            
    except Exception as e:
        log_event(f"GitHub events fetch error: {e}")
        
    return events

def append_events_to_log(events, log_path):
    """Append events to JSONL log file"""
    if not events:
        return
        
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    with log_path.open("a", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")

def forward_to_reflexshell(events, config):
    """Forward events to REFLEXSHELL BRAIN webhook"""
    if not config["integration"]["reflexshell_webhook"]["enabled"] or not events:
        return
        
    try:
        webhook_url = config["integration"]["reflexshell_webhook"]["url"]
        token = os.getenv('REFLEXSHELL_TOKEN')
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        payload = {
            "events": events,
            "source": "comms_orchestrator_v1",
            "timestamp": now_iso()
        }
        
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        log_event(f"Forwarded {len(events)} events to REFLEXSHELL BRAIN")
        
    except Exception as e:
        log_event(f"REFLEXSHELL forward error: {e}")

def main():
    """Main orchestrator loop"""
    parser = argparse.ArgumentParser(description="Comms Orchestrator v1")
    parser.add_argument("--config", required=True, help="Config file path")
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    log_event("SENSORY CORTEX v1 ACTIVATED")
    log_event(f"Config loaded: {args.config}")
    
    # Setup event log path
    event_log_path = Path(config["output"]["event_log"])
    log_event(f"Event log: {event_log_path}")
    
    # Main ingestion loop
    while True:
        try:
            all_events = []
            
            # Fetch from enabled sources
            if config["inputs"]["github"]["enabled"]:
                if config["inputs"]["github"]["notifications"]:
                    github_notifications = fetch_github_notifications()
                    all_events.extend(github_notifications)
                    
                if config["inputs"]["github"]["events"]:
                    github_events = fetch_github_events()
                    all_events.extend(github_events)
            
            # Process events if any were collected
            if all_events:
                # Limit events per run
                max_events = config["output"]["max_events_per_run"]
                if len(all_events) > max_events:
                    all_events = all_events[:max_events]
                
                # Append to event log
                append_events_to_log(all_events, event_log_path)
                
                # Forward to REFLEXSHELL BRAIN
                forward_to_reflexshell(all_events, config)
                
                log_event(f"NEURAL PATHWAY FIRED: {len(all_events)} events ingested")
            else:
                log_event("No new events detected")
                
        except Exception as e:
            log_event(f"Main loop error: {e}")
            
        # Sleep for 5 minutes
        time.sleep(300)

if __name__ == "__main__":
    main()