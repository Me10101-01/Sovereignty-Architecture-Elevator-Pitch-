# /sagco — SAGCO Command Interface

**SAGCO** (Sovereignty Architecture Graph Command Orchestrator) is the nerve-system
command layer of Strategickhaos DAO LLC.

This custom command gives you a Claude Code interface to the full SAGCO pipeline:
lexer → parser → VM → stepper crawler → DNA cell engine → Raspberry Pi deploy.

---

## Usage

```
/sagco <verb> [target] [flags]
```

Or compose pipelines:

```
/sagco crawl ./src --depth=3 | ingest README.md --convert=dna
```

---

## Verb Reference

| Verb       | Description                                          |
|------------|------------------------------------------------------|
| `boot`     | Initialize VM registers (binds all tool nodes)       |
| `crawl`    | Walk a directory tree, emit FolderTokens             |
| `ingest`   | Read a file, emit raw token on the bus               |
| `dna`      | Ingest a README and convert it to a DNA Cell         |
| `pipeline` | Run full stepper crawler on a folder                 |
| `emit`     | Manually push a signal token onto the bus            |
| `link`     | Connect two graph nodes                              |
| `spawn`    | Create a child agent process                         |
| `halt`     | Stop an agent by PID                                 |
| `deploy`   | Emit a deploy token (RPI / local / cloud)            |
| `vm`       | VM introspection: `status` \| `pids` \| `bus`         |
| `audit`    | List all files under a path, emit audit token        |
| `sync`     | Queue a sync job                                     |
| `convert`  | Convert a file to another format                     |
| `status`   | Alias for `vm status`                                |

---

## Flags

| Flag              | Type    | Description                              |
|-------------------|---------|------------------------------------------|
| `--depth=N`       | int     | Crawler max depth (default 3)            |
| `--emit=FORMAT`   | string  | Output format: `tokens` \| `json`         |
| `--convert=FORMAT`| string  | Convert target: `dna` \| `raw` \| `yaml`  |
| `--target=NAME`   | string  | Deploy target: `rpi` \| `local` \| `gke`  |
| `--host=ADDR`     | string  | Remote host address                      |
| `--branch=NAME`   | string  | Git branch to deploy                     |
| `--pid=ID`        | string  | Process ID for halt/query                |
| `--json`          | bool    | Output raw JSON                          |

---

## Examples

```bash
# Boot the VM and initialize all tool node registers
/sagco boot default

# Walk the entire workspace 3 levels deep, emit tokens
/sagco crawl . --depth=3 --emit=tokens

# Ingest a README and produce a DNA Cell
/sagco dna sagco/README.md

# Run full folder crawler (creates pipeline graph)
/sagco pipeline ./sagco

# Compose: crawl then convert to DNA
/sagco crawl ./sagco --depth=2 | sagco ingest README.md --convert=dna

# Deploy to Raspberry Pi
/sagco deploy --target=rpi --host=raspberrypi.local --branch=main

# Check VM process table
/sagco vm pids

# Check bus (last 10 tokens)
/sagco vm bus

# Full audit
/sagco audit .
```

---

## DNA Cell Model

When `--convert=dna` is used, SAGCO ingests any README into a **DNA Cell**:

```
Organelle       ←→  System mapping
─────────────────────────────────────
Nucleus         ←→  Identity (name, version, purpose)
Membrane        ←→  Interfaces (APIs, ports, commands)
Mitochondria    ←→  Executors (scripts, workflows, builds)
Ribosomes       ←→  Token generators (env vars, configs)
Cytoplasm       ←→  Raw content blob
DNA Strand      ←→  Base64 SHA-256 hash chain (links generations)
```

Each cell has a `cell_id`, `generation`, `parent_id`, and `dna_strand`
forming a linked chain across all ingested documents.

---

## Raspberry Pi Autodeploy

The `rpi_autodeploy.sh` agent runs on the Pi as a systemd service.
It polls for new commits on the configured branch, pulls, re-crawls,
and emits a deploy token through the SAGCO VM.

To install on the Pi:
```bash
# Copy the script
scp sagco/rpi_autodeploy.sh pi@raspberrypi.local:~/

# Create env file
cat > ~/.sagco.env <<EOF
SAGCO_REPO_URL=https://github.com/me10101-01/sovereignty-architecture-elevator-pitch-
SAGCO_REPO_DIR=/home/pi/sagco-workspace
SAGCO_BRANCH=main
SAGCO_POLL_INTERVAL=60
EOF

# Install systemd service (see embedded unit in rpi_autodeploy.sh)
sudo nano /etc/systemd/system/sagco-rpi.service
sudo systemctl enable sagco-rpi
sudo systemctl start sagco-rpi
```

---

## Architecture

```
/sagco <input>
    │
    ▼
sagco/lexer.py          ← headless tokenizer (no TTY required)
    │ Token stream
    ▼
sagco/parser.py         ← AST: ScriptNode → PipelineNode → CommandNode
    │ AST
    ▼
sagco/vm.py             ← VM: executes instructions, manages PID table + bus
    │         │
    │         └─→ sagco/dna_cell.py   ← README → DNA Cell
    │
    └─→ sagco/crawler.py ← Stepper crawler, FolderToken pipeline graph
              │
              └─→ sagco/rpi_autodeploy.sh ← Pi agent
                         │
                         └─→ .github/workflows/sagco-rpi-deploy.yml
```

---

*SAGCO — "A place where the tools can find each other."*

$ARGUMENTS
