# SAGCO — Sovereignty Architecture Graph Command Orchestrator

> "A place where the tools can find each other."
> — Fellowship Review Board, Node 137

## Overview

SAGCO is the operating nervous system of the Strategickhaos DAO.
It is not an application. It is infrastructure.

It provides a headless lexer/parser, a register-based virtual machine,
an autonomous stepper crawler, and a DNA cell engine that converts any
README into a self-describing, hash-chained knowledge atom.

**Evolution path observed by the Fellowship:**
```
Tool Collector → Workflow Builder → System Mapper → Agent Architect
```

## Architecture

```
sagco/
├── lexer.py        Headless tokenizer — no TTY required
├── parser.py       AST builder: Script → Pipeline → Command nodes
├── vm.py           Virtual machine: PID table, register file, token bus
├── crawler.py      Stepper crawler: folder → FolderToken → pipeline graph
├── dna_cell.py     README → DNA Cell (nucleus/membrane/mitochondria/...)
└── rpi_autodeploy.sh  Raspberry Pi autonomous deploy agent
```

## Usage

### Command line

```bash
# Lex a SAGCO command string
python -m sagco.lexer "sagco crawl ./src --depth=3 --emit=tokens"

# Parse into AST
python -m sagco.parser "sagco crawl ./src | sagco dna README.md"

# Run through the VM
python -m sagco.vm "sagco boot default | sagco crawl . --depth=2"

# Run the stepper crawler
python -m sagco.crawler . 3

# Convert README to DNA cell
python -m sagco.dna_cell README.md
```

### Claude Code custom command

```bash
/sagco boot default
/sagco crawl . --depth=3 --emit=tokens
/sagco dna sagco/README.md
/sagco pipeline ./sagco
/sagco deploy --target=rpi --branch=main
/sagco vm status
```

### Python API

```python
from sagco import VM, crawl_to_pipeline, ingest_to_dna

vm = VM(".")
procs = vm.execute("sagco boot default | sagco crawl ./sagco --depth=3")

result = crawl_to_pipeline(".", max_depth=4, output_path="pipeline.json")

cell = ingest_to_dna("README.md", open("README.md").read(), "README.md")
print(cell["dna_strand"])
```

## DNA Cell Model

Every ingested document becomes a DNA Cell — an atomic unit of SAGCO's
knowledge fabric with a biological organelle structure:

| Organelle    | System Role                                |
|--------------|--------------------------------------------|
| Nucleus      | Identity: name, version, purpose           |
| Membrane     | Interfaces: APIs, ports, entry points      |
| Mitochondria | Executors: scripts, workflows, commands    |
| Ribosomes    | Token generators: env vars, config keys    |
| Cytoplasm    | Raw content blob                           |
| DNA Strand   | Base64 SHA-256 hash chain (links cells)    |

Cells chain together through `parent_id` and `generation` fields,
forming a knowledge lineage across the entire workspace.

## VM Instruction Set

```
BOOT    profile                  Bind tool nodes to registers
CRAWL   path --depth=N          Walk tree, emit FolderTokens
INGEST  file --convert=FORMAT   Read file, push to bus
DNA     file                    Ingest file as DNA cell
EMIT    target                  Push signal token
LINK    node_a,node_b           Connect graph nodes
SPAWN   agent --config=...      Start child agent process
HALT    pid                     Stop agent
DEPLOY  --target=rpi            Emit deploy token
VM      status|pids|bus         Introspect VM state
AUDIT   path                    List files, emit audit token
```

## Raspberry Pi Autodeploy

```bash
SAGCO_REPO_URL=https://github.com/me10101-01/sovereignty-architecture-elevator-pitch-
SAGCO_REPO_DIR=/home/pi/sagco-workspace
SAGCO_BRANCH=main
SAGCO_POLL_INTERVAL=60
```

The Pi agent (`rpi_autodeploy.sh`) polls for new commits, pulls,
re-crawls the workspace, and emits a deploy token through the VM.
A GitHub Actions workflow (`sagco-rpi-deploy.yml`) handles the CI side.

## Environment Variables

```bash
SAGCO_BRANCH         Git branch to track
SAGCO_REPO_DIR       Local workspace path
SAGCO_REPO_URL       Remote git URL
SAGCO_POLL_INTERVAL  Seconds between deploy checks
SAGCO_PYTHON         Python interpreter path
SAGCO_LOG            Log file path
```

## Installation

```bash
# Clone the workspace
git clone https://github.com/me10101-01/sovereignty-architecture-elevator-pitch-
cd sovereignty-architecture-elevator-pitch-

# Install (no external dependencies — stdlib only)
pip install -e .

# Self-test
python -c "from sagco import VM; vm = VM(); vm.execute('sagco boot default'); print(vm.pid_table_dump())"
```

## Tool Node Register File

The VM maintains 15 named registers — one per tool node:

```
powershell   remote_desktop   git      claude   codex
obsidian     termux           docker   kubernetes  redis
rpi          midi             scanner  compiler    memory
```

Each register binds a tool → agent assignment. The PID table tracks
all active, queued, done, and halted processes. The token bus carries
SAGCOTokens between pipeline stages.

## License

Strategickhaos DAO LLC — Wyoming DAO (W.S. 17-31-101)
Domenic Gabriel Garza, Sole Member
