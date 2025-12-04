#!/usr/bin/env python3
"""
STRATEGICKHAOS LLM COUNCIL
Multi-model orchestration for AI consensus
"""

import requests
from typing import List, Dict

MODELS = {
    "llama1": "http://localhost:5001",
    "llama2": "http://localhost:5002",
    "llama3": "http://localhost:5003",
    "llama4": "http://localhost:5004",
    "llama5": "http://localhost:5005",
}


def query_all(prompt: str) -> List[Dict]:
    """Query all models and collect responses"""
    responses = []
    for name, url in MODELS.items():
        try:
            r = requests.post(f"{url}/inference", json={"prompt": prompt}, timeout=30)
            responses.append({"model": name, "response": r.json()})
        except Exception as e:
            responses.append({"model": name, "error": str(e)})
    return responses


def consensus(responses: List[Dict]) -> str:
    """Find consensus among model responses"""
    # Simple majority voting - enhance with weighted voting
    valid = [r for r in responses if "response" in r]
    if not valid:
        return "No consensus - all models failed"
    # TODO: Implement actual consensus algorithm
    return valid[0]["response"]


if __name__ == "__main__":
    print("🧠 LLM Council Ready")
    print(f"Models: {list(MODELS.keys())}")
