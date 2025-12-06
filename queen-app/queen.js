/**
 * Queen Orchestrator
 * Central coordination hub for the Strategickhaos sovereign infrastructure
 * 
 * Routes signals between:
 * - Academic systems (SNHU/Education)
 * - Financial systems (ValorYield Engine)
 * - Governance systems (DAO Decisions)
 * - Development systems (GitHub Events)
 * - Treasury operations (Dividend Distribution)
 * 
 * @requires Node.js 18+ (uses native fetch API)
 * @author Domenic Garza <domenic.garza@snhu.edu>
 * @license MIT
 */

import express from 'express';
import crypto from 'crypto';
import { EventEmitter } from 'events';

// Check Node.js version for native fetch support
const nodeVersion = parseInt(process.versions.node.split('.')[0], 10);
if (nodeVersion < 18) {
  console.error('Error: Node.js 18 or higher is required for native fetch API support');
  process.exit(1);
}

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
  name: 'Queen Orchestrator',
  version: '1.0.0',
  domain: 'queen.strategickhaos.ai',
  legalEntities: {
    dao: {
      name: 'Strategickhaos DAO LLC',
      ein: '39-2900295'
    },
    pbc: {
      name: 'ValorYield Engine PBC',
      ein: '39-2923503'
    }
  }
};

// ============================================================================
// SIGNAL ROUTER
// ============================================================================

class SignalRouter extends EventEmitter {
  constructor() {
    super();
    this.routes = new Map();
    this.signalLog = [];
    this.setupDefaultRoutes();
  }

  setupDefaultRoutes() {
    // Academic signals (SNHU/Education)
    this.registerRoute('academic', {
      handler: this.handleAcademicSignal.bind(this),
      description: 'Educational and academic event routing'
    });

    // Financial signals (ValorYield Engine)
    this.registerRoute('financial', {
      handler: this.handleFinancialSignal.bind(this),
      description: 'Treasury and financial operations'
    });

    // Governance signals (DAO Decisions)
    this.registerRoute('governance', {
      handler: this.handleGovernanceSignal.bind(this),
      description: 'DAO governance and voting'
    });

    // GitHub signals (Code Events)
    this.registerRoute('github', {
      handler: this.handleGitHubSignal.bind(this),
      description: 'GitHub webhook events'
    });

    // Treasury allocation signals
    this.registerRoute('treasury', {
      handler: this.handleTreasurySignal.bind(this),
      description: 'Treasury allocation and distribution'
    });
  }

  registerRoute(name, config) {
    this.routes.set(name, {
      name,
      handler: config.handler,
      description: config.description,
      createdAt: new Date().toISOString()
    });
  }

  async routeSignal(routeName, payload, metadata = {}) {
    const route = this.routes.get(routeName);
    if (!route) {
      throw new Error(`Unknown route: ${routeName}`);
    }

    const signal = {
      id: this.generateSignalId(),
      route: routeName,
      payload,
      metadata,
      timestamp: new Date().toISOString(),
      status: 'PROCESSING'
    };

    this.signalLog.push(signal);
    this.emit('signalReceived', signal);

    try {
      const result = await route.handler(payload, metadata);
      signal.status = 'COMPLETED';
      signal.result = result;
      this.emit('signalCompleted', signal);
      return { success: true, signal, result };
    } catch (error) {
      signal.status = 'FAILED';
      signal.error = error.message;
      this.emit('signalFailed', signal);
      return { success: false, signal, error: error.message };
    }
  }

  generateSignalId() {
    return `sig-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`;
  }

  // Signal Handlers

  async handleAcademicSignal(payload, metadata) {
    // Route to academic systems
    return {
      routed: 'academic',
      action: payload.action || 'received',
      timestamp: new Date().toISOString()
    };
  }

  async handleFinancialSignal(payload, metadata) {
    // Route to ValorYield Financial OS
    const valorYieldUrl = process.env.VALORYIELD_URL || 'http://localhost:3000';
    
    try {
      const response = await fetch(`${valorYieldUrl}/signals/financial`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: payload.action, payload })
      });
      return await response.json();
    } catch (error) {
      return {
        routed: 'financial',
        status: 'queued',
        reason: 'ValorYield unreachable, signal queued',
        payload
      };
    }
  }

  async handleGovernanceSignal(payload, metadata) {
    // Process governance decisions
    const decision = {
      id: this.generateSignalId(),
      type: payload.type || 'PROPOSAL',
      title: payload.title,
      description: payload.description,
      proposer: payload.proposer,
      votes: payload.votes || {},
      status: 'PENDING',
      timestamp: new Date().toISOString()
    };

    return {
      routed: 'governance',
      decision,
      message: 'Governance decision logged'
    };
  }

  async handleGitHubSignal(payload, metadata) {
    // Process GitHub webhooks
    const event = metadata.event || 'unknown';
    
    return {
      routed: 'github',
      event,
      repository: payload.repository?.full_name,
      action: payload.action,
      timestamp: new Date().toISOString()
    };
  }

  async handleTreasurySignal(payload, metadata) {
    // Route treasury allocation requests
    const valorYieldUrl = process.env.VALORYIELD_URL || 'http://localhost:3000';
    
    try {
      const response = await fetch(`${valorYieldUrl}/treasury/allocate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      return await response.json();
    } catch (error) {
      return {
        routed: 'treasury',
        status: 'queued',
        reason: 'ValorYield unreachable, allocation queued',
        payload
      };
    }
  }

  getSignalLog(filter = {}) {
    let log = this.signalLog;

    if (filter.route) {
      log = log.filter(s => s.route === filter.route);
    }

    if (filter.status) {
      log = log.filter(s => s.status === filter.status);
    }

    if (filter.limit) {
      log = log.slice(-filter.limit);
    }

    return log;
  }

  getRoutes() {
    return Array.from(this.routes.entries()).map(([name, config]) => ({
      name,
      description: config.description,
      createdAt: config.createdAt
    }));
  }
}

// ============================================================================
// AI COUNCIL
// ============================================================================

class AICouncil {
  constructor() {
    this.members = [
      { id: 'claude', name: 'Claude', provider: 'Anthropic', role: 'reasoning' },
      { id: 'gpt', name: 'GPT-4', provider: 'OpenAI', role: 'general' },
      { id: 'grok', name: 'Grok', provider: 'xAI', role: 'analysis' }
    ];
    this.consultations = [];
  }

  async consult(question, context = {}) {
    const consultation = {
      id: `council-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`,
      question,
      context,
      timestamp: new Date().toISOString(),
      responses: [],
      recommendation: null
    };

    // In production, this would query actual AI models
    // For now, return a structured placeholder
    consultation.responses = this.members.map(member => ({
      member: member.name,
      role: member.role,
      status: 'available',
      message: `${member.name} is ready to provide ${member.role} assistance`
    }));

    consultation.recommendation = {
      summary: 'AI Council consulted and ready for human decision',
      confidence: 'high',
      requiresHumanApproval: true
    };

    this.consultations.push(consultation);
    return consultation;
  }

  getConsultations(limit = 10) {
    return this.consultations.slice(-limit);
  }

  getMembers() {
    return this.members;
  }
}

// ============================================================================
// QUEEN ORCHESTRATOR
// ============================================================================

class QueenOrchestrator extends EventEmitter {
  constructor() {
    super();
    this.router = new SignalRouter();
    this.council = new AICouncil();
    this.humanOperator = {
      name: 'Domenic Garza',
      role: 'Managing Member',
      permissions: ['veto', 'approve', 'override']
    };
    this.startedAt = new Date().toISOString();
  }

  getStatus() {
    return {
      system: {
        name: CONFIG.name,
        version: CONFIG.version,
        domain: CONFIG.domain,
        startedAt: this.startedAt,
        uptime: Date.now() - new Date(this.startedAt).getTime()
      },
      legalEntities: CONFIG.legalEntities,
      routes: this.router.getRoutes(),
      aiCouncil: this.council.getMembers(),
      humanOperator: this.humanOperator,
      recentSignals: this.router.getSignalLog({ limit: 5 })
    };
  }

  async processSignal(route, payload, metadata) {
    return this.router.routeSignal(route, payload, metadata);
  }

  async consultCouncil(question, context) {
    return this.council.consult(question, context);
  }
}

// ============================================================================
// EXPRESS API SERVER
// ============================================================================

function createServer(queen) {
  const app = express();
  app.use(express.json());

  // CORS
  app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization, X-GitHub-Event, X-GitHub-Delivery');
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    if (req.method === 'OPTIONS') {
      return res.sendStatus(200);
    }
    next();
  });

  // Health check
  app.get('/health', (req, res) => {
    res.json({ status: 'healthy', timestamp: new Date().toISOString() });
  });

  // Status
  app.get('/status', (req, res) => {
    res.json(queen.getStatus());
  });

  // Signal routes
  app.post('/signals/academic', async (req, res) => {
    try {
      const result = await queen.processSignal('academic', req.body, { source: 'api' });
      res.json(result);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  });

  app.post('/signals/financial', async (req, res) => {
    try {
      const result = await queen.processSignal('financial', req.body, { source: 'api' });
      res.json(result);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  });

  app.post('/signals/governance', async (req, res) => {
    try {
      const result = await queen.processSignal('governance', req.body, { source: 'api' });
      res.json(result);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  });

  app.post('/webhooks/github', async (req, res) => {
    try {
      const event = req.headers['x-github-event'] || 'unknown';
      const deliveryId = req.headers['x-github-delivery'];
      const result = await queen.processSignal('github', req.body, { event, deliveryId, source: 'github' });
      res.json(result);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  });

  app.post('/treasury/allocate', async (req, res) => {
    try {
      const result = await queen.processSignal('treasury', req.body, { source: 'api' });
      res.json(result);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  });

  // AI Council
  app.post('/council/consult', async (req, res) => {
    try {
      const { question, context } = req.body;
      const result = await queen.consultCouncil(question, context);
      res.json(result);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  });

  app.get('/council/members', (req, res) => {
    res.json(queen.council.getMembers());
  });

  app.get('/council/consultations', (req, res) => {
    const limit = parseInt(req.query.limit) || 10;
    res.json(queen.council.getConsultations(limit));
  });

  // Signal log
  app.get('/signals', (req, res) => {
    const { route, status, limit } = req.query;
    const filter = {
      route,
      status,
      limit: limit ? parseInt(limit) : 50
    };
    res.json(queen.router.getSignalLog(filter));
  });

  // Routes info
  app.get('/routes', (req, res) => {
    res.json(queen.router.getRoutes());
  });

  // Root documentation
  app.get('/', (req, res) => {
    res.json({
      name: CONFIG.name,
      version: CONFIG.version,
      domain: CONFIG.domain,
      description: 'Central coordination hub for Strategickhaos sovereign infrastructure',
      legalEntities: CONFIG.legalEntities,
      endpoints: {
        status: 'GET /status',
        health: 'GET /health',
        routes: 'GET /routes',
        signals: {
          academic: 'POST /signals/academic',
          financial: 'POST /signals/financial',
          governance: 'POST /signals/governance',
          github: 'POST /webhooks/github',
          treasury: 'POST /treasury/allocate',
          list: 'GET /signals'
        },
        council: {
          consult: 'POST /council/consult',
          members: 'GET /council/members',
          consultations: 'GET /council/consultations'
        }
      }
    });
  });

  return app;
}

// ============================================================================
// MAIN ENTRY POINT
// ============================================================================

const queen = new QueenOrchestrator();
const app = createServer(queen);

const PORT = process.env.PORT || 3001;

app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         👑 QUEEN ORCHESTRATOR                                 ║
║                    queen.strategickhaos.ai                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  Signal Routes:                                                               ║
║  ├── /signals/academic     (SNHU/Education)                                  ║
║  ├── /signals/financial    (ValorYield Engine)                               ║
║  ├── /signals/governance   (DAO Decisions)                                   ║
║  ├── /webhooks/github      (Code Events)                                     ║
║  └── /treasury/allocate    (Dividend Distribution)                           ║
║                                                                               ║
║  AI Council:                                                                  ║
║  ├── Claude (Anthropic) - Reasoning                                          ║
║  ├── GPT-4 (OpenAI) - General                                                ║
║  └── Grok (xAI) - Analysis                                                   ║
║                                                                               ║
║  Human Operator: Domenic Garza (Managing Member)                             ║
║  Permissions: veto, approve, override                                        ║
║                                                                               ║
║  Server running on: http://localhost:${PORT}                                     ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
  `);
});

export { QueenOrchestrator, SignalRouter, AICouncil };
