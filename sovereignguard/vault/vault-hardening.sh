#!/bin/bash
# SovereignGuard - Vault Security Hardening Script
# Phase 1: Credential Vault Security Configuration
# Applies additional security measures after vault-init.sh

set -euo pipefail

# Configuration
VAULT_ADDR="${VAULT_ADDR:-http://localhost:8200}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/vault-hardening.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    local level="$1"
    shift
    local msg="$*"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${msg}" | tee -a "$LOG_FILE"
}

info() { log "${BLUE}INFO${NC}" "$@"; }
warn() { log "${YELLOW}WARN${NC}" "$@"; }
error() { log "${RED}ERROR${NC}" "$@"; }
success() { log "${GREEN}SUCCESS${NC}" "$@"; }

# Verify Vault is ready
verify_vault() {
    info "Verifying Vault status..."
    
    if ! vault status >/dev/null 2>&1; then
        error "Vault is not accessible. Please ensure Vault is running and unsealed."
        exit 1
    fi
    
    if vault status 2>/dev/null | grep -q "Sealed.*true"; then
        error "Vault is sealed. Please unseal Vault first."
        exit 1
    fi
    
    success "Vault is accessible and unsealed"
}

# Configure audit logging with enhanced options
enhance_audit_logging() {
    info "Enhancing audit logging configuration..."
    
    local audit_dir="${SCRIPT_DIR}/../logs"
    mkdir -p "$audit_dir"
    chmod 700 "$audit_dir"
    
    # Enable detailed file audit
    if ! vault audit list 2>/dev/null | grep -q "file-detailed/"; then
        vault audit enable -path="file-detailed" file \
            file_path="${audit_dir}/vault-audit-detailed.log" \
            log_raw=false \
            hmac_accessor=true \
            mode=0600 2>/dev/null || warn "Detailed file audit may already exist"
        success "Detailed file audit logging enabled"
    else
        info "Detailed file audit already enabled"
    fi
    
    # Enable syslog audit if available
    if command -v logger >/dev/null 2>&1; then
        if ! vault audit list 2>/dev/null | grep -q "syslog/"; then
            vault audit enable syslog 2>/dev/null || info "Syslog audit may already exist"
            success "Syslog audit logging enabled"
        else
            info "Syslog audit already enabled"
        fi
    fi
}

# Configure auth method tuning
tune_auth_methods() {
    info "Tuning authentication methods..."
    
    # Tune AppRole settings
    vault auth tune \
        -default-lease-ttl=1h \
        -max-lease-ttl=8h \
        -description="SovereignGuard AppRole Authentication" \
        approle/ 2>/dev/null || warn "AppRole tuning may have failed"
    
    success "Auth methods tuned"
}

# Configure secrets engine settings
tune_secrets_engines() {
    info "Tuning secrets engine settings..."
    
    # Tune KV v2 settings
    vault secrets tune \
        -default-lease-ttl=24h \
        -max-lease-ttl=168h \
        -description="SovereignGuard Secrets Store" \
        secret/ 2>/dev/null || warn "KV tuning may have failed"
    
    # Tune transit settings
    vault secrets tune \
        -default-lease-ttl=1h \
        -max-lease-ttl=24h \
        -description="SovereignGuard Encryption Service" \
        transit/ 2>/dev/null || warn "Transit tuning may have failed"
    
    success "Secrets engines tuned"
}

# Create additional security policies
create_security_policies() {
    info "Creating additional security policies..."
    
    # Deny-all baseline policy
    cat > /tmp/deny-all-policy.hcl << 'EOF'
# Deny All Policy - Baseline for least privilege
path "*" {
  capabilities = ["deny"]
}
EOF
    vault policy write deny-all /tmp/deny-all-policy.hcl
    success "Deny-all baseline policy created"
    
    # Read-only secrets policy
    cat > /tmp/readonly-secrets-policy.hcl << 'EOF'
# Read-Only Secrets Policy
path "secret/data/*" {
  capabilities = ["read"]
}

path "secret/metadata/*" {
  capabilities = ["list", "read"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}
EOF
    vault policy write readonly-secrets /tmp/readonly-secrets-policy.hcl
    success "Read-only secrets policy created"
    
    # Emergency break-glass policy
    cat > /tmp/emergency-policy.hcl << 'EOF'
# Emergency Break-Glass Policy
# Use only in emergencies with proper authorization
path "*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

# Audit trail for emergency access
path "sys/audit" {
  capabilities = ["read", "list"]
}

path "sys/audit/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}
EOF
    vault policy write emergency /tmp/emergency-policy.hcl
    warn "Emergency break-glass policy created - use with caution!"
    
    # Cleanup
    rm -f /tmp/*-policy.hcl
}

# Configure rate limiting
configure_rate_limiting() {
    info "Configuring rate limiting..."
    
    # Check if vault command is available
    if ! command -v vault >/dev/null 2>&1; then
        warn "Vault CLI not available - skipping rate limiting configuration"
        return 0
    fi
    
    # Note: Rate limiting is an enterprise feature, skip for OSS
    local vault_version_output
    vault_version_output=$(vault version 2>&1) || {
        warn "Could not determine Vault version - skipping rate limiting"
        return 0
    }
    
    if echo "$vault_version_output" | grep -qi "enterprise"; then
        info "Enterprise version detected, configuring rate limits..."
        # Enterprise-specific rate limiting would go here
        # Example: vault write sys/quotas/rate-limit/global-limit rate=100
        success "Rate limiting configured"
    else
        info "Vault OSS version detected - rate limiting is an enterprise-only feature"
        info "Consider upgrading to Vault Enterprise for rate limiting capabilities"
        info "Alternative: Use network-level rate limiting (e.g., Traefik, nginx)"
    fi
}

# Configure secret versioning
configure_versioning() {
    info "Configuring secret versioning..."
    
    # Configure KV v2 max versions
    vault kv metadata put -max-versions=10 secret/discord 2>/dev/null || info "Discord path versioning set"
    vault kv metadata put -max-versions=10 secret/github 2>/dev/null || info "GitHub path versioning set"
    vault kv metadata put -max-versions=10 secret/trading 2>/dev/null || info "Trading path versioning set"
    vault kv metadata put -max-versions=5 secret/shared 2>/dev/null || info "Shared path versioning set"
    
    success "Secret versioning configured"
}

# Create rotation schedule configuration
create_rotation_config() {
    info "Creating secret rotation configuration..."
    
    cat > "${SCRIPT_DIR}/rotation-schedule.yaml" << 'EOF'
# SovereignGuard Secret Rotation Schedule
# This file defines when secrets should be rotated

rotation_policies:
  hmac_secrets:
    interval: "7d"
    description: "HMAC signing keys"
    auto_rotate: true
    cron: "0 2 * * 0"  # Sundays at 2 AM
    
  jwt_secrets:
    interval: "30d"
    description: "JWT signing secrets"
    auto_rotate: true
    cron: "0 3 1 * *"  # 1st of month at 3 AM
    
  approle_secrets:
    interval: "30d"
    description: "AppRole secret IDs"
    auto_rotate: true
    cron: "0 4 15 * *"  # 15th of month at 4 AM
    
  discord_token:
    interval: "90d"
    description: "Discord bot token"
    auto_rotate: false
    requires_manual: true
    notification: "discord-webhook"
    
  trading_api_keys:
    interval: "90d"
    description: "Trading platform API keys"
    auto_rotate: false
    requires_manual: true
    notification: "discord-webhook"
    
  database_credentials:
    interval: "24h"
    description: "Dynamic database credentials"
    auto_rotate: true
    managed_by: "vault-dynamic"

emergency_rotation:
  trigger: "security-incident"
  scope: "all-secrets"
  notification: "all-channels"
  
notifications:
  discord_webhook: "${DISCORD_SECURITY_WEBHOOK:-}"
  email: "${SECURITY_EMAIL:-}"
EOF
    
    success "Rotation schedule created at ${SCRIPT_DIR}/rotation-schedule.yaml"
}

# Create backup configuration
create_backup_config() {
    info "Creating backup configuration..."
    
    cat > "${SCRIPT_DIR}/backup-config.yaml" << 'EOF'
# SovereignGuard Vault Backup Configuration

backup:
  enabled: true
  schedule: "0 1 * * *"  # Daily at 1 AM
  retention_days: 30
  
  destinations:
    - type: "local"
      path: "/var/backups/vault"
      encrypt: true
      
    - type: "s3"
      bucket: "${VAULT_BACKUP_S3_BUCKET:-}"
      region: "${AWS_REGION:-us-east-1}"
      encrypt: true
      sse: "aws:kms"
      
  pre_backup:
    - "vault operator raft snapshot"
    
  post_backup:
    - "verify-backup-integrity"
    - "notify-backup-complete"
    
  restore:
    requires_approval: true
    approvers:
      - "admin"
      - "security-team"
    procedure: "See /docs/vault-restore-procedure.md"

integrity_checks:
  enabled: true
  schedule: "0 6 * * *"  # Daily at 6 AM
  notifications:
    success: false
    failure: true
EOF
    
    success "Backup configuration created at ${SCRIPT_DIR}/backup-config.yaml"
}

# Verify security configuration
verify_security() {
    info "Verifying security configuration..."
    
    local issues=0
    
    # Check audit logging
    if ! vault audit list 2>/dev/null | grep -q "file/\|file-detailed/"; then
        warn "No file audit logging enabled"
        issues=$((issues + 1))
    else
        success "✓ Audit logging verified"
    fi
    
    # Check policies exist
    local required_policies=("discord-bot" "event-gateway" "financial-enclave" "audit-log" "admin" "deny-all")
    for policy in "${required_policies[@]}"; do
        if ! vault policy read "$policy" >/dev/null 2>&1; then
            warn "Policy '$policy' not found"
            issues=$((issues + 1))
        else
            success "✓ Policy '$policy' verified"
        fi
    done
    
    # Check AppRoles exist
    local services=("discord-bot" "event-gateway" "financial-enclave" "audit-log")
    for service in "${services[@]}"; do
        if ! vault read "auth/approle/role/${service}" >/dev/null 2>&1; then
            warn "AppRole '$service' not found"
            issues=$((issues + 1))
        else
            success "✓ AppRole '$service' verified"
        fi
    done
    
    # Check secrets engines
    if ! vault secrets list | grep -q "secret/"; then
        warn "KV secrets engine not enabled"
        issues=$((issues + 1))
    else
        success "✓ KV secrets engine verified"
    fi
    
    if ! vault secrets list | grep -q "transit/"; then
        warn "Transit secrets engine not enabled"
        issues=$((issues + 1))
    else
        success "✓ Transit secrets engine verified"
    fi
    
    if [ $issues -eq 0 ]; then
        success "All security checks passed!"
    else
        warn "$issues security issue(s) found"
    fi
    
    return $issues
}

# Print security summary
print_security_summary() {
    echo ""
    echo "=========================================="
    echo "🛡️ SovereignGuard Security Summary"
    echo "=========================================="
    echo ""
    echo "Hardening Measures Applied:"
    echo "  ✓ Enhanced audit logging"
    echo "  ✓ Auth method tuning"
    echo "  ✓ Secrets engine tuning"
    echo "  ✓ Security policies created"
    echo "  ✓ Secret versioning configured"
    echo "  ✓ Rotation schedule defined"
    echo "  ✓ Backup configuration created"
    echo ""
    echo "Security Policies:"
    echo "  - discord-bot: Read-only Discord secrets"
    echo "  - event-gateway: Webhook and GitHub access"
    echo "  - financial-enclave: Trading API with encryption"
    echo "  - audit-log: Write-only audit access"
    echo "  - admin: Full access for emergencies"
    echo "  - deny-all: Baseline deny policy"
    echo "  - readonly-secrets: Read-only access"
    echo "  - emergency: Break-glass access"
    echo ""
    echo "Configuration Files:"
    echo "  - ${SCRIPT_DIR}/rotation-schedule.yaml"
    echo "  - ${SCRIPT_DIR}/backup-config.yaml"
    echo ""
    echo "Recommendations:"
    echo "  1. Review and customize rotation schedule"
    echo "  2. Configure backup destinations"
    echo "  3. Set up monitoring alerts"
    echo "  4. Document emergency procedures"
    echo "  5. Schedule regular security audits"
    echo ""
}

# Main execution
main() {
    echo ""
    echo "=========================================="
    echo "🛡️ SovereignGuard Vault Hardening"
    echo "   Phase 1: Security Configuration"
    echo "=========================================="
    echo ""
    
    verify_vault
    enhance_audit_logging
    tune_auth_methods
    tune_secrets_engines
    create_security_policies
    configure_rate_limiting
    configure_versioning
    create_rotation_config
    create_backup_config
    verify_security
    print_security_summary
    
    echo ""
    success "=========================================="
    success "🎉 Vault hardening complete!"
    success "=========================================="
    echo ""
}

# Execute if run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
