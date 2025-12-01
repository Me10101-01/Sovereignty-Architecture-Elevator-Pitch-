// src/cpa-sentinel/modules/audit.js
// Audit Trail Module - Merkle Trees, Git Anchors, 7yr Retention

import crypto from 'crypto';

export class AuditModule {
  constructor(config) {
    this.config = config || {};
    this.enabled = true;
    this.healthy = true;
    this.anchors = [];
    this.merkleRoots = [];
    this.auditLog = [];
  }

  getStatus() {
    return {
      enabled: this.enabled,
      healthy: this.healthy,
      integrations: {
        merkle_trees: this.config.merkle_trees?.enabled || false,
        git_anchors: this.config.git_anchors?.enabled || false
      },
      retentionYears: this.config.retention?.years || 7,
      storageType: this.config.retention?.storage || 'encrypted_cold',
      anchorCount: this.anchors.length,
      merkleRootCount: this.merkleRoots.length
    };
  }

  // Create Merkle root for audit log entries
  createMerkleRoot(entries) {
    if (!entries || entries.length === 0) {
      return null;
    }
    
    // Hash all entries
    const hashes = entries.map(entry => 
      crypto.createHash('sha256').update(JSON.stringify(entry)).digest('hex')
    );
    
    // Build Merkle tree
    let currentLevel = hashes;
    while (currentLevel.length > 1) {
      const nextLevel = [];
      for (let i = 0; i < currentLevel.length; i += 2) {
        const left = currentLevel[i];
        const right = currentLevel[i + 1] || left;
        const combined = crypto.createHash('sha256')
          .update(left + right)
          .digest('hex');
        nextLevel.push(combined);
      }
      currentLevel = nextLevel;
    }
    
    const merkleRoot = {
      root: currentLevel[0],
      entryCount: entries.length,
      createdAt: new Date().toISOString(),
      leaves: hashes
    };
    
    this.merkleRoots.push(merkleRoot);
    return merkleRoot;
  }

  // Create git anchor for immutable record
  createGitAnchor(commitHash, description) {
    const anchor = {
      id: crypto.randomUUID(),
      commitHash,
      description,
      timestamp: new Date().toISOString(),
      verified: false
    };
    
    this.anchors.push(anchor);
    return anchor;
  }

  // Log audit event
  logEvent(eventType, data, actor = 'system') {
    const event = {
      id: crypto.randomUUID(),
      eventType,
      data,
      actor,
      timestamp: new Date().toISOString(),
      hash: crypto.createHash('sha256')
        .update(JSON.stringify({ eventType, data, actor }))
        .digest('hex')
    };
    
    this.auditLog.push(event);
    
    // Check if we should create a new Merkle root
    if (this.auditLog.length % 100 === 0) {
      this.createMerkleRoot(this.auditLog.slice(-100));
    }
    
    return event;
  }

  getAuditLog(count = 50) {
    return this.auditLog.slice(-count);
  }

  getAnchors(count = 10) {
    return this.anchors.slice(-count);
  }

  getMerkleRoots(count = 10) {
    return this.merkleRoots.slice(-count);
  }

  // Verify entry exists in Merkle tree
  verifyEntry(entry, merkleRoot) {
    const entryHash = crypto.createHash('sha256')
      .update(JSON.stringify(entry))
      .digest('hex');
    
    return merkleRoot.leaves.includes(entryHash);
  }
}

export default AuditModule;
