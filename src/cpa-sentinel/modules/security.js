// src/cpa-sentinel/modules/security.js
// Security Module - Alert correlation, IP monitoring, Discord login tracking

export class SecurityModule {
  constructor(config) {
    this.config = config || {};
    this.enabled = true;
    this.healthy = true;
    this.loginEvents = [];
    this.correlatedAlerts = [];
    this.knownIPs = new Set();
  }

  getStatus() {
    return {
      enabled: this.enabled,
      healthy: this.healthy,
      discordLoginMonitoring: this.config.discord_login_monitoring || false,
      alertOnNewIP: this.config.alert_on_new_ip || true,
      correlationEnabled: this.config.correlation?.enabled || false,
      correlationSources: this.config.correlation?.sources || [],
      knownIPCount: this.knownIPs.size
    };
  }

  // Track login event
  trackLogin(source, ip, userId, metadata = {}) {
    const event = {
      id: crypto.randomUUID(),
      source,
      ip,
      userId,
      metadata,
      timestamp: new Date().toISOString(),
      isNewIP: !this.knownIPs.has(ip)
    };
    
    this.loginEvents.push(event);
    
    // Alert on new IP if configured
    if (event.isNewIP && this.config.alert_on_new_ip) {
      this.correlatedAlerts.push({
        type: 'new_ip_detected',
        source,
        ip,
        userId,
        severity: 'medium',
        timestamp: event.timestamp
      });
    }
    
    // Add to known IPs
    this.knownIPs.add(ip);
    
    return event;
  }

  // Add IP to whitelist
  whitelistIP(ip) {
    this.config.ip_whitelist = this.config.ip_whitelist || [];
    if (!this.config.ip_whitelist.includes(ip)) {
      this.config.ip_whitelist.push(ip);
    }
    this.knownIPs.add(ip);
    return true;
  }

  // Correlate alerts from multiple sources
  correlateAlerts(alerts) {
    const correlated = [];
    const timeWindow = 5 * 60 * 1000; // 5 minutes
    
    // Group alerts by time window
    const sortedAlerts = [...alerts].sort((a, b) => 
      new Date(a.timestamp) - new Date(b.timestamp)
    );
    
    for (let i = 0; i < sortedAlerts.length; i++) {
      const currentAlert = sortedAlerts[i];
      const currentTime = new Date(currentAlert.timestamp).getTime();
      const relatedAlerts = [currentAlert];
      
      for (let j = i + 1; j < sortedAlerts.length; j++) {
        const compareAlert = sortedAlerts[j];
        const compareTime = new Date(compareAlert.timestamp).getTime();
        
        if (compareTime - currentTime <= timeWindow) {
          relatedAlerts.push(compareAlert);
        } else {
          break;
        }
      }
      
      if (relatedAlerts.length > 1) {
        correlated.push({
          id: crypto.randomUUID(),
          alerts: relatedAlerts,
          sources: [...new Set(relatedAlerts.map(a => a.source))],
          timeSpan: {
            start: relatedAlerts[0].timestamp,
            end: relatedAlerts[relatedAlerts.length - 1].timestamp
          },
          correlatedAt: new Date().toISOString()
        });
      }
    }
    
    this.correlatedAlerts.push(...correlated);
    return correlated;
  }

  getLoginEvents(count = 50) {
    return this.loginEvents.slice(-count);
  }

  getCorrelatedAlerts(count = 10) {
    return this.correlatedAlerts.slice(-count);
  }
}

export default SecurityModule;
