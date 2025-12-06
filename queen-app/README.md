# Queen - Sovereign Orchestrator

The Queen is the central coordination node in the SovereignMesh ecosystem. It acts as the sovereign orchestrator that receives and routes signals from various sources:

- **Academic signals** - From Outlook/Zapier outer-ring (SNHU emails, etc.)
- **Financial signals** - From Thread Bank and treasury systems
- **Security signals** - From SovereignGuard and alert systems
- **GitHub webhooks** - From the Estrategi-Khaos GitHub App

## Features

- **Pure Node.js** - Uses only built-in `http` and `crypto` modules (no heavy frameworks)
- **Zero dependencies** - No external npm packages required
- **Environment-based config** - All secrets via environment variables
- **HMAC verification** - Secure GitHub webhook signature verification
- **In-memory signal queue** - Ready to be swapped for NATS later
- **Logging system** - DEBUG/INFO/WARN/ERROR levels

## Quick Start

### 1. Navigate to queen-app

```bash
cd queen-app
```

### 2. Set Environment Variables

```bash
export PORT=3000
export GITHUB_APP_ID=1884781
export GITHUB_WEBHOOK_SECRET="your-github-webhook-secret"
export ZAPIER_WEBHOOK_SECRET="outer-ring-secret"
# Optional:
export NATS_URL=""
export DISCORD_WEBHOOK_URL=""
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARN, ERROR
```

### 3. Run Queen

```bash
npm start
# or for development with auto-reload:
npm run dev
```

You should see:
```
[timestamp] [INFO] QUEEN: Queen listening on port 3000
```

## API Endpoints

### Health Check
```bash
curl http://localhost:3000/health
```
Response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### Full Status
```bash
curl http://localhost:3000/status
```
Response includes version, uptime, config snapshot, and queue sizes.

### Academic Signals (Zapier → Queen)
```bash
curl -X POST http://localhost:3000/signals/academic \
  -H "Content-Type: application/json" \
  -H "X-Queen-Secret: outer-ring-secret" \
  -d '{
    "source": "zapier-outlook",
    "type": "academic_email",
    "summary": "New email from SNHU",
    "sender": "advisor@snhu.edu",
    "subject": "Course Update",
    "timestamp": "2024-01-01T00:00:00.000Z"
  }'
```

### Financial Signals
```bash
curl -X POST http://localhost:3000/signals/financial \
  -H "Content-Type: application/json" \
  -H "X-Queen-Secret: outer-ring-secret" \
  -d '{
    "source": "thread-bank",
    "type": "transaction",
    "amount": 100.00,
    "timestamp": "2024-01-01T00:00:00.000Z"
  }'
```

### Security Signals
```bash
curl -X POST http://localhost:3000/signals/security \
  -H "Content-Type: application/json" \
  -H "X-Queen-Secret: outer-ring-secret" \
  -d '{
    "source": "sovereign-guard",
    "type": "alert",
    "severity": "high",
    "message": "Unauthorized access attempt",
    "timestamp": "2024-01-01T00:00:00.000Z"
  }'
```

### GitHub Webhooks
This endpoint is called automatically by GitHub when events occur. Configure your GitHub App with:
- **Webhook URL**: `https://your-domain/webhooks/github`
- **Webhook Secret**: Same as `GITHUB_WEBHOOK_SECRET`

## Zapier Integration

In your Zapier workflow, configure the "Webhooks by Zapier" action:

1. **URL**: `https://your-codespace-url.github.dev/signals/academic`
2. **Method**: POST
3. **Headers**:
   - `Content-Type: application/json`
   - `X-Queen-Secret: outer-ring-secret`
4. **Body**:
```json
{
  "source": "zapier-outlook",
  "type": "academic_email",
  "summary": "{{AI Summary}}",
  "sender": "{{From}}",
  "subject": "{{Subject}}",
  "timestamp": "{{Date}}"
}
```

## GitHub App Integration

Configure your Estrategi-Khaos Queen GitHub App:

1. **Webhook URL**: `https://your-codespace-url.github.dev/webhooks/github`
2. **Webhook Secret**: Set to match `GITHUB_WEBHOOK_SECRET`
3. **Permissions**:
   - Repository: Checks (Read & write), Actions (Read), Metadata (Read)
4. **Events**: push, workflow_job, check_run

## Architecture

```
Outlook (personal) -> Zapier -> Queen (/signals/academic) -> [future: Knowledge Node]

GitHub (push, checks, workflows) -> GitHub App -> Queen (/webhooks/github)

Thread Bank -> Queen (/signals/financial) -> [future: SwarmGate/Treasury]

SovereignGuard -> Queen (/signals/security) -> [future: Alert System]
```

## Future Enhancements

- **NATS integration** - Replace in-memory queue with NATS for distributed messaging
- **Knowledge Node** - Forward academic signals to Obsidian markdown storage
- **SwarmGate** - Route financial signals to treasury management
- **SovereignGuard** - Enhanced security signal processing
- **Discord notifications** - Forward important signals to Discord channels

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| PORT | No | 3000 | Server port |
| GITHUB_APP_ID | No | - | GitHub App identifier |
| GITHUB_WEBHOOK_SECRET | No | - | Secret for GitHub webhook verification |
| ZAPIER_WEBHOOK_SECRET | No | - | Secret for outer-ring verification |
| NATS_URL | No | - | NATS server URL (future) |
| DISCORD_WEBHOOK_URL | No | - | Discord webhook for notifications |
| LOG_LEVEL | No | INFO | Logging level (DEBUG, INFO, WARN, ERROR) |

## License

MIT License - Strategickhaos DAO LLC
