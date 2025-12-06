# Security Policy

## SovereignGuard Security Framework

This repository is protected by **SovereignGuard**, an automated security orchestration system that addresses 36 identified security exposure vectors through defense-in-depth architecture.

### Security Modules

| Module | Status | Exposures Addressed |
| ------ | ------ | ------------------- |
| Credential Vault | ✅ Active | #1-#6 |
| Service Mesh | ✅ Active | #7, #8, #19-#21, #24 |
| Financial Enclave | 🔄 Design | #11, #12, #17, #25, #30 |
| Air-Gap Inference | 🔄 Design | #13-#16, #26 |
| Immutable Audit | ✅ Prototype | #9, #10, #22, #23, #27 |
| Chaos Testing | 🔄 Design | #18, #28, #29 |

For detailed security architecture, see [SOVEREIGNGUARD.md](SOVEREIGNGUARD.md).

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 5.1.x   | :white_check_mark: |
| 5.0.x   | :x:                |
| 4.0.x   | :white_check_mark: |
| < 4.0   | :x:                |

## Reporting a Vulnerability

### Responsible Disclosure

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly:

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. **Email**: security@strategickhaos.internal (or use GitHub Security Advisories)
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

| Severity | Initial Response | Resolution Target |
| -------- | ---------------- | ----------------- |
| Critical | 4 hours | 24 hours |
| High | 24 hours | 7 days |
| Medium | 48 hours | 30 days |
| Low | 7 days | 90 days |

### What to Expect

- **Acknowledgment**: Within the initial response time
- **Investigation**: We'll investigate and determine severity
- **Updates**: Regular updates on remediation progress
- **Credit**: Public acknowledgment (if desired) after fix is deployed

## Security Best Practices

### For Contributors

1. **Never commit secrets** - Use Vault for all credentials
2. **Sign commits** - Use GPG signing for all commits
3. **Review dependencies** - Check for vulnerabilities before adding
4. **Follow least privilege** - Request minimum necessary permissions

### For Operators

1. **Enable audit logging** - All security events must be logged
2. **Rotate secrets regularly** - Follow the rotation schedule in Vault
3. **Monitor alerts** - React to security alerts within SLA
4. **Test recovery** - Participate in chaos engineering exercises

## Security Contacts

- **Security Team**: security@strategickhaos.internal
- **Discord**: #security-alerts channel
- **On-call**: See internal runbook for escalation

## Compliance

This project maintains compliance with:
- SOC 2 Type II (in progress)
- ISO 27001 (planned)
- NIST Cybersecurity Framework
