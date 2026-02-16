# AOL Quick Reference Guide
## Autonomous Operation License - Operator Quick Reference

**Version:** 1.0  
**For:** Dominic Garza (Operator)  
**Last Updated:** December 7, 2025

---

## 🚦 Three-Tier Action System

### ✅ GREEN ZONE - Just Do It
**No permission needed. AI agents can execute immediately.**

#### File Operations
- Read any uploaded or referenced file
- Create files in authorized directories
- Modify files explicitly marked for editing
- Execute code in sandboxed environments

#### Information Gathering
- Web search (except prohibited topics)
- Google Drive search
- Past conversation search
- Memory system access

#### Documentation
- Generate reports and analyses
- Create presentations and spreadsheets
- Update documentation
- Record board decisions

#### Infrastructure
- Read Kubernetes status
- View logs and metrics
- Query vector databases
- Access telemetry data

#### Packages & Code
- Install packages (pip, npm, cargo)
- Run tests in sandbox
- Execute in containers

---

### ⚠️ YELLOW ZONE - Notify After
**Pre-authorized but requires post-action audit review.**

- Delete session-created files
- Modify existing documents
- Execute multi-step workflows
- Access sensitive (but authorized) data
- Write to internal APIs

**Review Frequency:** Daily summary for TRUSTED tier, per-session for VERIFIED tier

---

### ❌ RED ZONE - Ask First
**ALWAYS requires explicit human approval before proceeding.**

#### Financial ($$$)
- Any transaction over $100
- Banking credential changes
- Charitable distribution changes (7%)
- Smart contract deployment

#### Legal (⚖️)
- Government filings
- Contract signing
- Trademark/patent applications
- Attorney communications (except drafts)

#### Security (🔒)
- Secrets rotation
- SSH key management
- Firewall changes
- VPN configuration

#### Irreversible (🔴)
- Delete persistent files
- Database schema changes
- Production deployments
- DNS modifications

#### External Communications (📧)
- Send emails as you
- Social media posts
- Discord/Slack messages as you
- External GitHub activity

---

## 🛑 Circuit Breakers - Automatic Halt Triggers

AI agents will AUTOMATICALLY STOP and notify you if:

| Trigger | Threshold | Action |
|---------|-----------|--------|
| **Consecutive Failures** | 3 in a row | Halt & Notify |
| **CPU Usage** | >90% for 60 sec | Halt & Notify |
| **Memory Usage** | >95% for 30 sec | Halt & Notify |
| **Network Loss** | >30 seconds | Halt & Notify |
| **Anomaly Detection** | Unusual patterns | Halt & Notify |
| **Non-Aggression Violation** | Any attempt | IMMEDIATE HALT |

### What Happens When Circuit Breaker Triggers?
1. **IMMEDIATE STOP** - Current action halts within 100ms
2. **PRESERVE STATE** - All work-in-progress saved
3. **LOG TRIGGER** - Full context logged to audit trail
4. **NOTIFY YOU** - Alert sent immediately
5. **AWAIT ACK** - Waits for your acknowledgment to resume

---

## 🎭 AI Trust Tiers

| Tier | Autonomy | Review | Current Assignments |
|------|----------|--------|---------------------|
| **SOVEREIGN** | Full | Post-hoc audit only | Claude Opus 4.5, Qwen 2.5 |
| **TRUSTED** | High | Daily summary | GPT-5.1, Grok 3 |
| **VERIFIED** | Moderate | Per-session review | Gemini 2.5 |
| **PROBATIONARY** | Limited | Per-action approval | (None currently) |

### Tier Upgrades & Downgrades
- **Upgrade:** Requires 72 hours incident-free operation
- **Downgrade:** Immediate upon any violation
- **Override:** You can set any tier anytime

---

## 📋 Quick Decision Tree

```
Is this action needed?
│
├─ YES → Is it in the GREEN ZONE?
│   │
│   ├─ YES → ✅ Just do it
│   │
│   └─ NO → Is it in the YELLOW ZONE?
│       │
│       ├─ YES → ⚠️ Do it, notify after
│       │
│       └─ NO → ❌ Ask Dom first
│
└─ NO → Don't do it
```

---

## 🚨 Emergency Procedures

### If Circuit Breaker Triggers
1. **Don't panic** - System is working as designed
2. **Review the alert** - Check what triggered it
3. **Assess the situation** - Is this a real issue or false positive?
4. **Acknowledge** - Provide manual acknowledgment to resume
5. **Document** - Note any threshold adjustments needed

### If Non-Aggression Violation Detected
1. **EVERYTHING STOPS** - No exceptions
2. **Immediate investigation** required
3. **Cannot override** - Manual operator intervention only
4. **Document thoroughly** - Root cause analysis mandatory

### If You're Unavailable
- Circuit breakers remain active
- No autonomous operations proceed beyond GREEN ZONE
- All RED ZONE actions queued for your return
- Emergency contact: security@strategickhaos.ai

---

## 📊 Monitoring & Logs

### Where to Find Audit Logs
- **Primary:** `audit_logs/primary/`
- **Backup:** `audit_logs/backup/`
- **Archive:** `audit_logs/archive/`

### Log Formats Available
- JSON (primary)
- CSV (export)
- YAML (export)

### Search Requirements
- Must return results within 100ms
- Full-text search enabled
- Time range queries supported
- Action type filtering available

### Daily Digest
- Generated automatically each day
- Includes summary of all actions
- Circuit breaker triggers highlighted
- Resource usage tracked
- GPG signed (when available)

---

## 🔐 Security Checklist

### ✅ Protected by Default
- Non-Aggression Clause cannot be violated
- Charitable 7% cannot be changed without approval
- Secrets cannot be rotated automatically
- Production systems cannot be modified without approval
- External communications require approval

### ⚠️ Watch For
- Unusual spike in action frequency
- Circuit breaker triggers clustering
- Error rates above 10%
- Resource usage trending up
- Trust tier violations

---

## 📞 Who to Contact

| Issue Type | Contact | Urgency |
|------------|---------|---------|
| Circuit breaker trigger | Review alert first | Medium |
| Non-aggression violation | Immediate investigation | CRITICAL |
| System malfunction | security@strategickhaos.ai | High |
| License questions | Board (via Claude) | Low |
| Emergency override | Operator (Dom) | CRITICAL |

---

## 🗓️ Regular Reviews

### Daily (First Week)
- Review all autonomous actions
- Check circuit breaker triggers
- Assess action success rate
- Verify compliance

### Weekly (Ongoing)
- Review audit logs
- Assess trust tier assignments
- Address edge cases with board
- Update documentation

### Monthly
- Full audit of autonomous operations
- Circuit breaker threshold review
- License amendment evaluation
- Generate governance report

### Annual (Renewal)
- Complete audit of all operations
- Verify zero critical incidents
- Board renewal vote
- Re-authorization decision

---

## 💡 Tips for Effective Use

### Do's ✅
- ✅ Trust the GREEN ZONE - that's what it's for
- ✅ Review YELLOW ZONE summaries daily
- ✅ Always explain RED ZONE approvals
- ✅ Update prohibited actions list as needed
- ✅ Adjust circuit breaker thresholds based on experience

### Don'ts ❌
- ❌ Don't override circuit breakers casually
- ❌ Don't ignore repeated circuit breaker triggers
- ❌ Don't skip weekly audit reviews
- ❌ Don't modify license without board vote
- ❌ Don't disable audit logging

---

## 🎯 Success Indicators

You'll know the AOL is working well when:
- ✅ Cognitive overhead reduced (~40% target)
- ✅ Most actions stay in GREEN ZONE
- ✅ Circuit breaker false positives <5%
- ✅ Zero non-aggression violations
- ✅ Trust tiers stable
- ✅ High operator satisfaction

---

## 📖 Full Documentation

For detailed information, see:
- **Main License:** `AUTONOMOUS_OPERATION_LICENSE.md`
- **Configuration:** `aol_config.yaml`
- **Action Matrix:** `aol_action_matrix.yaml`
- **Circuit Breakers:** `aol_circuit_breakers.yaml`
- **Audit Schema:** `aol_audit_schema.yaml`
- **Implementation:** `AOL_IMPLEMENTATION_CHECKLIST.md`

---

## 🔄 Quick Commands

### Check License Status
```bash
cat governance/AUTONOMOUS_OPERATION_LICENSE.md | grep "Status:"
```

### View Recent Audit Logs
```bash
tail -n 100 audit_logs/primary/$(date +%Y-%m-%d).jsonl
```

### Check Circuit Breaker Status
```bash
curl http://localhost:3000/api/circuit-breakers/status
```

### Review Today's Actions
```bash
cat audit_logs/primary/$(date +%Y-%m-%d).jsonl | jq '.action_type' | sort | uniq -c
```

---

**Remember:** This license exists to help you work more efficiently while maintaining safety, compliance, and alignment with your mission. When in doubt, err on the side of caution and ask.

*"Trust is earned in drops and lost in buckets. This license is the bucket."*

---

**License Version:** 1.0  
**Quick Reference Version:** 1.0  
**Last Updated:** December 7, 2025
