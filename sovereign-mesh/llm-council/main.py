#!/usr/bin/env python3
"""
STRATEGICKHAOS LLM COUNCIL
Multi-model orchestration for AI consensus
"""

import requests
from typing import List, Dict
from collections import Counter

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
            r.raise_for_status()  # Raise exception for HTTP errors
            responses.append({"model": name, "response": r.json()})
        except requests.exceptions.HTTPError as e:
            responses.append({"model": name, "error": f"HTTP error: {e.response.status_code}"})
        except requests.exceptions.RequestException as e:
            responses.append({"model": name, "error": str(e)})
    return responses


def consensus(responses: List[Dict]) -> str:
    """Find consensus among model responses using majority voting"""
    valid = [r for r in responses if "response" in r]
    if not valid:
        return "No consensus - all models failed"
    
    # Extract response text for voting
    response_texts = []
    for r in valid:
        resp = r.get("response", {})
        if isinstance(resp, dict):
            response_texts.append(resp.get("response", str(resp)))
        else:
            response_texts.append(str(resp))
    
    # Simple majority voting
    if response_texts:
        counter = Counter(response_texts)
        most_common = counter.most_common(1)
        if most_common:
            return most_common[0][0]
    
    # Fallback to first response if no majority
    return response_texts[0] if response_texts else "No consensus"


if __name__ == "__main__":
    print("🧠 LLM Council Ready")
    print(f"Models: {list(MODELS.keys())}")
