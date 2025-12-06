/**
 * 👑 Queen - StrategicKhaos Swarm Intelligence Control Plane
 * 
 * Main entry point for the Queen service deployed to GKE.
 * Handles GitHub webhooks, OAuth callbacks, academic signals, and health checks.
 * 
 * Endpoints:
 *   GET  /              - Landing page
 *   GET  /health        - Health check
 *   POST /signals/academic - Receive academic signals from Zapier
 *   POST /webhooks/github  - Receive GitHub App webhooks
 *   GET  /oauth/callback   - Handle GitHub OAuth callbacks
 * 
 * Environment Variables:
 *   PORT                      - Server port (default: 3000)
 *   GITHUB_APP_ID             - GitHub App ID
 *   GITHUB_APP_INSTALLATION_ID - GitHub App Installation ID
 *   GITHUB_WEBHOOK_SECRET     - Secret for validating GitHub webhooks
 *   GITHUB_APP_PRIVATE_KEY    - Private key for GitHub App authentication
 *   QUEEN_DOMAIN              - Domain name (queen.strategickhaos.ai)
 *   DISCORD_BOT_TOKEN         - Discord bot token for notifications
 */

const http = require('http');
const crypto = require('crypto');

// Configuration from environment
const PORT = process.env.PORT || 3000;
const GITHUB_WEBHOOK_SECRET = process.env.GITHUB_WEBHOOK_SECRET;
const GITHUB_APP_ID = process.env.GITHUB_APP_ID;
const GITHUB_APP_INSTALLATION_ID = process.env.GITHUB_APP_INSTALLATION_ID;
const QUEEN_DOMAIN = process.env.QUEEN_DOMAIN || 'queen.strategickhaos.ai';
const LOG_LEVEL = process.env.LOG_LEVEL || 'info';

// Simple logger
const log = {
  info: (...args) => console.log(`[INFO] ${new Date().toISOString()}`, ...args),
  warn: (...args) => console.warn(`[WARN] ${new Date().toISOString()}`, ...args),
  error: (...args) => console.error(`[ERROR] ${new Date().toISOString()}`, ...args),
  debug: (...args) => LOG_LEVEL === 'debug' && console.log(`[DEBUG] ${new Date().toISOString()}`, ...args)
};

/**
 * Main request handler
 */
async function handleRequest(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const path = url.pathname;
  const method = req.method;

  log.debug(`${method} ${path}`);

  try {
    // Health check endpoint
    if (path === '/health' && method === 'GET') {
      return sendJSON(res, 200, {
        status: 'healthy',
        service: 'queen',
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        github: {
          appId: GITHUB_APP_ID,
          installationId: GITHUB_APP_INSTALLATION_ID
        }
      });
    }

    // Academic signals endpoint (for Zapier)
    if (path === '/signals/academic' && method === 'POST') {
      return handleAcademicSignal(req, res);
    }

    // GitHub webhooks endpoint
    if (path === '/webhooks/github' && method === 'POST') {
      return handleGitHubWebhook(req, res);
    }

    // OAuth callback endpoint
    if (path === '/oauth/callback' && method === 'GET') {
      return handleOAuthCallback(req, res, url);
    }

    // Root/landing page
    if (path === '/' && method === 'GET') {
      return sendLandingPage(res);
    }

    // Metrics endpoint (for Prometheus)
    if (path === '/metrics' && method === 'GET') {
      return sendMetrics(res);
    }

    // 404 for all other paths
    return sendJSON(res, 404, { error: 'Not found', path: path });
  } catch (err) {
    log.error('Unhandled error:', err);
    return sendJSON(res, 500, { error: 'Internal server error' });
  }
}

/**
 * Handle academic signals from Zapier
 */
async function handleAcademicSignal(req, res) {
  try {
    const body = await getRequestBody(req);
    const signal = JSON.parse(body);
    log.info('Academic signal received:', JSON.stringify(signal));
    
    // TODO: Process signal (forward to Discord, trigger workflows, etc.)
    
    return sendJSON(res, 200, {
      received: true,
      signal_type: 'academic',
      processed_at: new Date().toISOString()
    });
  } catch (err) {
    log.error('Signal processing failed:', err.message);
    return sendJSON(res, 400, { error: 'Invalid signal payload' });
  }
}

/**
 * Handle GitHub webhooks
 */
async function handleGitHubWebhook(req, res) {
  try {
    const body = await getRequestBody(req);
    const signature = req.headers['x-hub-signature-256'];
    
    // Verify webhook signature
    if (GITHUB_WEBHOOK_SECRET && signature) {
      const hmac = crypto.createHmac('sha256', GITHUB_WEBHOOK_SECRET);
      hmac.update(body);
      const expectedSig = `sha256=${hmac.digest('hex')}`;
      
      if (!crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSig))) {
        log.warn('Invalid webhook signature');
        return sendJSON(res, 401, { error: 'Invalid signature' });
      }
    }

    const event = req.headers['x-github-event'];
    const payload = JSON.parse(body);
    log.info(`GitHub event: ${event}`);
    
    // Process different event types
    await processGitHubEvent(event, payload);
    
    return sendJSON(res, 200, {
      received: true,
      event: event,
      processed_at: new Date().toISOString()
    });
  } catch (err) {
    log.error('Webhook processing failed:', err.message);
    return sendJSON(res, 400, { error: 'Webhook processing failed' });
  }
}

/**
 * Process GitHub events
 */
async function processGitHubEvent(event, payload) {
  switch (event) {
    case 'installation':
      log.info(`App ${payload.action} on ${payload.installation?.account?.login}`);
      break;
    case 'installation_repositories':
      log.info(`Repositories ${payload.action}: ${payload.repositories_added?.map(r => r.name).join(', ')}`);
      break;
    case 'pull_request':
      log.info(`PR ${payload.action}: #${payload.pull_request?.number} - ${payload.pull_request?.title}`);
      break;
    case 'push':
      log.info(`Push to ${payload.ref} by ${payload.pusher?.name}`);
      break;
    case 'issues':
      log.info(`Issue ${payload.action}: #${payload.issue?.number} - ${payload.issue?.title}`);
      break;
    case 'issue_comment':
      log.info(`Comment on #${payload.issue?.number} by ${payload.comment?.user?.login}`);
      break;
    case 'check_suite':
      log.info(`Check suite ${payload.action}: ${payload.check_suite?.conclusion}`);
      break;
    case 'check_run':
      log.info(`Check run ${payload.action}: ${payload.check_run?.name} - ${payload.check_run?.conclusion}`);
      break;
    case 'workflow_run':
      log.info(`Workflow ${payload.action}: ${payload.workflow_run?.name} - ${payload.workflow_run?.conclusion}`);
      break;
    default:
      log.info(`Event ${event} received`);
  }
}

/**
 * Handle OAuth callback
 */
function handleOAuthCallback(req, res, url) {
  const code = url.searchParams.get('code');
  const state = url.searchParams.get('state');
  const error = url.searchParams.get('error');
  
  if (error) {
    log.warn('OAuth error:', error);
    return sendHTML(res, 400, `
      <html>
        <body style="font-family: sans-serif; text-align: center; padding: 40px;">
          <h1>❌ Authorization Failed</h1>
          <p>Error: ${escapeHtml(error)}</p>
        </body>
      </html>
    `);
  }
  
  if (!code) {
    return sendHTML(res, 400, `
      <html>
        <body style="font-family: sans-serif; text-align: center; padding: 40px;">
          <h1>❌ OAuth Error</h1>
          <p>No authorization code received.</p>
        </body>
      </html>
    `);
  }
  
  log.info(`OAuth callback received - code: ${code.substring(0, 10)}...`);
  
  // TODO: Exchange code for access token using GITHUB_CLIENT_SECRET
  
  return sendHTML(res, 200, `
    <html>
      <body style="font-family: sans-serif; text-align: center; padding: 40px;">
        <h1>✅ Authorization Complete</h1>
        <p>Queen has been authorized. You can close this window.</p>
        <p style="color: #666; font-size: 12px;">
          GitHub App ID: ${GITHUB_APP_ID}<br>
          Domain: ${QUEEN_DOMAIN}
        </p>
      </body>
    </html>
  `);
}

/**
 * Send landing page
 */
function sendLandingPage(res) {
  return sendHTML(res, 200, `
    <!DOCTYPE html>
    <html>
      <head>
        <title>Queen | StrategicKhaos</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
          * { box-sizing: border-box; }
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
          }
          .container {
            text-align: center;
            padding: 40px;
            max-width: 600px;
          }
          h1 { font-size: 3em; margin-bottom: 10px; }
          .crown { font-size: 4em; animation: pulse 2s infinite; }
          @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
          }
          .status { 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 10px;
            margin-top: 30px;
          }
          .endpoint { 
            font-family: monospace; 
            background: rgba(0,0,0,0.3); 
            padding: 8px 16px;
            border-radius: 4px;
            margin: 5px 0;
            display: inline-block;
          }
          .healthy { color: #4ade80; }
          a { color: #60a5fa; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="crown">👑</div>
          <h1>Queen</h1>
          <p>StrategicKhaos Swarm Intelligence Control Plane</p>
          <div class="status">
            <p class="healthy">● Status: Online</p>
            <h3>Active Endpoints</h3>
            <div class="endpoint">GET /health</div><br>
            <div class="endpoint">POST /signals/academic</div><br>
            <div class="endpoint">POST /webhooks/github</div><br>
            <div class="endpoint">GET /oauth/callback</div>
          </div>
          <p style="margin-top: 30px; color: #888; font-size: 14px;">
            GitHub App: ${GITHUB_APP_ID || 'Not configured'} | 
            Installation: ${GITHUB_APP_INSTALLATION_ID || 'Not configured'}
          </p>
          <p style="color: #666; font-size: 12px;">
            <a href="https://github.com/strategickhaos-swarm-intelligence">GitHub</a> |
            <a href="/health">Health Check</a>
          </p>
        </div>
      </body>
    </html>
  `);
}

/**
 * Send Prometheus metrics
 */
function sendMetrics(res) {
  const metrics = [
    '# HELP queen_up Whether Queen is running',
    '# TYPE queen_up gauge',
    'queen_up 1',
    '',
    '# HELP queen_info Queen service information',
    '# TYPE queen_info gauge',
    `queen_info{version="1.0.0",github_app_id="${GITHUB_APP_ID}"} 1`
  ].join('\n');
  
  res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });
  res.end(metrics);
}

// Helper: Get request body
function getRequestBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => body += chunk.toString());
    req.on('end', () => resolve(body));
    req.on('error', reject);
  });
}

// Helper: Send JSON response
function sendJSON(res, status, data) {
  res.writeHead(status, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}

// Helper: Send HTML response
function sendHTML(res, status, html) {
  res.writeHead(status, { 'Content-Type': 'text/html' });
  res.end(html);
}

// Helper: Escape HTML to prevent XSS
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Create and start server
const server = http.createServer((req, res) => {
  handleRequest(req, res).catch(err => {
    log.error('Unhandled error:', err);
    // Only send error response if headers haven't been sent yet
    if (!res.headersSent) {
      sendJSON(res, 500, { error: 'Internal server error' });
    }
  });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  log.info('SIGTERM received, shutting down...');
  server.close(() => {
    log.info('Server closed');
    process.exit(0);
  });
});

// Start server
server.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════════════════════════════╗
║                        👑 QUEEN ONLINE 👑                        ║
╠══════════════════════════════════════════════════════════════════╣
║  Port:         ${String(PORT).padEnd(48)}║
║  Domain:       ${(QUEEN_DOMAIN || 'localhost').padEnd(48)}║
║  GitHub App:   ${(GITHUB_APP_ID || 'Not configured').padEnd(48)}║
║  Installation: ${(GITHUB_APP_INSTALLATION_ID || 'Not configured').padEnd(48)}║
╚══════════════════════════════════════════════════════════════════╝
  `);
});

module.exports = { handleRequest, processGitHubEvent };
