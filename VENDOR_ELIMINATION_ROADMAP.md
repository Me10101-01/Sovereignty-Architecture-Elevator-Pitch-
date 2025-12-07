# VENDOR ELIMINATION ROADMAP

## Strategic Plan for Complete Sovereignty (2026-2027)

**Document ID:** `VENDOR-ELIM-2025-001`  
**Version:** 1.0  
**Last Updated:** December 7, 2025  
**Parent Document:** [ARSENAL_ANALYSIS.md](./ARSENAL_ANALYSIS.md)  
**Status:** Approved by AI Board (4/5 + Human)

---

## EXECUTIVE SUMMARY

This roadmap outlines the strategic elimination of all vendor dependencies by Q2 2027, achieving complete operational sovereignty while maintaining or improving service quality. The plan targets **~$1,000+/year** in direct cost savings plus elimination of transaction fees and usage-based pricing.

### Success Criteria

- ✅ **100% data portability** (<24hr export capability)
- ✅ **Zero vendor lock-in** (can migrate any service in <1 week)
- ✅ **Cost reduction** (eliminate annual subscription fees)
- ✅ **Feature parity** (match or exceed current capabilities)
- ✅ **Operational resilience** (self-hosted, self-managed)

---

## TABLE OF CONTENTS

1. [Current Vendor Landscape](#current-vendor-landscape)
2. [Sovereign Replacements](#sovereign-replacements)
3. [Migration Timeline](#migration-timeline)
4. [Implementation Details](#implementation-details)
5. [Risk Mitigation](#risk-mitigation)
6. [Success Metrics](#success-metrics)

---

## CURRENT VENDOR LANDSCAPE

### Active Vendor Dependencies

| Vendor | Service | Annual Cost | Usage | Lock-in Risk | Priority |
|--------|---------|-------------|-------|--------------|----------|
| **Airtable** | Database/CRM | $240/year | CPA Sentinel, compliance tracking | HIGH | P0 |
| **Zapier** | Automation | $240+/year | Email monitoring, webhooks, notifications | HIGH | P0 |
| **GitHub** | Version control | $0-252/year | Code hosting, CI/CD, collaboration | MEDIUM | P1 |
| **Discord** | Communication | $0-84/year | Team chat, bot hosting, notifications | MEDIUM | P2 |
| **Notion** | Documentation | $0-120/year | Knowledge base, wikis, notes | LOW | P3 |
| **Stripe** | Payments | 2.9%+30¢/txn | Trading bot deposits, client billing | MEDIUM | P2 |
| **Obsidian Sync** | Knowledge sync | $96/year | 34+ vault synchronization | LOW | P3 |

**Total Annual Cost:** $576-1,032 base + transaction fees (~$200-500/year) = **$776-1,532/year**

### Vendor Risk Assessment

#### HIGH RISK (Must Eliminate)

**Airtable:**
- ❌ **Proprietary format:** API export only, no native database dump
- ❌ **Increasing prices:** Free tier reduced, paid tier expensive
- ❌ **Data volume:** 1,500+ records, 50+ tables = painful migration
- ⚠️ **Critical function:** Compliance tracking (CPA Sentinel)

**Zapier:**
- ❌ **Usage-based pricing:** Unpredictable costs as automation scales
- ❌ **Workflow lock-in:** 50+ zaps = weeks to recreate
- ❌ **No export:** Workflows not portable (must recreate)
- ⚠️ **Critical function:** Email monitoring, deadline alerts

#### MEDIUM RISK (Should Eliminate)

**GitHub:**
- ✅ **Git is portable:** Can migrate repos easily
- ⚠️ **Actions lock-in:** Workflows use GitHub-specific syntax
- ⚠️ **Collaboration features:** Issues, PRs, Projects not standardized
- ℹ️ **Current cost:** $0 (free tier sufficient for now)

**Discord:**
- ✅ **Data export available:** Can export message history
- ⚠️ **Bot lock-in:** Custom bots tied to Discord API
- ⚠️ **Integration ecosystem:** Webhooks, slash commands proprietary
- ℹ️ **Current cost:** $0 (free tier)

**Stripe:**
- ✅ **Standard APIs:** Can switch to other payment processors
- ⚠️ **Transaction history:** Export available but cumbersome
- ⚠️ **Customer data:** Stored in Stripe, need migration plan
- ℹ️ **Current cost:** Transaction fees only

#### LOW RISK (Optional to Eliminate)

**Notion:**
- ✅ **Markdown export:** Full content portability
- ✅ **Low usage:** Most knowledge in Obsidian already
- ℹ️ **Current cost:** $0 (free tier)

**Obsidian Sync:**
- ✅ **E2E encrypted:** Data security maintained
- ✅ **Reliable:** 99.9% uptime, fast sync
- ℹ️ **Worth keeping:** $96/year for 34+ vaults is excellent value
- 📌 **Recommendation:** Keep (not a lock-in risk)

---

## SOVEREIGN REPLACEMENTS

### KhaosBase (Airtable Replacement)

**Technology Stack:**
- **Database:** PostgreSQL 16+ (industry standard, 30+ years proven)
- **UI Layer:** NocoDB or Baserow (open-source Airtable clones)
- **Hosting:** GKE cluster (existing infrastructure)
- **Backup:** Automated pg_dump to Google Cloud Storage

**Feature Parity:**

| Feature | Airtable | KhaosBase | Status |
|---------|----------|-----------|--------|
| **Relational tables** | ✅ | ✅ PostgreSQL | Ready |
| **Views/filters** | ✅ | ✅ NocoDB | Ready |
| **Forms** | ✅ | ✅ Baserow | Ready |
| **API access** | ✅ | ✅ REST + GraphQL | Ready |
| **Automations** | ✅ | 🔄 KhaosFlow | Dependent |
| **Collaboration** | ✅ | ✅ RBAC in NocoDB | Ready |

**Migration Plan:**
1. Export all Airtable tables to CSV/JSON (8 hours)
2. Generate PostgreSQL schema from Airtable metadata (4 hours)
3. Import data with validation (4 hours)
4. Deploy NocoDB connected to PostgreSQL (2 hours)
5. Recreate views and filters (4 hours)
6. Parallel run (1 week validation)
7. Cutover and cancel Airtable (immediate)

**Total Migration Time:** 22 hours + 1 week validation = **2 weeks**

---

### KhaosFlow (Zapier Replacement)

**Technology Stack:**
- **Workflow Engine:** n8n (open-source Zapier alternative)
- **Alternative:** Temporal.io (code-first approach for complex workflows)
- **Hosting:** GKE cluster (existing infrastructure)
- **Backup:** Workflow definitions in Git (version controlled)

**Feature Parity:**

| Feature | Zapier | KhaosFlow (n8n) | Status |
|---------|--------|-----------------|--------|
| **Webhooks** | ✅ | ✅ | Ready |
| **Email triggers** | ✅ | ✅ IMAP/POP3 | Ready |
| **HTTP requests** | ✅ | ✅ | Ready |
| **Database ops** | ✅ | ✅ PostgreSQL node | Ready |
| **Scheduled tasks** | ✅ | ✅ Cron | Ready |
| **Error handling** | ✅ | ✅ | Ready |
| **UI builder** | ✅ | ✅ Visual workflow | Ready |
| **Integrations** | 5,000+ | 300+ (growing) | Sufficient |

**Migration Plan:**
1. Document all 50+ Zapier workflows (1 week)
2. Recreate 10 highest-priority workflows in n8n (1 week)
3. Parallel run critical workflows (2 weeks validation)
4. Migrate remaining workflows (2 weeks)
5. Decommission Zapier (immediate)

**Total Migration Time:** 6 weeks (staggered approach, not blocking)

---

### KhaosForge (GitHub Replacement)

**Technology Stack:**
- **Git Server:** Gitea (lightweight GitHub alternative)
- **CI/CD:** Woodpecker CI (GitLab CI-compatible)
- **Hosting:** GKE cluster or dedicated VM
- **Mirror:** Existing GitHub repos as mirror (not primary)

**Feature Parity:**

| Feature | GitHub | KhaosForge (Gitea) | Status |
|---------|--------|-------------------|--------|
| **Git hosting** | ✅ | ✅ | Ready |
| **Pull requests** | ✅ | ✅ | Ready |
| **Issues** | ✅ | ✅ | Ready |
| **Projects** | ✅ | ✅ Kanban boards | Ready |
| **CI/CD** | ✅ Actions | ✅ Woodpecker | Ready |
| **Packages** | ✅ | ✅ Package registry | Ready |
| **Wiki** | ✅ | ✅ | Ready |

**Migration Plan:**
1. Deploy Gitea + Woodpecker on GKE (1 day)
2. Mirror all repositories to Gitea (automated, 4 hours)
3. Convert GitHub Actions to Woodpecker CI (1 week)
4. Update remote URLs in local clones (1 hour)
5. Parallel run (1 month validation)
6. Make Gitea primary, GitHub mirror (immediate)

**Total Migration Time:** 2 weeks active work + 1 month validation = **6 weeks**

**Note:** Keep GitHub as public mirror for discoverability, but Gitea is source of truth

---

### KhaosComms (Discord/Slack Replacement)

**Technology Stack:**
- **Server:** Matrix (federated protocol)
- **Client:** Element (web, desktop, mobile)
- **Bridge:** Matrix-Discord bridge (during transition)
- **Hosting:** Synapse server on GKE or dedicated VM

**Feature Parity:**

| Feature | Discord | KhaosComms (Matrix) | Status |
|---------|---------|---------------------|--------|
| **Text chat** | ✅ | ✅ | Ready |
| **Voice/video** | ✅ | ✅ Jitsi integration | Ready |
| **Bots** | ✅ | ✅ Matrix bot SDK | Ready |
| **Webhooks** | ✅ | ✅ Appservices | Ready |
| **File sharing** | ✅ | ✅ | Ready |
| **Threads** | ✅ | ✅ | Ready |
| **E2E encryption** | ❌ | ✅ | Better |

**Migration Plan:**
1. Deploy Synapse (Matrix server) on GKE (1 day)
2. Setup Matrix-Discord bridge (1 day)
3. Mirror Discord channels to Matrix (automated)
4. Migrate bots to Matrix SDK (2 weeks)
5. Parallel run (1 month)
6. Deprecate Discord (gradual)

**Total Migration Time:** 3 weeks active work + 1 month validation = **7 weeks**

**Note:** Low priority (Discord free tier is sufficient for now)

---

### KhaosDocs (Notion Replacement)

**Technology Stack:**
- **Server:** Outline (open-source Notion alternative)
- **Database:** PostgreSQL (shared with KhaosBase)
- **Storage:** S3-compatible (Google Cloud Storage)
- **Hosting:** GKE cluster

**Feature Parity:**

| Feature | Notion | KhaosDocs (Outline) | Status |
|---------|--------|---------------------|--------|
| **Rich text editor** | ✅ | ✅ Markdown | Ready |
| **Hierarchical docs** | ✅ | ✅ Collections | Ready |
| **Collaboration** | ✅ | ✅ Real-time | Ready |
| **Search** | ✅ | ✅ Full-text | Ready |
| **API access** | ✅ | ✅ REST API | Ready |
| **Templates** | ✅ | ✅ | Ready |

**Migration Plan:**
1. Export all Notion pages to Markdown (automated, 2 hours)
2. Deploy Outline on GKE (1 day)
3. Import Markdown files (4 hours)
4. Recreate collection structure (1 day)
5. Validate content (2 days)
6. Cutover (immediate)

**Total Migration Time:** 1 week

**Note:** Low priority (most knowledge already in Obsidian)

---

### KhaosPay (Stripe Replacement)

**Technology Stack:**
- **Option 1:** Direct BaaS integration (Thread Bank, NFCU)
- **Option 2:** BTCPay Server (crypto-only)
- **Option 3:** Keep Stripe (lowest priority to replace)

**Feature Parity:**

| Feature | Stripe | KhaosPay (BaaS) | Status |
|---------|--------|-----------------|--------|
| **Card processing** | ✅ | ✅ Thread Bank API | Ready |
| **ACH transfers** | ✅ | ✅ BaaS direct | Ready |
| **Crypto payments** | ❌ | ✅ BTCPay | Better |
| **Invoicing** | ✅ | 🔄 Custom build | Pending |
| **Subscriptions** | ✅ | 🔄 Custom build | Pending |

**Migration Plan:**
1. Research BaaS providers (1 week)
2. Build custom payment gateway (4 weeks)
3. Migrate customer billing data (1 week)
4. Parallel run (1 month validation)
5. Cutover (gradual by customer)

**Total Migration Time:** 10 weeks

**Note:** Lowest priority (transaction fees are acceptable for now)

---

## MIGRATION TIMELINE

### Phase 1: Critical Infrastructure (Q1-Q2 2026)

**Priority:** Eliminate high-risk vendor lock-in

| Quarter | Milestone | Deliverable | Status |
|---------|-----------|-------------|--------|
| **Q1 2026** | KhaosBase deployment | Airtable replacement operational | 🚧 In Progress |
| **Q1 2026** | CPA Sentinel migration | Compliance data moved to KhaosBase | 📋 Planned |
| **Q2 2026** | KhaosFlow deployment | Zapier replacement operational | 📋 Planned |
| **Q2 2026** | Email monitoring migration | All zaps converted to n8n workflows | 📋 Planned |
| **Q2 2026** | Vendor cancellation | Airtable + Zapier cancelled | 📋 Planned |

**Success Metrics:**
- ✅ Zero data loss during migration
- ✅ <1 hour downtime for each service
- ✅ Cost savings: $480/year

---

### Phase 2: Development Tools (Q3-Q4 2026)

**Priority:** Establish sovereign development infrastructure

| Quarter | Milestone | Deliverable | Status |
|---------|-----------|-------------|--------|
| **Q3 2026** | KhaosForge deployment | Gitea + Woodpecker CI operational | 📐 Designed |
| **Q3 2026** | Repository migration | All repos mirrored to Gitea | 📋 Planned |
| **Q4 2026** | CI/CD migration | GitHub Actions → Woodpecker | 📋 Planned |
| **Q4 2026** | KhaosComms deployment | Matrix server operational | 📋 Planned |
| **Q4 2026** | Bot migration | Discord bots → Matrix bots | 📋 Planned |

**Success Metrics:**
- ✅ All repositories accessible on Gitea
- ✅ CI/CD pipelines functional
- ✅ Matrix chat feature parity with Discord

---

### Phase 3: Collaboration & Finance (Q1-Q2 2027)

**Priority:** Complete vendor independence

| Quarter | Milestone | Deliverable | Status |
|---------|-----------|-------------|--------|
| **Q1 2027** | KhaosDocs deployment | Outline documentation server | 📋 Planned |
| **Q1 2027** | Documentation migration | Notion → Outline | 📋 Planned |
| **Q2 2027** | KhaosPay research | BaaS provider selection | 💭 Conceptual |
| **Q2 2027** | Payment gateway build | Custom billing system | 💭 Conceptual |
| **Q2 2027** | Complete independence | All vendors eliminated | 📋 Planned |

**Success Metrics:**
- ✅ 100% vendor independence achieved
- ✅ Total cost savings: $1,000+/year
- ✅ Zero vendor lock-in risks

---

## IMPLEMENTATION DETAILS

### KhaosBase Technical Architecture

```yaml
khaosbase:
  database:
    engine: "PostgreSQL 16"
    hosting: "GKE cluster (jarvis-swarm-personal-001)"
    storage: "100GB persistent volume"
    backup:
      frequency: "Daily"
      retention: "30 days"
      destination: "Google Cloud Storage"
  
  ui_layer:
    primary: "NocoDB"
    alternative: "Baserow"
    deployment: "Docker container on GKE"
    config: "Environment variables (secrets in Vault)"
  
  access_control:
    authentication: "OAuth2 + local accounts"
    authorization: "RBAC (NocoDB built-in)"
    audit_log: "PostgreSQL audit extension"
  
  api:
    rest: "NocoDB REST API"
    graphql: "NocoDB GraphQL"
    custom: "PostgreSQL direct connection (read-only views)"
  
  monitoring:
    metrics: "Prometheus (PostgreSQL exporter)"
    logs: "Loki (centralized logging)"
    alerts: "Grafana (downtime, slow queries)"
```

---

### KhaosFlow Technical Architecture

```yaml
khaosflow:
  workflow_engine:
    primary: "n8n"
    alternative: "Temporal.io (code-first)"
    deployment: "Docker container on GKE"
    persistence: "PostgreSQL (workflow state)"
  
  integrations:
    email: "IMAP/POP3/SMTP"
    databases: "PostgreSQL, MySQL, MongoDB"
    http: "REST API calls, webhooks"
    custom: "JavaScript/TypeScript functions"
  
  scheduling:
    cron: "Built-in scheduler"
    webhooks: "Instant trigger"
    manual: "API-triggered workflows"
  
  error_handling:
    retry: "Exponential backoff"
    alerting: "Discord/Matrix notifications"
    logging: "Loki (centralized)"
  
  backup:
    workflows: "Git repository (YAML export)"
    state: "PostgreSQL backup"
    frequency: "Continuous (Git push on change)"
```

---

### KhaosForge Technical Architecture

```yaml
khaosforge:
  git_server:
    engine: "Gitea"
    deployment: "GKE cluster or dedicated VM"
    storage: "500GB persistent volume"
    backup: "Daily Git bundle export"
  
  ci_cd:
    engine: "Woodpecker CI"
    deployment: "Docker container on GKE"
    runners: "Kubernetes pods (ephemeral)"
    pipelines: "YAML-based (similar to GitLab CI)"
  
  registry:
    docker: "Docker registry (built-in Gitea)"
    npm: "Verdaccio (separate deployment)"
    pypi: "devpi (separate deployment)"
  
  access_control:
    authentication: "OAuth2 + local accounts"
    authorization: "Organizations, teams, repos"
    ssh_keys: "Per-user SSH key management"
  
  monitoring:
    metrics: "Prometheus (Gitea exporter)"
    logs: "Loki (centralized)"
    alerts: "Grafana (disk space, uptime)"
```

---

## RISK MITIGATION

### Data Loss Prevention

**Strategy:**
1. **Parallel Run:** Maintain old vendor during migration (1-4 weeks)
2. **Automated Validation:** Compare record counts, checksums
3. **Rollback Plan:** Keep vendor account active for 30 days post-migration
4. **Backup Everything:** Daily exports from both old and new systems

**Validation Script:**
```bash
#!/bin/bash
# Compare Airtable vs KhaosBase data integrity

AIRTABLE_COUNT=$(curl -s "https://api.airtable.com/v0/..." | jq '.records | length')
KHAOSBASE_COUNT=$(psql -t -c "SELECT COUNT(*) FROM compliance_table")

if [ "$AIRTABLE_COUNT" != "$KHAOSBASE_COUNT" ]; then
  echo "ERROR: Record count mismatch"
  echo "Airtable: $AIRTABLE_COUNT"
  echo "KhaosBase: $KHAOSBASE_COUNT"
  exit 1
fi

echo "✅ Data integrity verified"
```

---

### Downtime Minimization

**Strategy:**
1. **Deploy First:** New system operational before cutover
2. **DNS Cutover:** Instant switch (or load balancer routing)
3. **Rollback Ready:** One command to revert if issues detected
4. **Off-Hours Migration:** Schedule during low-usage periods

**Downtime Budget:** <1 hour per service

---

### Feature Gap Analysis

**Process:**
1. **Inventory Current Usage:** Document all features used in vendor
2. **Map to Replacement:** Verify feature parity in sovereign tool
3. **Build Custom:** If gap exists, build missing feature before migration
4. **User Testing:** Validate workflows with actual usage

**Example (Airtable → KhaosBase):**

| Airtable Feature | Usage | KhaosBase Equivalent | Gap? |
|------------------|-------|----------------------|------|
| Relational tables | Heavy | PostgreSQL foreign keys | ✅ No |
| Forms | Medium | NocoDB forms | ✅ No |
| Views | Heavy | NocoDB views | ✅ No |
| Automations | Light | KhaosFlow (n8n) | ⚠️ Dependency |
| Calendar view | None | N/A | ✅ No gap |

**Result:** One dependency (KhaosFlow must deploy before KhaosBase automations)

---

### Skill Gap Training

**Strategy:**
1. **Documentation:** Write deployment guides for each replacement
2. **Testing:** Deploy in staging environment first
3. **Familiarization:** Use new tool for 1 week before migration
4. **Support:** Keep vendor documentation accessible during transition

**Training Time Budget:** 1 week per major system (KhaosBase, KhaosFlow, KhaosForge)

---

## SUCCESS METRICS

### Cost Savings

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Annual subscription savings** | $1,000+/year | Vendor invoices (before) vs $0 (after) |
| **Transaction fee savings** | $200-500/year | Stripe fees eliminated (if KhaosPay deployed) |
| **Infrastructure cost** | +$20/month | GKE cluster expansion for self-hosted tools |
| **Net savings** | $700-1,200/year | Total savings minus infrastructure increase |

---

### Data Sovereignty

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Data portability** | <24hr export | Time to full database dump + attachments |
| **Vendor dependencies** | 0 critical | No vendors with proprietary data formats |
| **Open source ratio** | 100% | All tools are open-source or self-built |
| **Migration capability** | <1 week | Time to migrate any service to new provider |

---

### Operational Resilience

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Uptime** | 99.9%+ | Prometheus metrics (uptime percentage) |
| **Backup frequency** | Daily | Automated backup logs |
| **Recovery time** | <1 hour | Test restore from backup (quarterly) |
| **Feature parity** | 100% | All current workflows operational |

---

## CONTINGENCY PLANS

### Scenario 1: Migration Failure

**Trigger:** Data integrity issues, critical feature gaps, unacceptable downtime

**Response:**
1. Revert to vendor immediately (DNS change or load balancer)
2. Analyze failure cause (data corruption? feature gap? performance?)
3. Fix issue in staging environment
4. Retry migration after 2-4 weeks

**Fallback:** Keep vendor account active for 30 days minimum

---

### Scenario 2: Vendor Price Increase

**Trigger:** Vendor raises prices mid-migration

**Response:**
1. Accelerate migration timeline (work overtime if needed)
2. Negotiate with vendor for short-term discount/freeze
3. Accept price increase temporarily if migration <2 months away
4. Communicate cost impact to stakeholders

**Decision Criteria:** If price doubles, immediately prioritize that vendor

---

### Scenario 3: Sovereign Tool Abandonment

**Trigger:** NocoDB, n8n, or Gitea project discontinued

**Response:**
1. Fork project immediately (open-source advantage)
2. Maintain critical security patches ourselves
3. Evaluate alternative tools (Baserow vs NocoDB, Temporal vs n8n)
4. Migrate to alternative if fork is unsustainable

**Prevention:** Choose tools with active communities (1,000+ GitHub stars)

---

## CONCLUSION

The Vendor Elimination Roadmap achieves complete sovereignty by Q2 2027 through systematic replacement of all vendor dependencies with open-source, self-hosted alternatives.

**Key Benefits:**
- 💰 **Cost Savings:** $700-1,200/year recurring savings
- 🔓 **Zero Lock-in:** 100% data portability, <1 week migration capability
- 🛡️ **Resilience:** Self-hosted infrastructure, no vendor outage risk
- 🚀 **Innovation:** Full control over features and roadmap

**Success Factors:**
- ✅ Parallel run during migration (minimize risk)
- ✅ Automated validation (ensure data integrity)
- ✅ Staged rollout (one vendor at a time)
- ✅ Documentation (knowledge transfer for future)

**Next Steps:**
1. Begin KhaosBase deployment (Q1 2026)
2. Document current Airtable workflows (1 week)
3. Setup PostgreSQL + NocoDB on GKE (1 day)
4. Initiate data migration process (2 weeks)

---

**Document Approved By:** AI Board (4/5 + Human)  
**Implementation Owner:** Domenic Garza (Blue Team)  
**Review Frequency:** Quarterly  
**Next Review:** March 31, 2026

---

*"True sovereignty is not independence from all tools—it's the ability to change any tool without disrupting the mission."*
