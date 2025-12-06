# Data Directory

This directory stores analysis outputs from swarm log analysis.

## Contents

Analysis results are stored as JSON files with naming pattern:
- `analysis_<timestamp>.json`

## Usage

Log analysis automatically saves results here:

```bash
python main.py analyze --input /path/to/logs.json
# Creates: data/analysis_<timestamp>.json
```

## Output Format

Analysis outputs include:
- `analysis_type`: Type of analysis performed
- `timestamp`: When the analysis was run
- `summary`: Key statistics and metrics
- `insights`: Extracted insights and patterns

## Cleanup

Analysis outputs can be cleaned up periodically. Keep important results in
version control or export to external systems.

---

*This file ensures the data/ directory is tracked by git.*
