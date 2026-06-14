# SAGCO HP Node — Claude Code Agent Configuration

## Node Identity

```
node:    sagco-node-hp
ip:      192.168.1.98
os:      Windows 11 (WSL2 for Linux workloads)
network: Ethernet, AT&T, attlocal.net
```

## Hardware

```
CPU:  AMD (3.74 GHz, multi-core)
RAM:  31.1 GB DDR5 4800 MT/s (2x DIMM, fully populated)
SSD:  932 GB NVMe (C:) — System disk, page file on SSD
GPU:  AMD Radeon 740M
        Dedicated VRAM: 512 MB
        Shared VRAM:    15.5 GB (system RAM)
        DirectX 12 (FL 12.2)
        Driver: 32.0.21034.41 (Oct 2025)
        Temp: 52°C (nominal)
        ROCm support: RDNA3 — ROCm 6.x on WSL2
USB:  Disk 1(E:), Disk 2(D:), Disk 3(F:) — external drives
```

## Runtime Stack (observed live)

```
Ollama           → port 11434  (local LLM — sovereign)
Docker Desktop   → docker-agent, docker-mcp, docker-sandbox
WSL2 (VmmemWSL) → Linux environment for Rust/Python builds
SSH Agent        → OpenSSH for Windows (port 22)
Node.js          → multiple runtimes
Python           → active
Git for Windows  → active
```

## Agent Permissions (Dangerous Mode)

This node runs Claude Code in **full-trust developer mode**.
All tool calls are auto-approved. No permission prompts.

```json
{
  "dangerouslySkipPermissions": true
}
```

Use this only on this sovereign node. Not on external machines.

## Working Directory

The SAGCO repo lives at one of:
- `C:\Users\<you>\Sovereignty-Architecture-Elevator-Pitch-`
- Or inside WSL2: `/home/<you>/Sovereignty-Architecture-Elevator-Pitch-`

## Ollama GPU Acceleration

AMD Radeon 740M can accelerate Ollama inference:
- **Windows**: Ollama uses DirectML automatically (no config needed)
- **WSL2**: Enable ROCm 6.x (see `setup-ollama-amd.sh`)

Recommended models for 16 GB shared VRAM:
- `llama3.2:3b`    — fast, fits comfortably
- `llama3.1:8b`    — good quality, fits in shared VRAM
- `phi3.5`         — Microsoft, fast on AMD
- `deepseek-r1:7b` — reasoning, fits

## SAGCO Registry

```
sagco node hp status     — check SSH + Ollama alive
sagco node hp probe      — full hardware probe
sagco node hp ollama     — list loaded models
sagco node hp ssh        — SSH session
```

## Rules for This Node

1. Ollama is sovereign — use local models before calling external APIs
2. Docker MCP is live — can spin containers for isolation
3. WSL2 = Linux execution layer — run Rust/Python builds there
4. Never commit secrets, API keys, or real IPs to the public repo
5. This node is always-on (wired Ethernet, SSD, no thermal throttle at 52°C)
