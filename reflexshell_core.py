#!/usr/bin/env python3
"""
REFLEXSHELL BRAIN v1 - Core Webhook Server
Strategickhaos DAO LLC | Node 137
Cognitive event processing and contradiction analysis
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import uvicorn

# Data models
class CommEvent(BaseModel):
    timestamp: str
    source: str
    event_type: str
    kind: str
    title: str = None
    repository: str = None
    url: str = None

class EventBatch(BaseModel):
    events: List[CommEvent]
    source: str
    timestamp: str

# FastAPI app
app = FastAPI(title="REFLEXSHELL BRAIN v1", version="1.0.0")

# Authentication
def verify_token(authorization: str = Header(None)):
    """Verify REFLEXSHELL_TOKEN"""
    expected_token = os.getenv('REFLEXSHELL_TOKEN')
    if not expected_token:
        return True  # No auth required if token not set
    
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(' ')[1]
    if token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return True

@app.post("/events")
async def receive_events(batch: EventBatch, auth: bool = Depends(verify_token)):
    """Receive events from comms orchestrator"""
    
    # Log received events
    log_path = Path("/data/reflexshell/brain_events.jsonl")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    with log_path.open("a") as f:
        for event in batch.events:
            brain_event = {
                "received_at": datetime.now(timezone.utc).isoformat(),
                "batch_source": batch.source,
                "batch_timestamp": batch.timestamp,
                **event.dict()
            }
            f.write(json.dumps(brain_event) + "\n")
    
    # Process events for contradictions (placeholder)
    contradictions_found = analyze_contradictions(batch.events)
    
    return {
        "status": "processed",
        "events_received": len(batch.events),
        "contradictions_found": contradictions_found,
        "brain_status": "NEURAL_PATHWAYS_FIRING"
    }

@app.get("/events/query")
async def query_events(
    q: str = None,
    source: str = None,
    event_type: str = None,
    limit: int = 100
):
    """Query unified event stream"""
    
    log_path = Path("/data/reflexshell/brain_events.jsonl")
    if not log_path.exists():
        return {"events": [], "total": 0}
    
    events = []
    with log_path.open("r") as f:
        for line in f:
            try:
                event = json.loads(line.strip())
                
                # Apply filters
                if source and event.get("source") != source:
                    continue
                if event_type and event.get("event_type") != event_type:
                    continue
                if q and q.lower() not in str(event).lower():
                    continue
                
                events.append(event)
                
                if len(events) >= limit:
                    break
                    
            except json.JSONDecodeError:
                continue
    
    # Reverse to get most recent first
    events.reverse()
    
    return {
        "events": events[:limit],
        "total": len(events),
        "query": {
            "q": q,
            "source": source,
            "event_type": event_type,
            "limit": limit
        }
    }

@app.get("/brain/status")
async def brain_status():
    """Get REFLEXSHELL BRAIN status"""
    
    log_path = Path("/data/reflexshell/brain_events.jsonl")
    event_count = 0
    
    if log_path.exists():
        with log_path.open("r") as f:
            event_count = sum(1 for _ in f)
    
    return {
        "status": "COGNITIVE_PROCESSES_ACTIVE",
        "total_events_processed": event_count,
        "neural_pathways": "FIRING",
        "contradiction_engine": "ONLINE",
        "sensory_cortex": "ACTIVATED"
    }

def analyze_contradictions(events: List[CommEvent]) -> int:
    """
    Analyze events for contradictions
    TODO: Implement actual contradiction detection logic
    """
    # Placeholder - count events with conflicting information
    contradiction_count = 0
    
    # Simple heuristic: look for opposing keywords
    opposing_pairs = [
        ("approve", "reject"),
        ("merge", "close"),
        ("fix", "break"),
        ("add", "remove")
    ]
    
    event_texts = [f"{e.title} {e.kind}" for e in events if e.title]
    
    for pair in opposing_pairs:
        word1_found = any(pair[0] in text.lower() for text in event_texts)
        word2_found = any(pair[1] in text.lower() for text in event_texts)
        
        if word1_found and word2_found:
            contradiction_count += 1
    
    return contradiction_count

if __name__ == "__main__":
    print("🧠 REFLEXSHELL BRAIN v1 - COGNITIVE PROCESSES INITIALIZING")
    print("🔗 Neural pathways: ESTABLISHING")
    print("🎯 Contradiction engine: LOADING")
    print("📡 Webhook server: ACTIVATING")
    
    uvicorn.run(app, host="0.0.0.0", port=8080)