# Services Directory

This directory contains the microservices that make up the SovereignMesh Node architecture.

## Architecture Overview

```
services/
├── queen/              # 👑 Orchestrator - The central router
├── swarmgate/          # 💰 Financial operations (future)
├── knowledge-node/     # 🧠 Obsidian sync (future)
└── sentinel/           # 🛡️ Security monitoring (future)
```

## Current Services

### 👑 Queen Orchestrator (`services/queen/`)

The Queen is the central control plane for the SovereignMesh Node. It provides:

- **Service Registry**: Track and manage all microservices
- **Request Routing**: Route requests to appropriate services
- **Health Monitoring**: Check service health status
- **Node Information**: Metadata about the current node

#### Quick Start

```bash
cd services/queen
npm install
npm start
```

#### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/services` | GET | List registered services |
| `/services/register` | POST | Register a new service |
| `/services/:name` | DELETE | Deregister a service |
| `/route/:service/*` | ALL | Route requests to a service |
| `/node` | GET | Node information |

## Future Services

### 💰 SwarmGate (`services/swarmgate/`)
Financial operations and payment processing.

### 🧠 Knowledge Node (`services/knowledge-node/`)
Obsidian sync and knowledge management.

### 🛡️ Sentinel (`services/sentinel/`)
Security monitoring and threat detection.

## SovereignMesh Philosophy

Each Codespace = One SovereignMesh Node  
Each `services/` folder = One Microservice  
Queen = The Router that coordinates all services

**Thesis:** Scattered tools  
**Antithesis:** Need unified control  
**Synthesis:** SovereignMesh — Codespaces as sovereign compute nodes with Queen as orchestrator
