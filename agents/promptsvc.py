#!/usr/bin/env python3
"""
Prompt Service for STRATEGICKHAOS Empire
Dynamic prompt templating and management
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import yaml

app = FastAPI(title="STRATEGICKHAOS Prompt Service", version="1.0.0")

class PromptTemplate(BaseModel):
    name: str
    template: str
    variables: List[str] = []
    category: str = "general"
    description: str = ""

class PromptRequest(BaseModel):
    template_name: str
    variables: Dict[str, Any] = {}

# === BUILT-IN TEMPLATES ===

TEMPLATES = {
    "recon_analysis": PromptTemplate(
        name="recon_analysis",
        template="Analyze the following reconnaissance data for {target}. Focus on {aspects}. Provide insights on: {focus_areas}",
        variables=["target", "aspects", "focus_areas"],
        category="intelligence",
        description="Analyze recon data for intelligence gathering"
    ),
    
    "license_compliance": PromptTemplate(
        name="license_compliance",
        template="Review the license terms for {software} and assess compliance for {use_case}. Consider: {legal_requirements}",
        variables=["software", "use_case", "legal_requirements"],
        category="legal",
        description="Assess software license compliance"
    ),
    
    "agent_performance": PromptTemplate(
        name="agent_performance",
        template="Evaluate agent {agent_name} performance. Current metrics: {metrics}. Recommend improvements for: {areas}",
        variables=["agent_name", "metrics", "areas"],
        category="hr",
        description="Evaluate and improve agent performance"
    ),
    
    "threat_analysis": PromptTemplate(
        name="threat_analysis",
        template="Analyze potential threats from {source}. Risk level: {risk_level}. Mitigation strategies: {strategies}",
        variables=["source", "risk_level", "strategies"],
        category="security",
        description="Analyze and mitigate security threats"
    )
}

@app.get("/templates")
async def list_templates():
    """List all available prompt templates"""
    return {"templates": list(TEMPLATES.keys())}

@app.get("/templates/{template_name}")
async def get_template(template_name: str):
    """Get specific template details"""
    if template_name not in TEMPLATES:
        return {"error": "Template not found"}
    
    return TEMPLATES[template_name]

@app.post("/generate")
async def generate_prompt(request: PromptRequest):
    """Generate a prompt from template and variables"""
    if request.template_name not in TEMPLATES:
        return {"error": "Template not found"}
    
    template = TEMPLATES[request.template_name]
    
    try:
        prompt = template.template.format(**request.variables)
        return {
            "prompt": prompt,
            "template_used": request.template_name,
            "variables": request.variables
        }
    except KeyError as e:
        return {"error": f"Missing variable: {e}"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "templates_loaded": len(TEMPLATES)}