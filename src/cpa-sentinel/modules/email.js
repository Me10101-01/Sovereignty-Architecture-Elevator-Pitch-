// src/cpa-sentinel/modules/email.js
// Email Protection Module - Proofpoint Auto-Whitelist

export class EmailModule {
  constructor(config) {
    this.config = config || {};
    this.enabled = true;
    this.healthy = true;
    this.lastCheck = null;
    this.quarantineReleases = [];
  }

  getStatus() {
    return {
      enabled: this.enabled,
      healthy: this.healthy,
      lastCheck: this.lastCheck,
      providers: {
        snhu_outlook: this.config.providers?.snhu_outlook?.enabled || false,
        gmail: this.config.providers?.gmail?.enabled || false,
        proofpoint: this.config.providers?.proofpoint?.enabled || false
      },
      whitelistCount: this.config.proofpoint_whitelist?.length || 0
    };
  }

  getWhitelist() {
    return this.config.proofpoint_whitelist || [];
  }

  shouldAutoRelease(sender) {
    const whitelist = this.getWhitelist();
    return whitelist.some(entry => entry.sender === sender);
  }

  async processQuarantinedEmail(email) {
    this.lastCheck = new Date().toISOString();
    
    if (this.shouldAutoRelease(email.sender)) {
      const entry = this.getWhitelist().find(e => e.sender === email.sender);
      this.quarantineReleases.push({
        sender: email.sender,
        subject: email.subject,
        releasedAt: new Date().toISOString(),
        reason: entry?.description || 'Whitelisted sender'
      });
      return { action: 'release', reason: entry?.description };
    }
    
    return { action: 'quarantine', reason: 'Not in whitelist' };
  }

  getRecentReleases(count = 10) {
    return this.quarantineReleases.slice(-count);
  }
}

export default EmailModule;
