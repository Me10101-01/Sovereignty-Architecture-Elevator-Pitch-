#!/usr/bin/env python3
"""
LangChain Worker for STRATEGICKHAOS Empire
AI processing with OpenAI integration
"""

import os
import json
import redis
import requests
from datetime import datetime, timezone

# === LANGCHAIN IMPORTS ===
try:
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
    from langchain_community.vectorstores import Qdrant
    from langchain_community.embeddings import OpenAIEmbeddings
except ImportError:
    print("LangChain imports failed - running in mock mode")
    ChatOpenAI = None

# === REDIS CONNECTION ===

redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

def log_event(message: str):
    """Log worker events"""
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"[{timestamp}] LANGCHAIN_WORKER: {message}")

def get_prompt_template(template_name: str, variables: dict = None):
    """Get prompt from prompt service"""
    try:
        response = requests.post(
            "http://promptsvc:8010/generate",
            json={"template_name": template_name, "variables": variables or {}},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get("prompt")
    except:
        pass
    return None

def process_with_openai(prompt: str, system_prompt: str = None):
    """Process prompt with OpenAI"""
    if not ChatOpenAI:
        return {"error": "LangChain not available", "mock_response": "This would be processed by OpenAI"}
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return {"error": "OpenAI API key not configured"}
    
    try:
        llm = ChatOpenAI(api_key=api_key, model="gpt-4")
        
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        
        response = llm(messages)
        return {"response": response.content, "model": "gpt-4"}
        
    except Exception as e:
        return {"error": str(e)}

def main_worker_loop():
    """Main worker processing loop"""
    log_event("WORKER STARTING - Listening for tasks")
    
    while True:
        try:
            # Listen for tasks from Redis queue
            task_data = redis_client.blpop("langchain_tasks", timeout=5)
            
            if task_data:
                task_json = task_data[1].decode('utf-8')
                task = json.loads(task_json)
                
                log_event(f"Processing task: {task.get('type', 'unknown')}")
                
                # Process different task types
                if task.get('type') == 'analyze_recon':
                    result = process_recon_analysis(task)
                elif task.get('type') == 'process_prompt':
                    result = process_custom_prompt(task)
                else:
                    result = {"error": "Unknown task type"}
                
                # Store result
                result_key = f"langchain_result:{task.get('id', 'unknown')}"
                redis_client.setex(result_key, 3600, json.dumps(result))  # 1 hour expiry
                
                log_event(f"Task completed: {task.get('id')}")
                
        except Exception as e:
            log_event(f"Worker error: {e}")

def process_recon_analysis(task):
    """Process reconnaissance data analysis"""
    data = task.get('data', '')
    target = task.get('target', 'unknown')
    
    # Get analysis prompt template
    prompt = get_prompt_template('recon_analysis', {
        'target': target,
        'aspects': 'licensing, compliance, security',
        'focus_areas': 'legal risks, technical dependencies, security implications'
    })
    
    if not prompt:
        prompt = f"Analyze this reconnaissance data for {target}:\\n\\n{data}"
    
    system_prompt = "You are a security analyst for STRATEGICKHAOS DAO. Analyze data for compliance, security, and legal implications."
    
    return process_with_openai(prompt, system_prompt)

def process_custom_prompt(task):
    """Process custom prompt task"""
    prompt = task.get('prompt', '')
    system_prompt = task.get('system_prompt')
    
    return process_with_openai(prompt, system_prompt)

if __name__ == "__main__":
    main_worker_loop()