/**
 * ValorYield Sovereign Financial OS
 * "Banking for the People, by the Code"
 * 
 * A transparent, auditable, AI-operated financial system for the Strategickhaos DAO
 * Wyoming DAO LLC statute compliant | Public Benefit Corporation mission-locked
 * 
 * Legal Foundation:
 * - Strategickhaos DAO LLC (EIN: 39-2900295) - Wyoming DAO Statute (Autonomous Operations)
 * - ValorYield Engine PBC (EIN: 39-2923503) - Public Benefit Corporation (Mission-Locked)
 * 
 * @author Domenic Garza <domenic.garza@snhu.edu>
 * @license MIT
 */

import express from 'express';
import crypto from 'crypto';
import { EventEmitter } from 'events';

// ============================================================================
// LEGAL ENTITY CONFIGURATION
// ============================================================================

const LEGAL_ENTITIES = {
  dao: {
    name: 'Strategickhaos DAO LLC',
    ein: '39-2900295',
    jurisdiction: 'Wyoming',
    statute: 'Wyoming DAO Statute',
    type: 'Decentralized Autonomous Organization',
    role: 'Autonomous Operations'
  },
  pbc: {
    name: 'ValorYield Engine PBC',
    ein: '39-2923503',
    jurisdiction: 'Wyoming',
    type: 'Public Benefit Corporation',
    role: 'Mission-Locked Financial Operations'
  }
};

// ============================================================================
// SOVEREIGNGUARD RULES - Financial Safety Configuration
// ============================================================================

const SOVEREIGN_GUARD_RULES = {
  maxAllocationPercent: 7,       // Maximum 7% of treasury per distribution
  reserveRequirementPercent: 20, // Always maintain 20% reserve
  minApprovalDelay: 24 * 60 * 60 * 1000, // 24 hours minimum for large transactions
  largeTransactionThreshold: 1000, // Transactions above this require delay
  maxDailyDistributions: 10,     // Maximum distributions per day
  auditRetentionDays: 365 * 7    // 7 years audit retention
};

// ============================================================================
// TREASURY MANAGEMENT
// ============================================================================

class Treasury extends EventEmitter {
  constructor() {
    super();
    this.balance = 0;
    this.transactions = [];
    this.createdAt = new Date().toISOString();
    this.id = this.generateId();
  }

  generateId() {
    return `treasury-${crypto.randomBytes(8).toString('hex')}`;
  }

  deposit(amount, source, metadata = {}) {
    if (amount <= 0) {
      throw new Error('Deposit amount must be positive');
    }

    const transaction = {
      id: this.generateTransactionId(),
      type: 'DEPOSIT',
      amount,
      source,
      timestamp: new Date().toISOString(),
      previousBalance: this.balance,
      newBalance: this.balance + amount,
      metadata,
      hash: null
    };

    transaction.hash = this.hashTransaction(transaction);
    this.balance += amount;
    this.transactions.push(transaction);
    
    this.emit('deposit', transaction);
    return transaction;
  }

  withdraw(amount, destination, approver, metadata = {}) {
    if (amount <= 0) {
      throw new Error('Withdrawal amount must be positive');
    }

    if (amount > this.balance) {
      throw new Error('Insufficient funds');
    }

    // Check reserve requirement
    const reserveRequired = (this.balance - amount) >= 
      (this.balance * SOVEREIGN_GUARD_RULES.reserveRequirementPercent / 100);
    
    if (!reserveRequired) {
      throw new Error(`Withdrawal would breach ${SOVEREIGN_GUARD_RULES.reserveRequirementPercent}% reserve requirement`);
    }

    const transaction = {
      id: this.generateTransactionId(),
      type: 'WITHDRAWAL',
      amount,
      destination,
      approver,
      timestamp: new Date().toISOString(),
      previousBalance: this.balance,
      newBalance: this.balance - amount,
      metadata,
      hash: null
    };

    transaction.hash = this.hashTransaction(transaction);
    this.balance -= amount;
    this.transactions.push(transaction);
    
    this.emit('withdrawal', transaction);
    return transaction;
  }

  getBalance() {
    return {
      total: this.balance,
      available: this.balance * (1 - SOVEREIGN_GUARD_RULES.reserveRequirementPercent / 100),
      reserved: this.balance * SOVEREIGN_GUARD_RULES.reserveRequirementPercent / 100,
      maxSingleAllocation: this.balance * SOVEREIGN_GUARD_RULES.maxAllocationPercent / 100
    };
  }

  generateTransactionId() {
    return `txn-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`;
  }

  hashTransaction(transaction) {
    const data = JSON.stringify({
      ...transaction,
      hash: undefined
    });
    return crypto.createHash('sha256').update(data).digest('hex');
  }

  getAuditTrail(startDate = null, endDate = null) {
    let filtered = this.transactions;
    
    if (startDate) {
      filtered = filtered.filter(t => new Date(t.timestamp) >= new Date(startDate));
    }
    
    if (endDate) {
      filtered = filtered.filter(t => new Date(t.timestamp) <= new Date(endDate));
    }
    
    return filtered.map(t => ({
      ...t,
      verified: this.hashTransaction({ ...t, hash: undefined }) === t.hash
    }));
  }
}

// ============================================================================
// BENEFICIARY REGISTRY
// ============================================================================

class BeneficiaryRegistry {
  constructor() {
    this.beneficiaries = new Map();
    this.distributions = [];
  }

  register(id, data) {
    const beneficiary = {
      id,
      name: data.name,
      type: data.type || 'individual', // individual, organization, emergency
      priority: data.priority || 'normal', // urgent, high, normal, low
      category: data.category || 'general', // bills, utilities, education, emergency
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      totalReceived: 0,
      distributionCount: 0,
      metadata: data.metadata || {}
    };

    this.beneficiaries.set(id, beneficiary);
    return beneficiary;
  }

  update(id, data) {
    const existing = this.beneficiaries.get(id);
    if (!existing) {
      throw new Error(`Beneficiary ${id} not found`);
    }

    const updated = {
      ...existing,
      ...data,
      updatedAt: new Date().toISOString()
    };

    this.beneficiaries.set(id, updated);
    return updated;
  }

  get(id) {
    return this.beneficiaries.get(id);
  }

  getAll() {
    return Array.from(this.beneficiaries.values());
  }

  recordDistribution(beneficiaryId, amount, transactionId) {
    const beneficiary = this.beneficiaries.get(beneficiaryId);
    if (!beneficiary) {
      throw new Error(`Beneficiary ${beneficiaryId} not found`);
    }

    beneficiary.totalReceived += amount;
    beneficiary.distributionCount += 1;
    beneficiary.updatedAt = new Date().toISOString();

    const distribution = {
      id: `dist-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`,
      beneficiaryId,
      amount,
      transactionId,
      timestamp: new Date().toISOString()
    };

    this.distributions.push(distribution);
    return distribution;
  }

  getDistributionHistory(beneficiaryId = null) {
    if (beneficiaryId) {
      return this.distributions.filter(d => d.beneficiaryId === beneficiaryId);
    }
    return this.distributions;
  }
}

// ============================================================================
// DIVIDEND ALLOCATOR (AI-Guided)
// ============================================================================

class DividendAllocator {
  constructor(treasury, beneficiaryRegistry) {
    this.treasury = treasury;
    this.registry = beneficiaryRegistry;
    this.allocationHistory = [];
  }

  calculateAllocation(beneficiaryId) {
    const beneficiary = this.registry.get(beneficiaryId);
    if (!beneficiary) {
      throw new Error(`Beneficiary ${beneficiaryId} not found`);
    }

    const balance = this.treasury.getBalance();
    const maxAllocation = balance.maxSingleAllocation;

    // Priority-based multipliers
    const priorityMultipliers = {
      urgent: 1.0,
      high: 0.75,
      normal: 0.5,
      low: 0.25
    };

    // Category-based base amounts
    const categoryBasePercent = {
      emergency: 5,
      bills: 4,
      utilities: 3,
      education: 3,
      general: 2
    };

    const priorityMult = priorityMultipliers[beneficiary.priority] || 0.5;
    const categoryBase = categoryBasePercent[beneficiary.category] || 2;

    // Calculate recommended allocation (respecting 7% max rule)
    let recommended = (balance.total * categoryBase / 100) * priorityMult;
    recommended = Math.min(recommended, maxAllocation);
    recommended = Math.min(recommended, balance.available);

    return {
      beneficiaryId,
      beneficiary: beneficiary.name,
      recommended: Math.round(recommended * 100) / 100,
      maxAllowed: maxAllocation,
      treasuryBalance: balance.total,
      availableBalance: balance.available,
      calculations: {
        priorityMultiplier: priorityMult,
        categoryBasePercent: categoryBase,
        maxAllocationPercent: SOVEREIGN_GUARD_RULES.maxAllocationPercent
      },
      timestamp: new Date().toISOString()
    };
  }

  proposeDistribution(beneficiaries = null) {
    const targets = beneficiaries || this.registry.getAll();
    const balance = this.treasury.getBalance();
    
    const proposals = targets.map(b => {
      const calc = this.calculateAllocation(b.id);
      return {
        beneficiaryId: b.id,
        name: b.name,
        priority: b.priority,
        category: b.category,
        proposedAmount: calc.recommended
      };
    });

    // Sort by priority
    const priorityOrder = { urgent: 0, high: 1, normal: 2, low: 3 };
    proposals.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

    // Ensure total doesn't exceed available funds
    let runningTotal = 0;
    const adjusted = proposals.map(p => {
      let amount = p.proposedAmount;
      if (runningTotal + amount > balance.available) {
        amount = Math.max(0, balance.available - runningTotal);
      }
      runningTotal += amount;
      return { ...p, adjustedAmount: amount };
    });

    return {
      proposals: adjusted,
      summary: {
        totalProposed: runningTotal,
        treasuryBalance: balance.total,
        availableBalance: balance.available,
        reserveBalance: balance.reserved,
        beneficiaryCount: adjusted.length
      },
      timestamp: new Date().toISOString()
    };
  }
}

// ============================================================================
// DISTRIBUTION ENGINE
// ============================================================================

class DistributionEngine extends EventEmitter {
  constructor(treasury, beneficiaryRegistry, allocator) {
    super();
    this.treasury = treasury;
    this.registry = beneficiaryRegistry;
    this.allocator = allocator;
    this.pendingDistributions = [];
    this.completedDistributions = [];
    this.dailyCount = 0;
    this.lastReset = new Date().toDateString();
  }

  resetDailyCounter() {
    const today = new Date().toDateString();
    if (today !== this.lastReset) {
      this.dailyCount = 0;
      this.lastReset = today;
    }
  }

  async executeDistribution(beneficiaryId, amount, approver, metadata = {}) {
    this.resetDailyCounter();

    // Check daily limit
    if (this.dailyCount >= SOVEREIGN_GUARD_RULES.maxDailyDistributions) {
      throw new Error(`Daily distribution limit (${SOVEREIGN_GUARD_RULES.maxDailyDistributions}) exceeded`);
    }

    const beneficiary = this.registry.get(beneficiaryId);
    if (!beneficiary) {
      throw new Error(`Beneficiary ${beneficiaryId} not found`);
    }

    // Validate amount against 7% rule
    const balance = this.treasury.getBalance();
    if (amount > balance.maxSingleAllocation) {
      throw new Error(`Amount exceeds ${SOVEREIGN_GUARD_RULES.maxAllocationPercent}% maximum allocation rule`);
    }

    // Check for large transaction delay
    if (amount > SOVEREIGN_GUARD_RULES.largeTransactionThreshold) {
      const pending = {
        id: `pending-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`,
        beneficiaryId,
        amount,
        approver,
        metadata,
        createdAt: new Date().toISOString(),
        executeAfter: new Date(Date.now() + SOVEREIGN_GUARD_RULES.minApprovalDelay).toISOString(),
        status: 'PENDING'
      };
      this.pendingDistributions.push(pending);
      this.emit('distributionPending', pending);
      return { status: 'PENDING', distribution: pending };
    }

    // Execute immediately
    return this.executeImmediate(beneficiaryId, amount, approver, metadata);
  }

  executeImmediate(beneficiaryId, amount, approver, metadata = {}) {
    const transaction = this.treasury.withdraw(
      amount,
      `Beneficiary: ${beneficiaryId}`,
      approver,
      { ...metadata, distributionType: 'dividend' }
    );

    const distribution = this.registry.recordDistribution(beneficiaryId, amount, transaction.id);

    const completed = {
      ...distribution,
      transaction,
      status: 'COMPLETED',
      approver
    };

    this.completedDistributions.push(completed);
    this.dailyCount += 1;
    
    this.emit('distributionCompleted', completed);
    return { status: 'COMPLETED', distribution: completed };
  }

  async processPending(approver) {
    const now = new Date();
    const ready = this.pendingDistributions.filter(
      p => p.status === 'PENDING' && new Date(p.executeAfter) <= now
    );

    const results = [];
    for (const pending of ready) {
      try {
        const result = this.executeImmediate(
          pending.beneficiaryId,
          pending.amount,
          approver,
          pending.metadata
        );
        pending.status = 'EXECUTED';
        results.push({ pending, result });
      } catch (error) {
        pending.status = 'FAILED';
        pending.error = error.message;
        results.push({ pending, error: error.message });
      }
    }

    return results;
  }

  getPendingDistributions() {
    return this.pendingDistributions.filter(p => p.status === 'PENDING');
  }

  getDistributionHistory() {
    return this.completedDistributions;
  }
}

// ============================================================================
// GOVERNANCE LOGGING
// ============================================================================

class GovernanceLogger extends EventEmitter {
  constructor() {
    super();
    this.decisions = [];
  }

  logDecision(decision) {
    const entry = {
      id: `gov-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`,
      type: decision.type,
      description: decision.description,
      proposer: decision.proposer,
      approvers: decision.approvers || [],
      outcome: decision.outcome,
      timestamp: new Date().toISOString(),
      metadata: decision.metadata || {},
      hash: null
    };

    entry.hash = this.hashDecision(entry);
    this.decisions.push(entry);
    
    this.emit('decisionLogged', entry);
    return entry;
  }

  hashDecision(decision) {
    const data = JSON.stringify({
      ...decision,
      hash: undefined
    });
    return crypto.createHash('sha256').update(data).digest('hex');
  }

  getDecisions(filter = {}) {
    let filtered = this.decisions;

    if (filter.type) {
      filtered = filtered.filter(d => d.type === filter.type);
    }

    if (filter.startDate) {
      filtered = filtered.filter(d => new Date(d.timestamp) >= new Date(filter.startDate));
    }

    if (filter.endDate) {
      filtered = filtered.filter(d => new Date(d.timestamp) <= new Date(filter.endDate));
    }

    return filtered.map(d => ({
      ...d,
      verified: this.hashDecision({ ...d, hash: undefined }) === d.hash
    }));
  }

  verifyIntegrity() {
    const results = this.decisions.map(d => ({
      id: d.id,
      timestamp: d.timestamp,
      valid: this.hashDecision({ ...d, hash: undefined }) === d.hash
    }));

    return {
      totalDecisions: results.length,
      validDecisions: results.filter(r => r.valid).length,
      invalidDecisions: results.filter(r => !r.valid).length,
      results
    };
  }
}

// ============================================================================
// VALORYIELD FINANCIAL OS - MAIN APPLICATION
// ============================================================================

class ValorYieldOS extends EventEmitter {
  constructor() {
    super();
    this.treasury = new Treasury();
    this.registry = new BeneficiaryRegistry();
    this.allocator = new DividendAllocator(this.treasury, this.registry);
    this.distribution = new DistributionEngine(this.treasury, this.registry, this.allocator);
    this.governance = new GovernanceLogger();
    this.startedAt = new Date().toISOString();

    // Wire up events for unified logging
    this.setupEventListeners();
  }

  setupEventListeners() {
    this.treasury.on('deposit', (tx) => {
      this.governance.logDecision({
        type: 'TREASURY_DEPOSIT',
        description: `Deposit of $${tx.amount} from ${tx.source}`,
        proposer: 'SYSTEM',
        outcome: 'EXECUTED',
        metadata: { transactionId: tx.id }
      });
    });

    this.treasury.on('withdrawal', (tx) => {
      this.governance.logDecision({
        type: 'TREASURY_WITHDRAWAL',
        description: `Withdrawal of $${tx.amount} to ${tx.destination}`,
        proposer: tx.approver,
        approvers: [tx.approver],
        outcome: 'EXECUTED',
        metadata: { transactionId: tx.id }
      });
    });

    this.distribution.on('distributionCompleted', (dist) => {
      this.emit('distribution', dist);
    });
  }

  getStatus() {
    const balance = this.treasury.getBalance();
    const pending = this.distribution.getPendingDistributions();
    const beneficiaries = this.registry.getAll();
    const integrityCheck = this.governance.verifyIntegrity();

    return {
      system: {
        name: 'ValorYield Sovereign Financial OS',
        version: '1.0.0',
        startedAt: this.startedAt,
        uptime: Date.now() - new Date(this.startedAt).getTime()
      },
      legalEntities: LEGAL_ENTITIES,
      treasury: balance,
      beneficiaries: {
        total: beneficiaries.length,
        byCategory: this.groupBy(beneficiaries, 'category'),
        byPriority: this.groupBy(beneficiaries, 'priority')
      },
      distributions: {
        pending: pending.length,
        completed: this.distribution.completedDistributions.length,
        dailyRemaining: SOVEREIGN_GUARD_RULES.maxDailyDistributions - this.distribution.dailyCount
      },
      governance: {
        totalDecisions: integrityCheck.totalDecisions,
        integrityValid: integrityCheck.invalidDecisions === 0
      },
      sovereignGuard: SOVEREIGN_GUARD_RULES
    };
  }

  groupBy(arr, key) {
    return arr.reduce((acc, item) => {
      const group = item[key];
      acc[group] = (acc[group] || 0) + 1;
      return acc;
    }, {});
  }
}

// ============================================================================
// EXPRESS API SERVER
// ============================================================================

// Simple in-memory rate limiter
class RateLimiter {
  constructor(windowMs = 60000, maxRequests = 100) {
    this.windowMs = windowMs;
    this.maxRequests = maxRequests;
    this.requests = new Map();
  }

  isAllowed(ip) {
    const now = Date.now();
    const windowStart = now - this.windowMs;
    
    // Clean old entries
    for (const [key, timestamps] of this.requests.entries()) {
      const filtered = timestamps.filter(t => t > windowStart);
      if (filtered.length === 0) {
        this.requests.delete(key);
      } else {
        this.requests.set(key, filtered);
      }
    }
    
    const timestamps = this.requests.get(ip) || [];
    if (timestamps.length >= this.maxRequests) {
      return false;
    }
    
    timestamps.push(now);
    this.requests.set(ip, timestamps);
    return true;
  }

  middleware() {
    return (req, res, next) => {
      const ip = req.ip || req.socket.remoteAddress || 'unknown';
      if (!this.isAllowed(ip)) {
        return res.status(429).json({ 
          error: 'Too many requests', 
          retryAfter: Math.ceil(this.windowMs / 1000) 
        });
      }
      next();
    };
  }
}

function createServer(os) {
  const app = express();
  app.use(express.json());

  // Rate limiting: 100 requests per minute per IP
  const rateLimiter = new RateLimiter(60000, 100);
  app.use(rateLimiter.middleware());

  // CORS headers
  app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
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

  // System status
  app.get('/status', (req, res) => {
    res.json(os.getStatus());
  });

  // Legal entities
  app.get('/legal', (req, res) => {
    res.json(LEGAL_ENTITIES);
  });

  // =====================
  // Treasury Routes
  // =====================
  
  app.get('/treasury', (req, res) => {
    res.json(os.treasury.getBalance());
  });

  app.post('/treasury/deposit', (req, res) => {
    try {
      const { amount, source, metadata } = req.body;
      const tx = os.treasury.deposit(amount, source, metadata);
      res.json({ success: true, transaction: tx });
    } catch (error) {
      res.status(400).json({ success: false, error: error.message });
    }
  });

  app.get('/treasury/audit', (req, res) => {
    const { startDate, endDate } = req.query;
    const trail = os.treasury.getAuditTrail(startDate, endDate);
    res.json(trail);
  });

  // =====================
  // Beneficiary Routes
  // =====================

  app.get('/beneficiaries', (req, res) => {
    res.json(os.registry.getAll());
  });

  app.post('/beneficiaries', (req, res) => {
    try {
      const { id, ...data } = req.body;
      const beneficiary = os.registry.register(id, data);
      res.json({ success: true, beneficiary });
    } catch (error) {
      res.status(400).json({ success: false, error: error.message });
    }
  });

  app.get('/beneficiaries/:id', (req, res) => {
    const beneficiary = os.registry.get(req.params.id);
    if (!beneficiary) {
      return res.status(404).json({ error: 'Beneficiary not found' });
    }
    res.json(beneficiary);
  });

  app.put('/beneficiaries/:id', (req, res) => {
    try {
      const updated = os.registry.update(req.params.id, req.body);
      res.json({ success: true, beneficiary: updated });
    } catch (error) {
      res.status(400).json({ success: false, error: error.message });
    }
  });

  // =====================
  // Allocation Routes
  // =====================

  app.get('/allocations/calculate/:beneficiaryId', (req, res) => {
    try {
      const allocation = os.allocator.calculateAllocation(req.params.beneficiaryId);
      res.json(allocation);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  });

  app.get('/allocations/propose', (req, res) => {
    const proposal = os.allocator.proposeDistribution();
    res.json(proposal);
  });

  // =====================
  // Distribution Routes
  // =====================

  app.post('/distributions', async (req, res) => {
    try {
      const { beneficiaryId, amount, approver, metadata } = req.body;
      const result = await os.distribution.executeDistribution(beneficiaryId, amount, approver, metadata);
      res.json(result);
    } catch (error) {
      res.status(400).json({ success: false, error: error.message });
    }
  });

  app.get('/distributions', (req, res) => {
    res.json(os.distribution.getDistributionHistory());
  });

  app.get('/distributions/pending', (req, res) => {
    res.json(os.distribution.getPendingDistributions());
  });

  app.post('/distributions/process-pending', async (req, res) => {
    try {
      const { approver } = req.body;
      const results = await os.distribution.processPending(approver);
      res.json({ success: true, results });
    } catch (error) {
      res.status(400).json({ success: false, error: error.message });
    }
  });

  // =====================
  // Governance Routes
  // =====================

  app.get('/governance/decisions', (req, res) => {
    const { type, startDate, endDate } = req.query;
    const decisions = os.governance.getDecisions({ type, startDate, endDate });
    res.json(decisions);
  });

  app.post('/governance/decisions', (req, res) => {
    try {
      const decision = os.governance.logDecision(req.body);
      res.json({ success: true, decision });
    } catch (error) {
      res.status(400).json({ success: false, error: error.message });
    }
  });

  app.get('/governance/verify', (req, res) => {
    const integrity = os.governance.verifyIntegrity();
    res.json(integrity);
  });

  // =====================
  // Queen Compatibility (Webhook endpoints)
  // =====================

  app.post('/signals/financial', (req, res) => {
    try {
      const { action, payload } = req.body;
      
      let result;
      switch (action) {
        case 'deposit':
          result = os.treasury.deposit(payload.amount, payload.source, payload.metadata);
          break;
        case 'propose':
          result = os.allocator.proposeDistribution();
          break;
        case 'status':
          result = os.getStatus();
          break;
        default:
          return res.status(400).json({ error: `Unknown action: ${action}` });
      }
      
      res.json({ success: true, result });
    } catch (error) {
      res.status(400).json({ success: false, error: error.message });
    }
  });

  app.post('/webhooks/github', (req, res) => {
    // Log GitHub events for governance tracking
    const event = req.headers['x-github-event'];
    os.governance.logDecision({
      type: 'GITHUB_EVENT',
      description: `GitHub ${event} event received`,
      proposer: 'GITHUB_WEBHOOK',
      outcome: 'LOGGED',
      metadata: { event, deliveryId: req.headers['x-github-delivery'] }
    });
    res.json({ received: true });
  });

  app.post('/treasury/allocate', async (req, res) => {
    try {
      const { beneficiaryId, amount, approver, metadata } = req.body;
      const result = await os.distribution.executeDistribution(beneficiaryId, amount, approver, metadata);
      res.json(result);
    } catch (error) {
      res.status(400).json({ success: false, error: error.message });
    }
  });

  // =====================
  // Documentation
  // =====================

  app.get('/', (req, res) => {
    res.json({
      name: 'ValorYield Sovereign Financial OS',
      description: 'Banking for the People, by the Code',
      version: '1.0.0',
      legalEntities: {
        dao: `${LEGAL_ENTITIES.dao.name} (EIN: ${LEGAL_ENTITIES.dao.ein})`,
        pbc: `${LEGAL_ENTITIES.pbc.name} (EIN: ${LEGAL_ENTITIES.pbc.ein})`
      },
      endpoints: {
        status: 'GET /status',
        legal: 'GET /legal',
        treasury: {
          balance: 'GET /treasury',
          deposit: 'POST /treasury/deposit',
          audit: 'GET /treasury/audit',
          allocate: 'POST /treasury/allocate'
        },
        beneficiaries: {
          list: 'GET /beneficiaries',
          create: 'POST /beneficiaries',
          get: 'GET /beneficiaries/:id',
          update: 'PUT /beneficiaries/:id'
        },
        allocations: {
          calculate: 'GET /allocations/calculate/:beneficiaryId',
          propose: 'GET /allocations/propose'
        },
        distributions: {
          execute: 'POST /distributions',
          list: 'GET /distributions',
          pending: 'GET /distributions/pending',
          processPending: 'POST /distributions/process-pending'
        },
        governance: {
          decisions: 'GET /governance/decisions',
          log: 'POST /governance/decisions',
          verify: 'GET /governance/verify'
        },
        signals: {
          financial: 'POST /signals/financial',
          github: 'POST /webhooks/github'
        }
      },
      sovereignGuard: SOVEREIGN_GUARD_RULES
    });
  });

  return app;
}

// ============================================================================
// MAIN ENTRY POINT
// ============================================================================

const os = new ValorYieldOS();
const app = createServer(os);

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    VALORYIELD SOVEREIGN FINANCIAL OS                          ║
║                    "Banking for the People, by the Code"                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  Legal Foundation:                                                            ║
║  ├── Strategickhaos DAO LLC (EIN: 39-2900295) - Wyoming DAO Statute          ║
║  └── ValorYield Engine PBC (EIN: 39-2923503) - Public Benefit Corp           ║
║                                                                               ║
║  SovereignGuard Rules:                                                        ║
║  ├── Max Allocation: ${SOVEREIGN_GUARD_RULES.maxAllocationPercent}% per distribution                                      ║
║  ├── Reserve Requirement: ${SOVEREIGN_GUARD_RULES.reserveRequirementPercent}%                                             ║
║  ├── Large Transaction Delay: 24 hours                                       ║
║  └── Max Daily Distributions: ${SOVEREIGN_GUARD_RULES.maxDailyDistributions}                                           ║
║                                                                               ║
║  Server running on: http://localhost:${PORT}                                     ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
  `);
});

export { ValorYieldOS, Treasury, BeneficiaryRegistry, DividendAllocator, DistributionEngine, GovernanceLogger };
