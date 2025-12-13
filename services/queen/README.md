# Queen Orchestrator 👑

The Queen service acts as the **control plane** for the SovereignMesh Node architecture. It receives GitHub webhooks and orchestrates responses across the Sovereignty Architecture.

## Architecture

```
Sovereignty-Architecture-Elevator-Pitch-/
  services/
    queen/      👑  orchestrator (this service)
  governance/   📜  rules
  legal/        ⚖️  entities
  .github/      ⚙️  CI/CD
```

## Quick Start

### 1. Install dependencies

```bash
cd services/queen
npm install
```

### 2. Configure environment variables

```bash
export PORT=3000
export GITHUB_APP_ID=<your-app-id>
export GITHUB_WEBHOOK_SECRET="<your-webhook-secret>"
```

### 3. Start the service

```bash
npm start
# or for development with auto-reload:
npm run dev
```

You should see:
```
QUEEN: listening on port 3000
```

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info and available endpoints |
| `/health` | GET | Health check (returns `{ ok: true, ... }`) |
| `/webhooks/github` | POST | GitHub webhook receiver |

## GitHub App Configuration

Configure your GitHub App with:

- **Webhook URL**: `https://<your-domain>/webhooks/github`
- **Webhook secret**: Same as `GITHUB_WEBHOOK_SECRET`

### Required Permissions

| Permission | Access |
|------------|--------|
| Checks | Read & write |
| Actions | Read |
| Metadata | Read |

### Subscribed Events

- `push`
- `workflow_job`
- `check_run`

## Development

Run with file watching:
```bash
npm run dev
```

## SovereignMesh Integration

This service is part of **SovereignMesh Node 01** and serves as the orchestration layer for:
- Receiving GitHub webhooks
- Coordinating CI/CD responses
- Managing governance rules
- Connecting to external services (Zapier, Discord, etc.)
