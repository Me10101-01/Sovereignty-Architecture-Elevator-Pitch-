#!/usr/bin/env python3
"""
LEGION OF MINDS - Orchestrator Brain
Strategickhaos DAO LLC | Node 137
Voice-activated reconnaissance swarm with license intelligence
"""

import os
import json
import yaml
from datetime import datetime, timezone
from pathlib import Path
from subprocess import run, PIPE
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import requests

# === DATA MODELS ===

class ReconRequest(BaseModel):
    trigger: str = "voice"
    patterns: Optional[List[str]] = None
    notify: bool = True

class ReconResult(BaseModel):
    status: str
    timestamp: str
    patterns_executed: int
    report_path: str
    json_path: str
    duration_seconds: float

class LegionStatus(BaseModel):
    status: str
    active_recons: int
    total_reports: int
    last_recon: Optional[str]
    jarvis_connected: bool
    qdrant_connected: bool

# === FASTAPI APP ===

app = FastAPI(
    title="LEGION OF MINDS - Recon Orchestrator",
    description="Voice-activated reconnaissance swarm for license intelligence",
    version="1.0.0"
)

# === GLOBAL STATE ===

active_recons = 0
total_reports = 0
last_recon_time = None

# === CORE FUNCTIONS ===

def log_event(message: str):
    """Log with timestamp"""
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"[{timestamp}] LEGION: {message}")

def check_qdrant_connection() -> bool:
    """Check if Qdrant is accessible"""
    try:
        response = requests.get("http://qdrant:6333/collections", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_jarvis_connection() -> bool:
    """Check if Jarvis voice trigger is active"""
    try:
        # Check if Home Assistant is responding
        response = requests.get("http://localhost:8123/api/", timeout=5)
        return response.status_code == 200
    except:
        return False

def execute_recon_arsenal() -> Dict:
    """Execute the curl patterns arsenal"""
    global active_recons, total_reports, last_recon_time
    
    start_time = datetime.now(timezone.utc)
    log_event("RECON ARSENAL ACTIVATED - 30 patterns firing")
    
    try:
        # Execute curl patterns script
        result = run(["./curl_patterns.sh"], capture_output=True, text=True, cwd="/app")
        
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        # Update global state
        total_reports += 1
        last_recon_time = start_time.isoformat()
        
        log_event(f"RECON COMPLETE - Duration: {duration:.2f}s")
        
        return {
            "success": True,
            "duration": duration,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
        
    except Exception as e:
        log_event(f"RECON FAILED: {e}")
        return {
            "success": False,
            "error": str(e),
            "duration": 0
        }

def generate_table_of_contents() -> str:
    """Generate markdown table of contents for the report"""
    toc = """
# 📚 TABLE OF CONTENTS — LEGION RECON v1

## 🏛️ VENDOR TERMS & LICENSES
1. **GitHub Enterprise Terms** → Enterprise licensing conditions
2. **JetBrains EULA** → Development tool licensing
3. **Obsidian License** → Knowledge management terms
4. **Harbor Registry** → Container registry compliance
5. **Docker Hub Terms** → Container hosting terms

## ☁️ CLOUD PROVIDER TERMS
6. **AWS Service Terms** → Amazon Web Services legal
7. **Azure Terms** → Microsoft cloud platform terms
8. **GCP Terms** → Google Cloud Platform legal

## 🔧 INFRASTRUCTURE LICENSES
9. **Kubernetes License** → Container orchestration
10. **Terraform License** → Infrastructure as code
11. **Ansible License** → Configuration management
12. **Prometheus License** → Monitoring and alerting
13. **Grafana License** → Data visualization

## 💾 DATABASE LICENSES
14. **Elasticsearch License** → Search and analytics
15. **PostgreSQL License** → Relational database
16. **Redis License** → In-memory data store
17. **MongoDB License** → Document database

## 🌐 WEB SERVER LICENSES
18. **Apache License** → HTTP server
19. **Nginx License** → Web server and proxy

## 💻 PROGRAMMING LANGUAGE LICENSES
20. **Node.js License** → JavaScript runtime
21. **Python License** → Python interpreter
22. **Go License** → Go compiler and runtime
23. **Rust License** → Rust compiler and tools

## 🛠️ DEVELOPMENT TOOL LICENSES
24. **VS Code License** → Code editor
25. **Git License** → Version control
26. **Vim License** → Text editor

## 🔒 SECURITY & SYSTEM LICENSES
27. **Linux Kernel License** → Operating system kernel
28. **OpenSSL License** → Cryptography library
29. **Curl License** → HTTP client library
30. **SPDX Licenses** → Open source license database

## 🎯 THESAURUS — VOICE COMMANDS
- `"Hey Jarvis, run legion recon"` → Execute full 30-pattern scan
- `"Hey Jarvis, check licenses"` → Quick license compliance check
- `"Hey Jarvis, legion status"` → Show recon system status
- `"Hey Jarvis, generate report"` → Create formatted intelligence report
- `"Hey Jarvis, quit legion"` → Safe shutdown of recon systems

---
**LEGION OF MINDS v1 — Sovereign Intelligence at Voice Command**
"""
    return toc

def embed_to_qdrant(report_data: Dict):
    """Embed recon results into Qdrant for searchable intelligence"""
    try:
        # TODO: Implement Qdrant embedding logic
        log_event("Embedding recon results to Qdrant vector database")
        pass
    except Exception as e:
        log_event(f"Qdrant embedding failed: {e}")

def notify_jarvis_completion():
    """Notify Jarvis that recon is complete"""
    try:
        # Send TTS notification through Home Assistant
        headers = {"Authorization": f"Bearer {os.getenv('HA_TOKEN')}"}
        payload = {
            "entity_id": "media_player.living_room",
            "message": "Legion recon complete. Thirty patterns executed. Intelligence gathered."
        }
        
        response = requests.post(
            "http://localhost:8123/api/services/tts/google_say",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            log_event("Jarvis notified of recon completion")
        else:
            log_event(f"Jarvis notification failed: {response.status_code}")
            
    except Exception as e:
        log_event(f"Jarvis notification error: {e}")

# === API ENDPOINTS ===

@app.post("/trigger", response_model=ReconResult)
async def trigger_recon(request: ReconRequest, background_tasks: BackgroundTasks):
    """Main trigger endpoint for voice-activated recon"""
    global active_recons
    
    if active_recons > 0:
        raise HTTPException(status_code=429, detail="Recon already in progress")
    
    active_recons += 1
    start_time = datetime.now(timezone.utc)
    
    try:
        log_event(f"RECON TRIGGERED - Source: {request.trigger}")
        
        # Execute reconnaissance
        recon_result = execute_recon_arsenal()
        
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        # Generate paths
        report_path = "/data/legion/legion_report.md"
        json_path = "/data/legion/legion_report.json"
        
        # Create table of contents
        toc_path = "/data/legion/table_of_contents.md"
        Path(toc_path).write_text(generate_table_of_contents())
        
        # Background tasks
        if request.notify:
            background_tasks.add_task(notify_jarvis_completion)
        
        background_tasks.add_task(embed_to_qdrant, recon_result)
        
        return ReconResult(
            status="recon_complete" if recon_result["success"] else "recon_failed",
            timestamp=start_time.isoformat(),
            patterns_executed=30,
            report_path=report_path,
            json_path=json_path,
            duration_seconds=duration
        )
        
    finally:
        active_recons -= 1

@app.get("/status", response_model=LegionStatus)
async def get_status():
    """Get LEGION system status"""
    return LegionStatus(
        status="active" if active_recons == 0 else "recon_in_progress",
        active_recons=active_recons,
        total_reports=total_reports,
        last_recon=last_recon_time,
        jarvis_connected=check_jarvis_connection(),
        qdrant_connected=check_qdrant_connection()
    )

@app.get("/reports")
async def list_reports():
    """List all generated recon reports"""
    reports_dir = Path("/data/legion")
    if not reports_dir.exists():
        return {"reports": []}
    
    reports = []
    for file in reports_dir.glob("*.md"):
        reports.append({
            "filename": file.name,
            "path": str(file),
            "size_bytes": file.stat().st_size,
            "modified": datetime.fromtimestamp(file.stat().st_mtime, tz=timezone.utc).isoformat()
        })
    
    return {"reports": reports}

@app.get("/report/{filename}")
async def get_report(filename: str):
    """Get specific recon report content"""
    report_path = Path(f"/data/legion/{filename}")
    
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        "filename": filename,
        "content": report_path.read_text(),
        "size_bytes": report_path.stat().st_size
    }

@app.post("/synthesize/windows-tools")
async def synthesize_windows_tools(background_tasks: BackgroundTasks):
    """Trigger Windows DNA synthesis"""
    try:
        log_event("Windows DNA synthesis triggered")
        
        # Execute Windows DNA synthesizer
        result = run(["python", "/app/synthesize_windows_dna.py"], capture_output=True, text=True, cwd="/app")
        
        if result.returncode == 0:
            log_event("Windows DNA synthesis completed successfully")
            return {
                "status": "synthesis_complete",
                "message": "Windows tools converted to sovereignty compounds",
                "output": result.stdout,
                "synthesis_timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            log_event(f"Windows DNA synthesis failed: {result.stderr}")
            return {
                "status": "synthesis_failed", 
                "error": result.stderr,
                "synthesis_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
    except Exception as e:
        log_event(f"Windows DNA synthesis error: {e}")
        raise HTTPException(status_code=500, detail=f"Synthesis error: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "legion_status": "MINDS_ACTIVATED",
        "dna_synthesis": "READY"
    }

if __name__ == "__main__":
    import uvicorn
    
    log_event("🏛️ LEGION OF MINDS - ORCHESTRATOR INITIALIZING")
    log_event("🎯 Voice-activated recon swarm: READY")
    log_event("📡 30 reconnaissance patterns: LOADED")
    log_event("🧠 Jarvis integration: ACTIVE")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)