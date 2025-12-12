# SovereignPRManager v1.0
## Autonomous Pull Request Orchestration System

**Philosophy:** Zero-button operation through multi-AI synthesis

**Status:** 🟢 ACTIVE

**Confidence Threshold:** 90% for auto-merge

**Legion Members:**
- Claude: Security + Sovereignty review
- GPT-4: Architecture + Performance review  
- Grok: Pattern recognition + Synthesis
- Gemini: Compliance validation

**Architecture:** Dialectical synthesis → Cryptographic provenance → Auto-merge

## Overview

SovereignPRManager is an autonomous PR orchestration system that coordinates multiple AI agents for:
- Multi-perspective code review (security, architecture, sovereignty)
- Conflict detection (git, semantic, dependency)
- Dialectical synthesis engine for merge decisions
- Auto-merge with cryptographic provenance

## Components

### Core
- `pr_monitor.py` - Monitors GitHub for new PRs and publishes events
- `config.py` - Configuration management

### AI Legion
- `legion_reviewer.py` - Coordinates multiple AI agents for review
- `security_reviewer.py` - Security-focused code analysis
- `sovereignty_reviewer.py` - Sovereignty architecture alignment

### Synthesis
- `dialectical_engine.py` - Synthesizes multiple review perspectives
- `provenance.py` - Cryptographic provenance tracking

### Deployment
- GitHub Actions workflow for automation

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run PR monitor
python -m SovereignPRManager.core.pr_monitor
```

## Configuration

Set the following environment variables:
- `GITHUB_TOKEN` - GitHub API token
- `ANTHROPIC_API_KEY` - Anthropic API key (optional)
- `OPENAI_API_KEY` - OpenAI API key (optional)

## License

Part of the Strategickhaos Sovereignty Architecture project.

Built by: Domenic G. Garza (StrategicKhaos DAO LLC)
Date: December 2025
