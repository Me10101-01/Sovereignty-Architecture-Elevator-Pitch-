/**
 * Queen Orchestrator - SovereignMesh Node 01
 * 
 * The Queen acts as the control plane for the Sovereignty Architecture.
 * It receives GitHub webhooks and orchestrates responses.
 */

import express from 'express';
import { Webhooks } from '@octokit/webhooks';
import rateLimit from 'express-rate-limit';

const PORT = process.env.PORT || 3000;
const GITHUB_APP_ID = process.env.GITHUB_APP_ID;
const GITHUB_WEBHOOK_SECRET = process.env.GITHUB_WEBHOOK_SECRET || '';

const app = express();

// Parse raw body for webhook signature verification with size limit
app.use(express.json({
  limit: '1mb', // Limit payload size to prevent memory exhaustion
  verify: (req, _res, buf) => {
    req.rawBody = buf.toString();
  }
}));

// Rate limiting for webhook endpoint
const webhookLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute window
  max: 100, // Max 100 requests per minute per IP
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many requests, please try again later' }
});

// Health endpoint for monitoring and verification
app.get('/health', (_req, res) => {
  res.json({
    ok: true,
    service: 'queen',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    appId: GITHUB_APP_ID || 'not configured'
  });
});

// Root endpoint
app.get('/', (_req, res) => {
  res.json({
    service: 'Queen Orchestrator',
    description: 'SovereignMesh Node control plane',
    endpoints: {
      health: '/health',
      webhooks: '/webhooks/github'
    }
  });
});

// Initialize GitHub webhooks handler
const webhooks = new Webhooks({
  secret: GITHUB_WEBHOOK_SECRET
});

// Handle push events
webhooks.on('push', ({ id, payload }) => {
  console.log(`QUEEN: push event received [${id}]`);
  console.log(`  Repository: ${payload.repository?.full_name}`);
  console.log(`  Ref: ${payload.ref}`);
  console.log(`  Commits: ${payload.commits?.length || 0}`);
});

// Handle workflow_job events
webhooks.on('workflow_job', ({ id, payload }) => {
  console.log(`QUEEN: workflow_job event received [${id}]`);
  console.log(`  Repository: ${payload.repository?.full_name}`);
  console.log(`  Action: ${payload.action}`);
  console.log(`  Job: ${payload.workflow_job?.name}`);
});

// Handle check_run events
webhooks.on('check_run', ({ id, payload }) => {
  console.log(`QUEEN: check_run event received [${id}]`);
  console.log(`  Repository: ${payload.repository?.full_name}`);
  console.log(`  Action: ${payload.action}`);
  console.log(`  Check: ${payload.check_run?.name}`);
});

// Generic error handler for webhooks
webhooks.onError((error) => {
  console.error('QUEEN: Webhook error:', error.message);
});

// GitHub webhook endpoint with rate limiting
app.post('/webhooks/github', webhookLimiter, async (req, res) => {
  try {
    const signature = req.headers['x-hub-signature-256'];
    const event = req.headers['x-github-event'];
    const id = req.headers['x-github-delivery'];

    // Validate required headers
    if (!signature || !event || !id) {
      return res.status(400).json({ error: 'Missing required webhook headers' });
    }

    console.log(`QUEEN: Received webhook - event: ${event}, id: ${id}`);

    await webhooks.verifyAndReceive({
      id: String(id),
      name: String(event),
      signature: String(signature),
      payload: req.rawBody || JSON.stringify(req.body)
    });

    res.status(200).json({ received: true });
  } catch (error) {
    console.error('QUEEN: Webhook processing error:', error.message);
    res.status(400).json({ error: 'Webhook processing failed' });
  }
});

// Start server
app.listen(PORT, () => {
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('👑 QUEEN: Orchestrator Active');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`QUEEN: listening on port ${PORT}`);
  console.log(`QUEEN: GitHub App ID: ${GITHUB_APP_ID || 'not configured'}`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
});
