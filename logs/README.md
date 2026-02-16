# Logs Directory

This directory stores captured traces from swarm experiments.

## Contents

Traces are stored as JSON files with naming pattern:
- `<experiment_name>_trace.json`

## Usage

Experiments automatically save traces here:

```bash
python main.py experiment --input /path/to/input.json --name my_experiment
# Creates: logs/my_experiment_trace.json
```

To analyze captured traces:

```bash
python main.py analyze --input logs/<experiment>_trace.json
```

## Cleanup

Traces can be cleaned up periodically. Keep important traces in version control
or archive to external storage.

---

*This file ensures the logs/ directory is tracked by git.*
