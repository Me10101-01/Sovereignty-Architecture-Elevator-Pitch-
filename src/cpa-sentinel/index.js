// src/cpa-sentinel/index.js
// CPA Sentinel - Compliance, Protection & Audit Department as a Service
// IDEA_100: StrategicKhaos DAO LLC / ValorYield Engine

import express from 'express';
import { loadConfig, loadSentinelConfig } from './config.js';
import { EmailModule } from './modules/email.js';
import { FinanceModule } from './modules/finance.js';
import { BrandModule } from './modules/brand.js';
import { CreditModule } from './modules/credit.js';
import { VerificationModule } from './modules/verification.js';
import { AuditModule } from './modules/audit.js';
import { CredentialsModule } from './modules/credentials.js';
import { SecurityModule } from './modules/security.js';
import { DashboardRouter } from './routes/dashboard.js';
import { APIRouter } from './routes/api.js';

const app = express();
app.use(express.json());

// Load configurations
const config = loadConfig();
const sentinelConfig = loadSentinelConfig();

// Initialize modules
const modules = {
  email: new EmailModule(sentinelConfig.email),
  finance: new FinanceModule(sentinelConfig.finance),
  brand: new BrandModule(sentinelConfig.brand),
  credit: new CreditModule(sentinelConfig.credit),
  verification: new VerificationModule(sentinelConfig.verification),
  audit: new AuditModule(sentinelConfig.audit),
  credentials: new CredentialsModule(sentinelConfig.credentials),
  security: new SecurityModule(sentinelConfig.security)
};

// Health check endpoint
app.get('/health', (req, res) => {
  const status = {
    status: 'healthy',
    service: 'cpa-sentinel',
    version: sentinelConfig.sentinel?.version || '1.0.0',
    timestamp: new Date().toISOString(),
    modules: Object.fromEntries(
      Object.entries(modules).map(([name, mod]) => [name, mod.getStatus()])
    )
  };
  res.json(status);
});

// Dashboard routes
app.use('/dashboard', DashboardRouter(modules, sentinelConfig));

// API routes
app.use('/api/v1', APIRouter(modules, sentinelConfig));

// Metrics endpoint for Prometheus
app.get('/metrics', (req, res) => {
  const metrics = [];
  
  // Module status metrics
  for (const [name, mod] of Object.entries(modules)) {
    const status = mod.getStatus();
    metrics.push(`cpa_sentinel_module_enabled{module="${name}"} ${status.enabled ? 1 : 0}`);
    metrics.push(`cpa_sentinel_module_healthy{module="${name}"} ${status.healthy ? 1 : 0}`);
  }
  
  // Entity monitoring metrics
  const entities = sentinelConfig.entities || [];
  entities.forEach(entity => {
    metrics.push(`cpa_sentinel_entity_status{name="${entity.name}",type="${entity.type}"} 1`);
  });
  
  res.set('Content-Type', 'text/plain');
  res.send(metrics.join('\n'));
});

// Start server
const port = sentinelConfig.service?.port || 8003;
app.listen(port, () => {
  console.log(`🛡️ CPA Sentinel running on port ${port}`);
  console.log(`📊 Dashboard: http://localhost:${port}/dashboard`);
  console.log(`📡 API: http://localhost:${port}/api/v1`);
  console.log(`❤️ Health: http://localhost:${port}/health`);
  console.log(`📈 Metrics: http://localhost:${port}/metrics`);
  
  // Log monitored entities
  const entities = sentinelConfig.entities || [];
  console.log(`\n🏢 Monitoring ${entities.length} entities:`);
  entities.forEach(e => console.log(`   - ${e.name} (${e.type}: ${e.id})`));
  
  // Start background monitoring tasks
  startMonitoringTasks(modules, sentinelConfig);
});

// Configurable check intervals (in milliseconds)
const CHECK_INTERVALS = {
  CREDENTIAL_CHECK: 24 * 60 * 60 * 1000,  // 24 hours
  INITIAL_CHECK_DELAY: 5000                // 5 seconds
};

function startMonitoringTasks(modules, config) {
  // Get configurable interval or use default (24 hours)
  const credentialCheckInterval = config.observability?.credential_check_interval_ms || 
    CHECK_INTERVALS.CREDENTIAL_CHECK;
  
  // Check credential expiration daily
  setInterval(() => {
    modules.credentials.checkExpirations();
  }, credentialCheckInterval);
  
  // Run initial checks
  setTimeout(() => {
    modules.credentials.checkExpirations();
    console.log('✅ Initial credential expiration check complete');
  }, 5000);
}

export default app;
