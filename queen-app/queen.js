/**
 * Queen - Sovereign Orchestrator for SovereignMesh
 * 
 * A lightweight HTTP server using only Node.js built-in modules (http, crypto)
 * that serves as the central coordination point for:
 * - Academic signals (Outlook/Zapier outer-ring)
 * - Financial signals (Thread Bank, treasury)
 * - Security signals (SovereignGuard)
 * - GitHub App webhooks
 * 
 * Environment Variables:
 * - PORT: Server port (default: 3000)
 * - GITHUB_APP_ID: GitHub App identifier
 * - GITHUB_WEBHOOK_SECRET: Secret for GitHub webhook verification
 * - ZAPIER_WEBHOOK_SECRET: Secret for Zapier/outer-ring verification
 * - NATS_URL: NATS messaging URL (optional, for future)
 * - DISCORD_WEBHOOK_URL: Discord notifications (optional)
 */

const http = require('http');
const crypto = require('crypto');

// Configuration from environment variables
const config = {
  port: parseInt(process.env.PORT || '3000', 10),
  githubAppId: process.env.GITHUB_APP_ID || '',
  githubWebhookSecret: process.env.GITHUB_WEBHOOK_SECRET || '',
  zapierWebhookSecret: process.env.ZAPIER_WEBHOOK_SECRET || '',
  natsUrl: process.env.NATS_URL || '',
  discordWebhookUrl: process.env.DISCORD_WEBHOOK_URL || '',
  version: '1.0.0',
  startTime: Date.now()
};

// Logging levels
const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3
};

const currentLogLevel = LOG_LEVELS[process.env.LOG_LEVEL] || LOG_LEVELS.INFO;

function log(level, message, data = null) {
  if (LOG_LEVELS[level] >= currentLogLevel) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      ...(data && { data })
    };
    console.log(`[${timestamp}] [${level}] QUEEN: ${message}`, data ? JSON.stringify(data) : '');
  }
}

// In-memory signal queue (ready to be swapped for NATS later)
const signalQueue = {
  academic: [],
  financial: [],
  security: [],
  github: []
};

const MAX_QUEUE_SIZE = 1000;
const MAX_BODY_SIZE = 1024 * 1024; // 1MB

// Helper function to get the last signal ID from a queue
function getLastSignalId(queueType) {
  const queue = signalQueue[queueType];
  return queue.length > 0 ? queue[queue.length - 1]?.id : undefined;
}

function enqueueSignal(type, signal) {
  if (!signalQueue[type]) {
    log('WARN', `Unknown signal type: ${type}`);
    return false;
  }
  
  signal.receivedAt = new Date().toISOString();
  signal.id = crypto.randomUUID();
  
  signalQueue[type].push(signal);
  
  // Trim queue if too large (FIFO)
  if (signalQueue[type].length > MAX_QUEUE_SIZE) {
    signalQueue[type].shift();
  }
  
  log('INFO', `Signal enqueued`, { type, id: signal.id });
  return true;
}

// Verify HMAC signature for GitHub webhooks
function verifyGitHubSignature(payload, signature) {
  if (!config.githubWebhookSecret || !signature) {
    return false;
  }
  
  const expectedSignature = 'sha256=' + crypto
    .createHmac('sha256', config.githubWebhookSecret)
    .update(payload)
    .digest('hex');
  
  try {
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(expectedSignature)
    );
  } catch {
    return false;
  }
}

// Verify X-Queen-Secret header for Zapier/outer-ring
function verifyQueenSecret(providedSecret) {
  if (!config.zapierWebhookSecret) {
    log('ERROR', 'ZAPIER_WEBHOOK_SECRET not configured - rejecting request for security');
    return false;
  }
  
  return providedSecret === config.zapierWebhookSecret;
}

// Parse JSON body from request
function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
      // Limit body size
      if (body.length > MAX_BODY_SIZE) {
        reject(new Error('Request body too large'));
      }
    });
    req.on('end', () => {
      try {
        resolve({ raw: body, parsed: body ? JSON.parse(body) : {} });
      } catch (e) {
        reject(new Error('Invalid JSON'));
      }
    });
    req.on('error', reject);
  });
}

// Send JSON response
function sendJSON(res, statusCode, data) {
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}

// Route handlers
const routes = {
  // Health check endpoint
  'GET /health': async (req, res) => {
    sendJSON(res, 200, { status: 'ok', timestamp: new Date().toISOString() });
  },

  // Full status endpoint
  'GET /status': async (req, res) => {
    const uptime = Math.floor((Date.now() - config.startTime) / 1000);
    sendJSON(res, 200, {
      status: 'ok',
      version: config.version,
      uptime: `${uptime}s`,
      config: {
        port: config.port,
        githubAppId: config.githubAppId ? '***configured***' : 'not set',
        githubWebhookSecret: config.githubWebhookSecret ? '***configured***' : 'not set',
        zapierWebhookSecret: config.zapierWebhookSecret ? '***configured***' : 'not set',
        natsUrl: config.natsUrl || 'not set',
        discordWebhookUrl: config.discordWebhookUrl ? '***configured***' : 'not set'
      },
      queues: {
        academic: signalQueue.academic.length,
        financial: signalQueue.financial.length,
        security: signalQueue.security.length,
        github: signalQueue.github.length
      },
      timestamp: new Date().toISOString()
    });
  },

  // Academic signals (Outlook/Zapier outer-ring)
  'POST /signals/academic': async (req, res) => {
    const queenSecret = req.headers['x-queen-secret'];
    
    if (!verifyQueenSecret(queenSecret)) {
      log('WARN', 'Unauthorized academic signal attempt');
      return sendJSON(res, 401, { error: 'Unauthorized', message: 'Invalid X-Queen-Secret' });
    }

    try {
      const { parsed } = await parseBody(req);
      log('INFO', 'Received academic signal', { source: parsed.source, type: parsed.type });
      
      enqueueSignal('academic', parsed);
      
      sendJSON(res, 200, { 
        status: 'accepted', 
        message: 'Academic signal received',
        signalId: getLastSignalId('academic')
      });
    } catch (e) {
      log('ERROR', 'Failed to process academic signal', { error: e.message });
      sendJSON(res, 400, { error: 'Bad Request', message: e.message });
    }
  },

  // Financial signals (Thread Bank, treasury)
  'POST /signals/financial': async (req, res) => {
    const queenSecret = req.headers['x-queen-secret'];
    
    if (!verifyQueenSecret(queenSecret)) {
      log('WARN', 'Unauthorized financial signal attempt');
      return sendJSON(res, 401, { error: 'Unauthorized', message: 'Invalid X-Queen-Secret' });
    }

    try {
      const { parsed } = await parseBody(req);
      log('INFO', 'Received financial signal', { source: parsed.source, type: parsed.type });
      
      enqueueSignal('financial', parsed);
      
      sendJSON(res, 200, { 
        status: 'accepted', 
        message: 'Financial signal received',
        signalId: getLastSignalId('financial')
      });
    } catch (e) {
      log('ERROR', 'Failed to process financial signal', { error: e.message });
      sendJSON(res, 400, { error: 'Bad Request', message: e.message });
    }
  },

  // Security signals (SovereignGuard)
  'POST /signals/security': async (req, res) => {
    const queenSecret = req.headers['x-queen-secret'];
    
    if (!verifyQueenSecret(queenSecret)) {
      log('WARN', 'Unauthorized security signal attempt');
      return sendJSON(res, 401, { error: 'Unauthorized', message: 'Invalid X-Queen-Secret' });
    }

    try {
      const { parsed } = await parseBody(req);
      log('INFO', 'Received security signal', { source: parsed.source, type: parsed.type });
      
      enqueueSignal('security', parsed);
      
      sendJSON(res, 200, { 
        status: 'accepted', 
        message: 'Security signal received',
        signalId: getLastSignalId('security')
      });
    } catch (e) {
      log('ERROR', 'Failed to process security signal', { error: e.message });
      sendJSON(res, 400, { error: 'Bad Request', message: e.message });
    }
  },

  // GitHub App webhooks
  'POST /webhooks/github': async (req, res) => {
    try {
      const { raw, parsed } = await parseBody(req);
      const signature = req.headers['x-hub-signature-256'];
      const event = req.headers['x-github-event'];
      const delivery = req.headers['x-github-delivery'];

      // Verify GitHub webhook signature if secret is configured
      if (config.githubWebhookSecret && !verifyGitHubSignature(raw, signature)) {
        log('WARN', 'Invalid GitHub webhook signature', { delivery });
        return sendJSON(res, 401, { error: 'Unauthorized', message: 'Invalid signature' });
      }

      log('INFO', 'Received GitHub webhook', { event, delivery, action: parsed.action });
      
      enqueueSignal('github', {
        event,
        delivery,
        action: parsed.action,
        repository: parsed.repository?.full_name,
        sender: parsed.sender?.login,
        payload: parsed
      });

      sendJSON(res, 200, { 
        status: 'accepted', 
        message: 'GitHub webhook received',
        event,
        delivery
      });
    } catch (e) {
      log('ERROR', 'Failed to process GitHub webhook', { error: e.message });
      sendJSON(res, 400, { error: 'Bad Request', message: e.message });
    }
  }
};

// Create HTTP server
const server = http.createServer(async (req, res) => {
  const method = req.method;
  const url = new URL(req.url, `http://localhost:${config.port}`);
  const path = url.pathname;
  const routeKey = `${method} ${path}`;

  log('DEBUG', `Request: ${routeKey}`);

  // CORS headers for development
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Queen-Secret, X-Hub-Signature-256');

  // Handle preflight
  if (method === 'OPTIONS') {
    res.writeHead(204);
    return res.end();
  }

  // Route request
  const handler = routes[routeKey];
  if (handler) {
    try {
      await handler(req, res);
    } catch (e) {
      log('ERROR', 'Handler error', { route: routeKey, error: e.message });
      sendJSON(res, 500, { error: 'Internal Server Error' });
    }
  } else {
    log('WARN', `Route not found: ${routeKey}`);
    sendJSON(res, 404, { error: 'Not Found', message: `Route ${routeKey} not found` });
  }
});

// Start server
server.listen(config.port, () => {
  log('INFO', `Queen listening on port ${config.port}`);
  log('INFO', 'Available endpoints:', {
    health: 'GET /health',
    status: 'GET /status',
    academic: 'POST /signals/academic',
    financial: 'POST /signals/financial',
    security: 'POST /signals/security',
    github: 'POST /webhooks/github'
  });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  log('INFO', 'Received SIGTERM, shutting down gracefully');
  server.close(() => {
    log('INFO', 'Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  log('INFO', 'Received SIGINT, shutting down gracefully');
  server.close(() => {
    log('INFO', 'Server closed');
    process.exit(0);
  });
});

module.exports = { server, config, signalQueue };
