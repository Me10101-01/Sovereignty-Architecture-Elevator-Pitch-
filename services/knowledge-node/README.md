# 🧠 Knowledge Node

**Status:** Planned

Obsidian sync and knowledge management service for the SovereignMesh architecture.

## Planned Features

- Obsidian vault synchronization
- Knowledge graph management
- Note indexing and search
- Cross-vault linking

## Integration with Queen

Knowledge Node will register with Queen orchestrator to be routed via:
```
POST /services/register
{
  "name": "knowledge-node",
  "url": "http://localhost:3102",
  "type": "knowledge"
}
```
