// src/cpa-sentinel/config.js
// Configuration loader for CPA Sentinel

import fs from 'fs';
import yaml from 'js-yaml';
import path from 'path';

export function loadConfig() {
  const configPath = process.env.DISCOVERY_CONFIG_PATH || 
    path.resolve(process.cwd(), 'discovery.yml');
  
  try {
    const fileContents = fs.readFileSync(configPath, 'utf8');
    return yaml.load(fileContents);
  } catch (e) {
    console.warn(`Could not load discovery config from ${configPath}:`, e.message);
    return {};
  }
}

export function loadSentinelConfig() {
  const configPath = process.env.CPA_SENTINEL_CONFIG_PATH || 
    path.resolve(process.cwd(), 'cpa_sentinel.yaml');
  
  try {
    const fileContents = fs.readFileSync(configPath, 'utf8');
    return yaml.load(fileContents);
  } catch (e) {
    console.warn(`Could not load sentinel config from ${configPath}:`, e.message);
    return getDefaultConfig();
  }
}

function getDefaultConfig() {
  return {
    sentinel: {
      version: '1.0.0',
      name: 'CPA Sentinel',
      enabled: true
    },
    entities: [],
    email: { providers: {}, proofpoint_whitelist: [] },
    finance: { stripe: { enabled: false } },
    brand: { uspto_tsdr: { enabled: false } },
    credit: { wyoming_sos: { enabled: false } },
    verification: { ofac_sdn: { enabled: false } },
    audit: { merkle_trees: { enabled: false } },
    credentials: { azure_devops: { enabled: false } },
    security: { correlation: { enabled: false } },
    service: { port: 8003 },
    notifications: { discord: { enabled: false } },
    observability: { log_level: 'info' }
  };
}

export default { loadConfig, loadSentinelConfig };
