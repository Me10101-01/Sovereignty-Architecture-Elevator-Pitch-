// src/cpa-sentinel/modules/credentials.js
// Credentials Module - Token rotation, Azure DevOps, expiration alerts

export class CredentialsModule {
  constructor(config) {
    this.config = config || {};
    this.enabled = true;
    this.healthy = true;
    this.alerts = [];
    this.lastCheck = null;
  }

  getStatus() {
    return {
      enabled: this.enabled,
      healthy: this.healthy,
      lastCheck: this.lastCheck,
      azureDevOps: {
        enabled: this.config.azure_devops?.enabled || false,
        tokenCount: this.config.azure_devops?.tokens?.length || 0
      },
      rotationPolicy: this.config.rotation_policy || {}
    };
  }

  getTokens() {
    return this.config.azure_devops?.tokens || [];
  }

  // Check for credential expirations
  checkExpirations() {
    this.lastCheck = new Date().toISOString();
    const tokens = this.getTokens();
    const now = new Date();
    const alerts = [];
    
    for (const token of tokens) {
      if (!token.expires) continue;
      
      const expirationDate = new Date(token.expires);
      const daysUntilExpiry = Math.floor(
        (expirationDate - now) / (1000 * 60 * 60 * 24)
      );
      
      const alertThreshold = token.alert_days_before || 30;
      
      if (daysUntilExpiry <= alertThreshold) {
        const alert = {
          type: 'credential_expiring',
          tokenName: token.name,
          user: token.user,
          expires: token.expires,
          daysUntilExpiry,
          severity: daysUntilExpiry <= 7 ? 'critical' : 
                   daysUntilExpiry <= 14 ? 'high' : 'medium',
          createdAt: new Date().toISOString()
        };
        alerts.push(alert);
        this.alerts.push(alert);
      }
    }
    
    return alerts;
  }

  // Get token details
  getTokenDetails(tokenName) {
    const tokens = this.getTokens();
    const token = tokens.find(t => t.name === tokenName);
    
    if (!token) {
      return null;
    }
    
    const now = new Date();
    const expirationDate = new Date(token.expires);
    const daysUntilExpiry = Math.floor(
      (expirationDate - now) / (1000 * 60 * 60 * 24)
    );
    
    return {
      ...token,
      daysUntilExpiry,
      isExpired: daysUntilExpiry < 0,
      needsRotation: daysUntilExpiry <= (token.alert_days_before || 30)
    };
  }

  getRecentAlerts(count = 10) {
    return this.alerts.slice(-count);
  }
}

export default CredentialsModule;
