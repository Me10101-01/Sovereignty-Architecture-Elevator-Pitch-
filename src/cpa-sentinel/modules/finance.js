// src/cpa-sentinel/modules/finance.js
// Finance Module - Stripe, Sequence.io, NinjaTrader monitoring

export class FinanceModule {
  constructor(config) {
    this.config = config || {};
    this.enabled = true;
    this.healthy = true;
    this.alerts = [];
    this.copycatDetections = [];
  }

  getStatus() {
    return {
      enabled: this.enabled,
      healthy: this.healthy,
      integrations: {
        stripe: this.config.stripe?.enabled || false,
        sequence_io: this.config.sequence_io?.enabled || false,
        plaid: this.config.plaid?.enabled || false,
        ninjatrader: this.config.ninjatrader?.enabled || false,
        crypto_wallets: this.config.crypto_wallets?.enabled || false
      },
      copycatDetection: this.config.sequence_io?.copycat_detection || false,
      watchedNames: this.config.sequence_io?.watch_names || []
    };
  }

  getWatchedNames() {
    return this.config.sequence_io?.watch_names || [];
  }

  // Sequence.io copycat detection
  async checkForCopycat(invoiceData) {
    const watchedNames = this.getWatchedNames();
    const lowercasedNames = watchedNames.map(n => n.toLowerCase());
    
    const textToCheck = [
      invoiceData.sender_name,
      invoiceData.company_name,
      invoiceData.description
    ].filter(Boolean).join(' ').toLowerCase();
    
    for (const name of lowercasedNames) {
      if (textToCheck.includes(name)) {
        const detection = {
          type: 'copycat_detected',
          matchedName: name,
          invoice: invoiceData,
          detectedAt: new Date().toISOString(),
          severity: 'high'
        };
        this.copycatDetections.push(detection);
        this.alerts.push(detection);
        return detection;
      }
    }
    
    return null;
  }

  // Check payment descriptions for brand misuse
  async checkPaymentDescription(description) {
    const watchedNames = this.getWatchedNames();
    const lowercased = description.toLowerCase();
    
    for (const name of watchedNames) {
      if (lowercased.includes(name.toLowerCase())) {
        return {
          flagged: true,
          matchedName: name,
          description,
          timestamp: new Date().toISOString()
        };
      }
    }
    
    return { flagged: false };
  }

  getRecentAlerts(count = 10) {
    return this.alerts.slice(-count);
  }

  getCopycatDetections(count = 10) {
    return this.copycatDetections.slice(-count);
  }
}

export default FinanceModule;
