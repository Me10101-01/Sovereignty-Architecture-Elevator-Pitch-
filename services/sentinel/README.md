# 🛡️ Sentinel

**Status:** Planned

Security monitoring and threat detection service for the SovereignMesh architecture.

## Planned Features

- Security monitoring
- Threat detection
- Access control
- Audit logging
- Intrusion detection

## Integration with Queen

Sentinel will register with Queen orchestrator to be routed via:
```
POST /services/register
{
  "name": "sentinel",
  "url": "http://localhost:3103",
  "type": "security"
}
```
