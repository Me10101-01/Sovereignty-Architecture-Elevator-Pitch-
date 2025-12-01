// src/cpa-sentinel/routes/api.js
// API routes for CPA Sentinel

import { Router } from 'express';

export function APIRouter(modules, config) {
  const router = Router();

  // =============
  // EMAIL MODULE
  // =============
  
  // Get Proofpoint whitelist
  router.get('/email/whitelist', (req, res) => {
    res.json({
      whitelist: modules.email.getWhitelist(),
      count: modules.email.getWhitelist().length
    });
  });

  // Check if sender should be auto-released
  router.post('/email/check-release', (req, res) => {
    const { sender } = req.body;
    if (!sender) {
      return res.status(400).json({ error: 'sender is required' });
    }
    const shouldRelease = modules.email.shouldAutoRelease(sender);
    res.json({ sender, shouldRelease });
  });

  // Process quarantined email
  router.post('/email/process-quarantine', async (req, res) => {
    const { sender, subject } = req.body;
    if (!sender) {
      return res.status(400).json({ error: 'sender is required' });
    }
    const result = await modules.email.processQuarantinedEmail({ sender, subject });
    res.json(result);
  });

  // =============
  // FINANCE MODULE
  // =============
  
  // Get watched names for copycat detection
  router.get('/finance/watch-names', (req, res) => {
    res.json({
      watchedNames: modules.finance.getWatchedNames()
    });
  });

  // Check for copycat invoicing
  router.post('/finance/check-copycat', async (req, res) => {
    const { sender_name, company_name, description } = req.body;
    const result = await modules.finance.checkForCopycat({
      sender_name,
      company_name,
      description
    });
    res.json({ detection: result });
  });

  // Check payment description
  router.post('/finance/check-payment', async (req, res) => {
    const { description } = req.body;
    if (!description) {
      return res.status(400).json({ error: 'description is required' });
    }
    const result = await modules.finance.checkPaymentDescription(description);
    res.json(result);
  });

  // Get copycat detections
  router.get('/finance/copycats', (req, res) => {
    const count = parseInt(req.query.count) || 10;
    res.json({
      detections: modules.finance.getCopycatDetections(count)
    });
  });

  // =============
  // BRAND MODULE
  // =============
  
  // Check USPTO status
  router.post('/brand/check-uspto', async (req, res) => {
    const { markId } = req.body;
    const result = await modules.brand.checkUSPTOStatus(markId);
    res.json(result);
  });

  // Check GitHub forks
  router.post('/brand/check-forks', async (req, res) => {
    const { repo } = req.body;
    if (!repo) {
      return res.status(400).json({ error: 'repo is required' });
    }
    const result = await modules.brand.checkGitHubForks(repo);
    res.json(result);
  });

  // Check domain WHOIS
  router.post('/brand/check-domain', async (req, res) => {
    const { domain } = req.body;
    if (!domain) {
      return res.status(400).json({ error: 'domain is required' });
    }
    const result = await modules.brand.checkDomainWhois(domain);
    res.json(result);
  });

  // =============
  // CREDIT MODULE
  // =============
  
  // Check Wyoming good standing
  router.get('/credit/wyoming', async (req, res) => {
    const entityId = req.query.entityId;
    const result = await modules.credit.checkWyomingGoodStanding(entityId);
    res.json(result);
  });

  // Check D&B PAYDEX
  router.get('/credit/paydex', async (req, res) => {
    const dunsNumber = req.query.duns;
    const result = await modules.credit.checkPAYDEX(dunsNumber);
    res.json(result);
  });

  // =============
  // VERIFICATION MODULE
  // =============
  
  // Screen against OFAC
  router.post('/verification/ofac', async (req, res) => {
    const { name, entityType } = req.body;
    if (!name) {
      return res.status(400).json({ error: 'name is required' });
    }
    const result = await modules.verification.screenOFAC(name, entityType);
    res.json(result);
  });

  // Check UCC filings
  router.post('/verification/ucc', async (req, res) => {
    const { entityName, state } = req.body;
    if (!entityName) {
      return res.status(400).json({ error: 'entityName is required' });
    }
    const result = await modules.verification.checkUCCFilings(entityName, state);
    res.json(result);
  });

  // Check PACER litigation
  router.post('/verification/pacer', async (req, res) => {
    const { entityName } = req.body;
    if (!entityName) {
      return res.status(400).json({ error: 'entityName is required' });
    }
    const result = await modules.verification.checkPACERLitigation(entityName);
    res.json(result);
  });

  // =============
  // AUDIT MODULE
  // =============
  
  // Get audit log
  router.get('/audit/log', (req, res) => {
    const count = parseInt(req.query.count) || 50;
    res.json({
      entries: modules.audit.getAuditLog(count)
    });
  });

  // Create audit entry
  router.post('/audit/log', (req, res) => {
    const { eventType, data, actor } = req.body;
    if (!eventType) {
      return res.status(400).json({ error: 'eventType is required' });
    }
    const entry = modules.audit.logEvent(eventType, data, actor);
    res.json(entry);
  });

  // Get Merkle roots
  router.get('/audit/merkle-roots', (req, res) => {
    const count = parseInt(req.query.count) || 10;
    res.json({
      merkleRoots: modules.audit.getMerkleRoots(count)
    });
  });

  // Get git anchors
  router.get('/audit/anchors', (req, res) => {
    const count = parseInt(req.query.count) || 10;
    res.json({
      anchors: modules.audit.getAnchors(count)
    });
  });

  // Create git anchor
  router.post('/audit/anchor', (req, res) => {
    const { commitHash, description } = req.body;
    if (!commitHash) {
      return res.status(400).json({ error: 'commitHash is required' });
    }
    const anchor = modules.audit.createGitAnchor(commitHash, description);
    res.json(anchor);
  });

  // =============
  // CREDENTIALS MODULE
  // =============
  
  // Check credential expirations
  router.get('/credentials/check', (req, res) => {
    const alerts = modules.credentials.checkExpirations();
    res.json({
      alerts,
      checkedAt: new Date().toISOString()
    });
  });

  // Get token details
  router.get('/credentials/token/:name', (req, res) => {
    const details = modules.credentials.getTokenDetails(req.params.name);
    if (!details) {
      return res.status(404).json({ error: 'Token not found' });
    }
    res.json(details);
  });

  // Get all tokens
  router.get('/credentials/tokens', (req, res) => {
    res.json({
      tokens: modules.credentials.getTokens().map(t => ({
        name: t.name,
        user: t.user,
        expires: t.expires,
        ...modules.credentials.getTokenDetails(t.name)
      }))
    });
  });

  // =============
  // SECURITY MODULE
  // =============
  
  // Track login event
  router.post('/security/login', (req, res) => {
    const { source, ip, userId, metadata } = req.body;
    if (!source || !ip) {
      return res.status(400).json({ error: 'source and ip are required' });
    }
    const event = modules.security.trackLogin(source, ip, userId, metadata);
    res.json(event);
  });

  // Whitelist IP
  router.post('/security/whitelist-ip', (req, res) => {
    const { ip } = req.body;
    if (!ip) {
      return res.status(400).json({ error: 'ip is required' });
    }
    const success = modules.security.whitelistIP(ip);
    res.json({ success, ip });
  });

  // Get login events
  router.get('/security/logins', (req, res) => {
    const count = parseInt(req.query.count) || 50;
    res.json({
      events: modules.security.getLoginEvents(count)
    });
  });

  // Get correlated alerts
  router.get('/security/correlated', (req, res) => {
    const count = parseInt(req.query.count) || 10;
    res.json({
      correlatedAlerts: modules.security.getCorrelatedAlerts(count)
    });
  });

  // =============
  // ENTITIES
  // =============
  
  // Get monitored entities
  router.get('/entities', (req, res) => {
    res.json({
      entities: config.entities || []
    });
  });

  // Get specific entity
  router.get('/entities/:id', (req, res) => {
    const entities = config.entities || [];
    const entity = entities.find(e => e.id === req.params.id);
    if (!entity) {
      return res.status(404).json({ error: 'Entity not found' });
    }
    res.json(entity);
  });

  return router;
}

export default APIRouter;
