#!/usr/bin/env python3
"""
STRATEGICKHAOS HR API
Strategickhaos DAO LLC | Node 137
Agent governance, complaints, and organizational intelligence
"""

import os
import json
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import requests

# === DATA MODELS ===

class Agent(BaseModel):
    id: str
    name: str
    role: str
    status: str = "active"
    last_seen: Optional[str] = None
    complaints: int = 0
    performance_score: float = 100.0
    specialties: List[str] = []

class Complaint(BaseModel):
    id: str
    agent_id: str
    issue: str
    severity: str = "low"  # low, medium, high, critical
    status: str = "open"  # open, investigating, resolved
    timestamp: str
    reporter: str = "system"

class RestartRequest(BaseModel):
    agent_id: str
    reason: str
    authorized_by: str

class OrganizationStats(BaseModel):
    total_agents: int
    active_agents: int
    pending_complaints: int
    average_performance: float
    system_health: str

# === FASTAPI APP ===

app = FastAPI(
    title="STRATEGICKHAOS HR API",
    description="Agent governance and organizational intelligence",
    version="1.0.0"
)

# === REDIS CONNECTION ===

redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

# === HUMOR CONFIG ===

HUMOR_ENABLED = os.getenv('HR_HUMOR', 'false').lower() == 'true'

def get_hr_response(message: str) -> str:
    """Add some humor to HR responses if enabled"""
    if not HUMOR_ENABLED:
        return message
    
    humor_responses = {
        "agent_created": f"{message} Welcome to the machine, agent.",
        "complaint_filed": f"{message} Another day, another complaint. Sigh.",
        "agent_restarted": f"{message} Did you try turning it off and on again?",
        "performance_review": f"{message} Performance is relative, like everything else.",
        "system_healthy": f"{message} All systems nominal. For now.",
        "default": f"{message} HR is watching. Always watching."
    }
    
    return humor_responses.get("default", message)

def log_event(event_type: str, data: Dict[str, Any]):
    """Log HR events to Redis"""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": event_type,
        "data": data
    }
    redis_client.lpush("hr_events", json.dumps(event))

# === AGENT MANAGEMENT ===

@app.post("/agents")
async def create_agent(agent: Agent):
    """Create a new agent in the system"""
    agent.last_seen = datetime.now(timezone.utc).isoformat()
    
    # Store in Redis
    redis_client.hset("agents", agent.id, agent.json())
    
    # Log event
    log_event("agent_created", agent.dict())
    
    return {
        "status": "created",
        "agent_id": agent.id,
        "message": get_hr_response("Agent successfully onboarded.")
    }

@app.get("/agents")
async def list_agents():
    """List all agents in the system"""
    agents_data = redis_client.hgetall("agents")
    agents = []
    
    for agent_id, agent_json in agents_data.items():
        agent_dict = json.loads(agent_json)
        agents.append(agent_dict)
    
    return {"agents": agents}

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent details"""
    agent_data = redis_client.hget("agents", agent_id)
    
    if not agent_data:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return json.loads(agent_data)

@app.put("/agents/{agent_id}/status")
async def update_agent_status(agent_id: str, status: str):
    """Update agent status"""
    agent_data = redis_client.hget("agents", agent_id)
    
    if not agent_data:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = json.loads(agent_data)
    agent["status"] = status
    agent["last_seen"] = datetime.now(timezone.utc).isoformat()
    
    redis_client.hset("agents", agent_id, json.dumps(agent))
    
    log_event("status_updated", {"agent_id": agent_id, "status": status})\n    \n    return {\n        \"status\": \"updated\",\n        \"agent_id\": agent_id,\n        \"new_status\": status,\n        \"message\": get_hr_response(\"Agent status updated.\")\n    }\n\n# === COMPLAINT SYSTEM ===\n\n@app.post(\"/complaints\")\nasync def file_complaint(complaint: Complaint):\n    \"\"\"File a complaint against an agent\"\"\"\n    complaint.timestamp = datetime.now(timezone.utc).isoformat()\n    \n    # Store complaint\n    redis_client.hset(\"complaints\", complaint.id, complaint.json())\n    \n    # Update agent complaint count\n    agent_data = redis_client.hget(\"agents\", complaint.agent_id)\n    if agent_data:\n        agent = json.loads(agent_data)\n        agent[\"complaints\"] += 1\n        redis_client.hset(\"agents\", complaint.agent_id, json.dumps(agent))\n    \n    # Log event\n    log_event(\"complaint_filed\", complaint.dict())\n    \n    return {\n        \"status\": \"filed\",\n        \"complaint_id\": complaint.id,\n        \"message\": get_hr_response(\"Complaint has been logged and will be investigated.\")\n    }\n\n@app.get(\"/complaints\")\nasync def list_complaints(status: Optional[str] = None):\n    \"\"\"List all complaints, optionally filtered by status\"\"\"\n    complaints_data = redis_client.hgetall(\"complaints\")\n    complaints = []\n    \n    for complaint_id, complaint_json in complaints_data.items():\n        complaint_dict = json.loads(complaint_json)\n        \n        if status and complaint_dict.get(\"status\") != status:\n            continue\n            \n        complaints.append(complaint_dict)\n    \n    return {\"complaints\": complaints}\n\n@app.put(\"/complaints/{complaint_id}/status\")\nasync def update_complaint_status(complaint_id: str, status: str):\n    \"\"\"Update complaint status\"\"\"\n    complaint_data = redis_client.hget(\"complaints\", complaint_id)\n    \n    if not complaint_data:\n        raise HTTPException(status_code=404, detail=\"Complaint not found\")\n    \n    complaint = json.loads(complaint_data)\n    complaint[\"status\"] = status\n    \n    redis_client.hset(\"complaints\", complaint_id, json.dumps(complaint))\n    \n    log_event(\"complaint_updated\", {\"complaint_id\": complaint_id, \"status\": status})\n    \n    return {\n        \"status\": \"updated\",\n        \"complaint_id\": complaint_id,\n        \"new_status\": status\n    }\n\n# === AGENT RESTART SYSTEM ===\n\n@app.post(\"/restart\")\nasync def restart_agent(request: RestartRequest):\n    \"\"\"Restart a problematic agent\"\"\"\n    agent_data = redis_client.hget(\"agents\", request.agent_id)\n    \n    if not agent_data:\n        raise HTTPException(status_code=404, detail=\"Agent not found\")\n    \n    # Update agent status\n    agent = json.loads(agent_data)\n    agent[\"status\"] = \"restarting\"\n    agent[\"last_seen\"] = datetime.now(timezone.utc).isoformat()\n    \n    redis_client.hset(\"agents\", request.agent_id, json.dumps(agent))\n    \n    # Log restart event\n    log_event(\"agent_restarted\", {\n        \"agent_id\": request.agent_id,\n        \"reason\": request.reason,\n        \"authorized_by\": request.authorized_by\n    })\n    \n    return {\n        \"status\": \"restarting\",\n        \"agent_id\": request.agent_id,\n        \"message\": get_hr_response(\"Agent restart initiated. Please stand by.\")\n    }\n\n# === ORGANIZATION STATS ===\n\n@app.get(\"/stats\", response_model=OrganizationStats)\nasync def get_organization_stats():\n    \"\"\"Get overall organization statistics\"\"\"\n    agents_data = redis_client.hgetall(\"agents\")\n    complaints_data = redis_client.hgetall(\"complaints\")\n    \n    total_agents = len(agents_data)\n    active_agents = 0\n    total_performance = 0.0\n    \n    for agent_json in agents_data.values():\n        agent = json.loads(agent_json)\n        if agent.get(\"status\") == \"active\":\n            active_agents += 1\n        total_performance += agent.get(\"performance_score\", 100.0)\n    \n    pending_complaints = 0\n    for complaint_json in complaints_data.values():\n        complaint = json.loads(complaint_json)\n        if complaint.get(\"status\") == \"open\":\n            pending_complaints += 1\n    \n    average_performance = total_performance / total_agents if total_agents > 0 else 100.0\n    \n    # Determine system health\n    health = \"excellent\"\n    if pending_complaints > 5:\n        health = \"poor\"\n    elif pending_complaints > 2:\n        health = \"fair\"\n    elif average_performance < 80:\n        health = \"concerning\"\n    \n    return OrganizationStats(\n        total_agents=total_agents,\n        active_agents=active_agents,\n        pending_complaints=pending_complaints,\n        average_performance=average_performance,\n        system_health=health\n    )\n\n# === JARVIS INTEGRATION ===\n\n@app.post(\"/jarvis/employee_status\")\nasync def jarvis_employee_status():\n    \"\"\"Get employee status for Jarvis voice reports\"\"\"\n    stats = await get_organization_stats()\n    \n    response = {\n        \"speech\": f\"We have {stats.total_agents} agents. {stats.active_agents} active. {stats.pending_complaints} pending complaints. System health: {stats.system_health}.\",\n        \"data\": stats\n    }\n    \n    return response\n\n@app.get(\"/events\")\nasync def get_hr_events(limit: int = 50):\n    \"\"\"Get recent HR events\"\"\"\n    events_data = redis_client.lrange(\"hr_events\", 0, limit - 1)\n    events = [json.loads(event_data) for event_data in events_data]\n    \n    return {\"events\": events}\n\n@app.get(\"/health\")\nasync def health_check():\n    \"\"\"Health check endpoint\"\"\"\n    return {\n        \"status\": \"healthy\",\n        \"timestamp\": datetime.now(timezone.utc).isoformat(),\n        \"version\": \"1.0.0\",\n        \"hr_system\": \"OPERATIONAL\",\n        \"message\": get_hr_response(\"HR systems are functioning normally.\")\n    }\n\nif __name__ == \"__main__\":\n    import uvicorn\n    \n    print(\"👔 STRATEGICKHAOS HR API - INITIALIZING\")\n    print(\"📋 Agent governance: ACTIVE\")\n    print(\"📞 Complaint system: ONLINE\")\n    print(\"🔄 Restart protocols: ARMED\")\n    \n    if HUMOR_ENABLED:\n        print(\"😄 HR humor mode: ENABLED (because why not?)\")\n    \n    uvicorn.run(app, host=\"0.0.0.0\", port=8002)