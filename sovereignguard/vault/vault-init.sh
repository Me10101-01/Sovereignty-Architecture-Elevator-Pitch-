#!/bin/bash
# SovereignGuard - Vault Initialization Script
# Phase 1: Credential Vault Setup
# Addresses exposures: #1, #2, #3, #4, #5, #6

set -euo pipefail

# Configuration
VAULT_ADDR="${VAULT_ADDR:-http://localhost:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-}"
VAULT_NAMESPACE="${VAULT_NAMESPACE:-sovereignguard}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/vault-init.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check prerequisites
check_prerequisites() {
    info "Checking prerequisites..."
    
    # Check for vault CLI
    if ! command -v vault >/dev/null 2>&1; then
        error "Vault CLI not found. Installing..."
        install_vault_cli
    fi
    
    # Check for jq
    if ! command -v jq >/dev/null 2>&1; then
        error "jq not found. Please install jq first."
        exit 1
    fi
    
    # Check for openssl
    if ! command -v openssl >/dev/null 2>&1; then
        error "openssl not found. Please install openssl first."
        exit 1
    fi
    
    success "All prerequisites met"
}

install_vault_cli() {
    info "Installing Vault CLI..."
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Download and install Vault
        curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
        sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
        sudo apt-get update && sudo apt-get install -y vault
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew tap hashicorp/tap
        brew install hashicorp/tap/vault
    else
        error "Unsupported OS. Please install Vault manually."
        exit 1
    fi
}

# Wait for Vault to be ready
wait_for_vault() {
    info "Waiting for Vault to be ready at ${VAULT_ADDR}..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if vault status >/dev/null 2>&1; then
            success "Vault is ready"
            return 0
        fi
        
        info "Attempt $attempt/$max_attempts: Vault not ready, waiting 5s..."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    error "Vault failed to become ready after $max_attempts attempts"
    exit 1
}

# Initialize Vault
initialize_vault() {
    info "Checking Vault initialization status..."
    
    if vault status 2>/dev/null | grep -q "Initialized.*true"; then
        info "Vault is already initialized"
        return 0
    fi
    
    info "Initializing Vault with Shamir's Secret Sharing..."
    
    # Initialize with 5 key shares, threshold of 3
    local init_output
    init_output=$(vault operator init -key-shares=5 -key-threshold=3 -format=json)
    
    # Create secure directory for keys
    local keys_dir="${SCRIPT_DIR}/.vault-keys"
    mkdir -p "$keys_dir"
    chmod 700 "$keys_dir"
    
    # Save unseal keys
    echo "$init_output" | jq -r '.unseal_keys_b64[]' > "${keys_dir}/unseal-keys"
    chmod 600 "${keys_dir}/unseal-keys"
    
    # Save root token
    echo "$init_output" | jq -r '.root_token' > "${keys_dir}/root-token"
    chmod 600 "${keys_dir}/root-token"
    
    warn "CRITICAL: Vault keys saved to ${keys_dir}/"
    warn "  - unseal-keys: Contains 5 unseal keys (need 3 to unseal)"
    warn "  - root-token: Root access token"
    warn "Please move these to a secure location and delete from disk!"
    
    # Set root token for subsequent operations
    export VAULT_TOKEN
    VAULT_TOKEN=$(cat "${keys_dir}/root-token")
    
    success "Vault initialized successfully"
}

# Unseal Vault
unseal_vault() {
    info "Checking Vault seal status..."
    
    if vault status 2>/dev/null | grep -q "Sealed.*false"; then
        info "Vault is already unsealed"
        return 0
    fi
    
    info "Unsealing Vault..."
    
    local keys_dir="${SCRIPT_DIR}/.vault-keys"
    if [[ -f "${keys_dir}/unseal-keys" ]]; then
        local count=0
        while IFS= read -r key; do
            vault operator unseal "$key" >/dev/null
            count=$((count + 1))
            if [ $count -ge 3 ]; then
                break
            fi
        done < "${keys_dir}/unseal-keys"
        
        success "Vault unsealed with $count keys"
    else
        error "No unseal keys found at ${keys_dir}/unseal-keys"
        error "Please unseal manually:"
        echo "  vault operator unseal <key1>"
        echo "  vault operator unseal <key2>"
        echo "  vault operator unseal <key3>"
        exit 1
    fi
}

# Setup secret engines
setup_secret_engines() {
    info "Setting up secret engines..."
    
    # Enable KV v2 secrets engine
    if ! vault secrets list | grep -q "secret/"; then
        vault secrets enable -path=secret kv-v2
        success "KV v2 secrets engine enabled at secret/"
    else
        info "KV v2 secrets engine already enabled"
    fi
    
    # Enable database secrets engine
    if ! vault secrets list | grep -q "database/"; then
        vault secrets enable database
        success "Database secrets engine enabled"
    else
        info "Database secrets engine already enabled"
    fi
    
    # Enable transit secrets engine for encryption
    if ! vault secrets list | grep -q "transit/"; then
        vault secrets enable transit
        success "Transit secrets engine enabled"
    else
        info "Transit secrets engine already enabled"
    fi
    
    # Create encryption key for SovereignGuard
    vault write -f transit/keys/sovereignguard 2>/dev/null || info "Transit key already exists"
    
    success "All secret engines configured"
}

# Setup policies
setup_policies() {
    info "Setting up access policies..."
    
    # Discord Bot Policy
    cat > /tmp/discord-bot-policy.hcl << 'EOF'
# Discord Bot Policy - Read-only access to Discord secrets
path "secret/data/discord/*" {
  capabilities = ["read"]
}

path "secret/metadata/discord/*" {
  capabilities = ["list", "read"]
}

path "secret/data/shared/hmac" {
  capabilities = ["read"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}
EOF
    vault policy write discord-bot /tmp/discord-bot-policy.hcl
    success "Discord bot policy created"
    
    # Event Gateway Policy
    cat > /tmp/event-gateway-policy.hcl << 'EOF'
# Event Gateway Policy - Webhook and GitHub access
path "secret/data/webhooks/*" {
  capabilities = ["read"]
}

path "secret/data/github/*" {
  capabilities = ["read"]
}

path "secret/data/shared/*" {
  capabilities = ["read"]
}

path "database/creds/event-gateway-ro" {
  capabilities = ["read"]
}

path "transit/encrypt/sovereignguard" {
  capabilities = ["update"]
}

path "transit/decrypt/sovereignguard" {
  capabilities = ["update"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}
EOF
    vault policy write event-gateway /tmp/event-gateway-policy.hcl
    success "Event gateway policy created"
    
    # Financial Enclave Policy (SwarmGate)
    cat > /tmp/financial-enclave-policy.hcl << 'EOF'
# Financial Enclave Policy - Trading API access with encryption
path "secret/data/trading/*" {
  capabilities = ["read"]
}

path "secret/data/swarmgate/*" {
  capabilities = ["read", "update"]
}

path "transit/encrypt/sovereignguard" {
  capabilities = ["update"]
}

path "transit/decrypt/sovereignguard" {
  capabilities = ["update"]
}

# No direct database access - only through encrypted channels
path "auth/token/renew-self" {
  capabilities = ["update"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}
EOF
    vault policy write financial-enclave /tmp/financial-enclave-policy.hcl
    success "Financial enclave policy created"
    
    # Audit Log Policy
    cat > /tmp/audit-log-policy.hcl << 'EOF'
# Audit Log Policy - Write-only audit access
path "secret/data/audit/*" {
  capabilities = ["create", "update"]
}

path "transit/encrypt/sovereignguard" {
  capabilities = ["update"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}
EOF
    vault policy write audit-log /tmp/audit-log-policy.hcl
    success "Audit log policy created"
    
    # Admin Policy
    cat > /tmp/admin-policy.hcl << 'EOF'
# Admin Policy - Full access for emergency operations
path "secret/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "database/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "transit/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "sys/policies/acl/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "auth/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "sys/mounts/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "sys/audit" {
  capabilities = ["read", "list"]
}

path "sys/audit/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}
EOF
    vault policy write admin /tmp/admin-policy.hcl
    success "Admin policy created"
    
    # Cleanup
    rm -f /tmp/*-policy.hcl
}

# Setup authentication methods
setup_auth() {
    info "Setting up authentication methods..."
    
    # Enable AppRole auth method
    if ! vault auth list | grep -q "approle/"; then
        vault auth enable approle
        success "AppRole auth method enabled"
    else
        info "AppRole auth method already enabled"
    fi
    
    # Create AppRole for each service
    local services=("discord-bot" "event-gateway" "financial-enclave" "audit-log")
    
    for service in "${services[@]}"; do
        vault write "auth/approle/role/${service}" \
            token_policies="${service}" \
            token_ttl=1h \
            token_max_ttl=4h \
            bind_secret_id=true
        
        success "AppRole for '${service}' created"
    done
    
    # Tune auth method settings
    vault auth tune -default-lease-ttl=1h -max-lease-ttl=8h approle/
    
    success "Authentication methods configured"
}

# Store initial secrets
store_initial_secrets() {
    info "Storing initial secrets..."
    
    # Validate required environment variables
    local has_placeholders=false
    
    # Discord secrets - validate or warn about placeholders
    if [[ -z "${DISCORD_TOKEN:-}" ]]; then
        warn "DISCORD_TOKEN not set - storing placeholder value"
        has_placeholders=true
    fi
    
    vault kv put secret/discord/bot \
        token="${DISCORD_TOKEN:-PLACEHOLDER_CHANGE_ME_DISCORD_TOKEN}" \
        client_id="${DISCORD_CLIENT_ID:-PLACEHOLDER_CHANGE_ME_CLIENT_ID}" \
        guild_id="${DISCORD_GUILD_ID:-PLACEHOLDER_CHANGE_ME_GUILD_ID}"
    success "Discord secrets stored"
    
    # GitHub secrets - validate or warn about placeholders
    if [[ -z "${GITHUB_TOKEN:-}" ]]; then
        warn "GITHUB_TOKEN not set - storing placeholder value"
        has_placeholders=true
    fi
    
    vault kv put secret/github/webhook \
        secret="${GITHUB_WEBHOOK_SECRET:-$(openssl rand -hex 32)}" \
        token="${GITHUB_TOKEN:-PLACEHOLDER_CHANGE_ME_GITHUB_TOKEN}"
    success "GitHub secrets stored"
    
    # Shared HMAC secrets - auto-generated for security
    vault kv put secret/shared/hmac \
        key="$(openssl rand -hex 32)" \
        events_key="$(openssl rand -hex 32)"
    success "HMAC secrets stored (auto-generated)"
    
    # JWT secrets - auto-generated for security
    vault kv put secret/shared/jwt \
        secret="$(openssl rand -hex 64)"
    success "JWT secrets stored (auto-generated)"
    
    # Trading API secrets - require explicit configuration
    warn "Trading API secrets require manual configuration"
    vault kv put secret/trading/ninjatrader \
        api_key="PLACEHOLDER_CHANGE_ME_NINJATRADER_API_KEY" \
        api_secret="PLACEHOLDER_CHANGE_ME_NINJATRADER_API_SECRET"
    vault kv put secret/trading/kraken \
        api_key="PLACEHOLDER_CHANGE_ME_KRAKEN_API_KEY" \
        api_secret="PLACEHOLDER_CHANGE_ME_KRAKEN_API_SECRET"
    success "Trading API secrets stored (placeholders)"
    
    # Report placeholder status
    if [[ "$has_placeholders" == "true" ]]; then
        echo ""
        warn "=========================================="
        warn "SECURITY WARNING: Placeholder secrets detected!"
        warn "=========================================="
        warn "Before production use, update the following secrets:"
        warn "  - secret/discord/bot (DISCORD_TOKEN, CLIENT_ID, GUILD_ID)"
        warn "  - secret/github/webhook (GITHUB_TOKEN)"
        warn "  - secret/trading/ninjatrader (API credentials)"
        warn "  - secret/trading/kraken (API credentials)"
        warn ""
        warn "Update with: vault kv put secret/<path> key=value"
        warn "=========================================="
    fi
    
    warn "Remember to update placeholder secrets with real values!"
}

# Enable audit logging
enable_audit() {
    info "Enabling audit logging..."
    
    local audit_dir="${SCRIPT_DIR}/../logs"
    mkdir -p "$audit_dir"
    chmod 700 "$audit_dir"
    
    # Enable file audit device
    if ! vault audit list | grep -q "file/"; then
        vault audit enable file file_path="${audit_dir}/vault-audit.log"
        success "File audit logging enabled at ${audit_dir}/vault-audit.log"
    else
        info "File audit logging already enabled"
    fi
}

# Print AppRole credentials
print_approle_credentials() {
    info "Generating AppRole credentials for services..."
    
    local services=("discord-bot" "event-gateway" "financial-enclave" "audit-log")
    
    echo ""
    echo "==================================="
    echo "AppRole Credentials for Services"
    echo "==================================="
    
    for service in "${services[@]}"; do
        local role_id
        local secret_id
        
        role_id=$(vault read -format=json "auth/approle/role/${service}/role-id" | jq -r '.data.role_id')
        secret_id=$(vault write -f -format=json "auth/approle/role/${service}/secret-id" | jq -r '.data.secret_id')
        
        echo ""
        echo "Service: ${service}"
        echo "  VAULT_ROLE_ID=${role_id}"
        echo "  VAULT_SECRET_ID=${secret_id}"
    done
    
    echo ""
    echo "==================================="
    warn "Save these credentials securely!"
    echo "==================================="
}

# Main execution
main() {
    echo ""
    echo "=========================================="
    echo "🔐 SovereignGuard Vault Initialization"
    echo "   Phase 1: Credential Vault Setup"
    echo "   Addresses exposures: #1-#6"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    wait_for_vault
    initialize_vault
    unseal_vault
    setup_secret_engines
    setup_policies
    setup_auth
    store_initial_secrets
    enable_audit
    print_approle_credentials
    
    echo ""
    success "=========================================="
    success "🎉 Vault initialization complete!"
    success "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Securely store and delete unseal keys from ${SCRIPT_DIR}/.vault-keys/"
    echo "2. Update placeholder secrets with real values"
    echo "3. Configure services with AppRole credentials above"
    echo "4. Run vault-hardening.sh for additional security"
    echo "5. Set up secret rotation schedule"
    echo ""
}

# Execute if run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
