// src/cpa-sentinel/routes/dashboard.js
// Dashboard routes for CPA Sentinel

import { Router } from 'express';

export function DashboardRouter(modules, config) {
  const router = Router();

  // Main dashboard view
  router.get('/', (req, res) => {
    const entities = config.entities || [];
    const moduleStatuses = Object.fromEntries(
      Object.entries(modules).map(([name, mod]) => [name, mod.getStatus()])
    );

    const dashboard = {
      title: 'CPA Sentinel Dashboard',
      version: config.sentinel?.version || '1.0.0',
      timestamp: new Date().toISOString(),
      
      // Summary
      summary: {
        entitiesMonitored: entities.length,
        modulesActive: Object.values(moduleStatuses).filter(s => s.enabled).length,
        modulesHealthy: Object.values(moduleStatuses).filter(s => s.healthy).length,
        totalModules: Object.keys(modules).length
      },
      
      // Entities
      entities: entities.map(e => ({
        name: e.name,
        type: e.type,
        id: e.id,
        status: e.status
      })),
      
      // Module Status Overview
      modules: moduleStatuses,
      
      // Quick Actions
      actions: [
        { name: 'Check Credential Expirations', endpoint: '/api/v1/credentials/check' },
        { name: 'Refresh Email Whitelist', endpoint: '/api/v1/email/whitelist' },
        { name: 'Run OFAC Screening', endpoint: '/api/v1/verification/ofac' },
        { name: 'View Audit Log', endpoint: '/api/v1/audit/log' },
        { name: 'Check WY Good Standing', endpoint: '/api/v1/credit/wyoming' }
      ],
      
      // Proofpoint Whitelist Summary
      proofpointWhitelist: modules.email.getWhitelist().map(w => ({
        sender: w.sender,
        description: w.description
      })),
      
      // Finance Watch Names
      financeWatchNames: modules.finance.getWatchedNames(),
      
      // Recent Alerts
      recentAlerts: {
        credentials: modules.credentials.getRecentAlerts(5),
        security: modules.security.getCorrelatedAlerts(5),
        brand: modules.brand.getRecentAlerts(5)
      },
      
      // Revenue Opportunities
      revenue: config.revenue?.opportunities || []
    };

    res.json(dashboard);
  });

  // Module-specific dashboards
  router.get('/email', (req, res) => {
    res.json({
      module: 'email',
      status: modules.email.getStatus(),
      whitelist: modules.email.getWhitelist(),
      recentReleases: modules.email.getRecentReleases(20)
    });
  });

  router.get('/finance', (req, res) => {
    res.json({
      module: 'finance',
      status: modules.finance.getStatus(),
      watchedNames: modules.finance.getWatchedNames(),
      copycatDetections: modules.finance.getCopycatDetections(20),
      recentAlerts: modules.finance.getRecentAlerts(20)
    });
  });

  router.get('/brand', (req, res) => {
    res.json({
      module: 'brand',
      status: modules.brand.getStatus(),
      monitoredDomains: modules.brand.getMonitoredDomains(),
      monitoredRepos: modules.brand.getMonitoredRepos(),
      keywords: modules.brand.getKeywords(),
      recentAlerts: modules.brand.getRecentAlerts(20)
    });
  });

  router.get('/credit', (req, res) => {
    res.json({
      module: 'credit',
      status: modules.credit.getStatus(),
      statusHistory: modules.credit.getStatusHistory(20)
    });
  });

  router.get('/verification', (req, res) => {
    res.json({
      module: 'verification',
      status: modules.verification.getStatus(),
      screeningHistory: modules.verification.getScreeningHistory(20),
      recentAlerts: modules.verification.getRecentAlerts(20)
    });
  });

  router.get('/audit', (req, res) => {
    res.json({
      module: 'audit',
      status: modules.audit.getStatus(),
      recentAnchors: modules.audit.getAnchors(10),
      merkleRoots: modules.audit.getMerkleRoots(10),
      auditLog: modules.audit.getAuditLog(50)
    });
  });

  router.get('/credentials', (req, res) => {
    res.json({
      module: 'credentials',
      status: modules.credentials.getStatus(),
      tokens: modules.credentials.getTokens().map(t => ({
        name: t.name,
        user: t.user,
        expires: t.expires,
        alertDaysBefore: t.alert_days_before
      })),
      recentAlerts: modules.credentials.getRecentAlerts(20)
    });
  });

  router.get('/security', (req, res) => {
    res.json({
      module: 'security',
      status: modules.security.getStatus(),
      loginEvents: modules.security.getLoginEvents(50),
      correlatedAlerts: modules.security.getCorrelatedAlerts(20)
    });
  });

  return router;
}

export default DashboardRouter;
