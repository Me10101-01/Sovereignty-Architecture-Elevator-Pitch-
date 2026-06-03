#!/bin/bash
# Strategickhaos Discord DevOps Control Plane Bootstrap Script
# Modes: deploy (k8s), compose (docker-compose), templates (config only)
set -uo pipefail

NAMESPACE="${NAMESPACE:-ops}"
KUBECTL="${KUBECTL:-kubectl}"
OUTPUT_DIR="${OUTPUT_DIR:-${HOME}/sagco_bootstrap}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

echo_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Resolve a writable output directory (never assumes CWD is writable)
resolve_output_dir() {
    if [[ -w "${PWD}" ]]; then
        OUTPUT_DIR="${PWD}"
    elif [[ -w "${HOME}" ]]; then
        OUTPUT_DIR="${HOME}/sagco_bootstrap"
        mkdir -p "${OUTPUT_DIR}" 2>/dev/null || true
    else
        OUTPUT_DIR="${TMPDIR:-/tmp}/sagco_bootstrap"
        mkdir -p "${OUTPUT_DIR}" 2>/dev/null || true
    fi
    echo_info "Output directory: ${OUTPUT_DIR}"
}

# Check prerequisites — warn only, do not exit
check_prerequisites() {
    echo_info "Checking prerequisites..."

    local mode="$1"

    if [[ "$mode" == "compose" ]]; then
        if command -v docker &> /dev/null; then
            echo_success "docker: found"
        else
            echo_warning "docker not found — install Docker to run compose mode"
        fi
        if docker compose version &> /dev/null 2>&1 || docker-compose version &> /dev/null 2>&1; then
            echo_success "docker compose: available"
        else
            echo_warning "docker compose not found — templates will still be generated"
        fi
        return 0
    fi

    # k8s mode checks
    if ! command -v kubectl &> /dev/null; then
        echo_warning "kubectl not found — switching to templates-only mode"
        echo_warning "Install kubectl: https://kubernetes.io/docs/tasks/tools/"
        return 1
    fi

    if ! command -v jq &> /dev/null; then
        echo_warning "jq not found — some features may not work properly"
    fi

    if ! $KUBECTL cluster-info &> /dev/null; then
        echo_warning "Cannot connect to Kubernetes cluster — switching to templates-only mode"
        echo_warning "Point KUBECONFIG to a live cluster to deploy"
        return 1
    fi

    echo_success "Prerequisites check passed (k8s mode)"
    return 0
}

# Create namespace
create_namespace() {
    echo_info "Creating namespace: $NAMESPACE"

    if $KUBECTL get namespace "$NAMESPACE" &> /dev/null; then
        echo_warning "Namespace $NAMESPACE already exists"
    else
        $KUBECTL create namespace "$NAMESPACE"
        $KUBECTL label namespace "$NAMESPACE" name="$NAMESPACE"
        echo_success "Namespace $NAMESPACE created"
    fi
}

# Apply Kubernetes manifests
apply_manifests() {
    echo_info "Applying Kubernetes manifests..."

    local manifests=(
        "rbac.yaml"
        "secrets.yaml"
        "configmap.yaml"
        "bot-deployment.yaml"
        "gateway-deployment.yaml"
        "ingress.yaml"
    )

    for manifest in "${manifests[@]}"; do
        if [[ -f "k8s/$manifest" ]]; then
            echo_info "Applying $manifest..."
            $KUBECTL apply -f "k8s/$manifest" -n "$NAMESPACE"
            echo_success "$manifest applied"
        else
            echo_warning "Manifest $manifest not found, skipping"
        fi
    done
}

# Wait for deployments
wait_for_deployments() {
    echo_info "Waiting for deployments to be ready..."

    local deployments=("discord-ops-bot" "event-gateway")

    for deployment in "${deployments[@]}"; do
        echo_info "Waiting for $deployment..."
        if $KUBECTL get deployment "$deployment" -n "$NAMESPACE" &> /dev/null; then
            $KUBECTL wait --for=condition=available --timeout=300s deployment/"$deployment" -n "$NAMESPACE"
            echo_success "$deployment is ready"
        else
            echo_warning "Deployment $deployment not found"
        fi
    done
}

# Verify installation
verify_installation() {
    echo_info "Verifying installation..."

    if ! command -v kubectl &> /dev/null; then
        echo_warning "kubectl not available — skipping cluster verification"
        return 0
    fi

    echo_info "Checking pod status..."
    $KUBECTL get pods -n "$NAMESPACE" -l app=strategickhaos-discord-ops

    echo_info "Checking services..."
    $KUBECTL get services -n "$NAMESPACE" -l app=strategickhaos-discord-ops

    echo_info "Checking ingress..."
    $KUBECTL get ingress -n "$NAMESPACE" strategickhaos-events || echo_warning "Ingress not found"

    local running_pods
    running_pods=$($KUBECTL get pods -n "$NAMESPACE" -l app=strategickhaos-discord-ops \
        --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)

    if [[ $running_pods -gt 0 ]]; then
        echo_success "Installation verification passed - $running_pods pods running"
    else
        echo_warning "No running pods found - check logs for issues"
    fi
}

# Generate configuration templates (writes to resolved output dir)
generate_config_templates() {
    resolve_output_dir
    echo_info "Generating configuration templates in ${OUTPUT_DIR}..."

    cat > "${OUTPUT_DIR}/discord-bot-env.template" << 'EOF'
# Discord Bot Configuration Template
# Copy to .env and fill in real values

# Discord Bot Token (from Discord Developer Portal)
DISCORD_BOT_TOKEN=your_bot_token_here

# Discord Guild (Server) ID
DISCORD_GUILD_ID=your_discord_server_id

# Channel IDs (right-click channel in Discord, copy ID)
PRS_CHANNEL=channel_id_for_prs
DEV_FEED_CHANNEL=channel_id_for_dev_feed

# GitHub App Configuration
GITHUB_APP_ID=your_github_app_id
GITHUB_APP_WEBHOOK_SECRET=your_webhook_secret
GITHUB_APP_PRIVATE_KEY_PATH=/path/to/private-key.pem

# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key

# PostgreSQL Vector Database
PGVECTOR_CONN=postgresql://user:pass@host:5432/db

# HMAC Key for webhook verification (generate with: openssl rand -hex 32)
EVENTS_HMAC_KEY=your_64_character_hmac_key_here
EOF

    cat > "${OUTPUT_DIR}/github-app-manifest.json" << 'EOF'
{
  "name": "Strategickhaos Discord DevOps",
  "url": "https://github.com/Strategickhaos-Swarm-Intelligence",
  "hook_attributes": {
    "url": "https://events.strategickhaos.com/git"
  },
  "redirect_url": "https://events.strategickhaos.com/auth/callback",
  "description": "Discord-based DevOps automation for Strategickhaos infrastructure",
  "public": false,
  "default_events": [
    "pull_request",
    "push",
    "check_suite",
    "issue_comment",
    "release"
  ],
  "default_permissions": {
    "contents": "read",
    "metadata": "read",
    "pull_requests": "write",
    "checks": "write"
  }
}
EOF

    echo_success "Configuration templates generated:"
    echo "  ${OUTPUT_DIR}/discord-bot-env.template"
    echo "  ${OUTPUT_DIR}/github-app-manifest.json"
}

# Generate docker-compose.yml for non-k8s deployments
generate_compose_file() {
    resolve_output_dir
    echo_info "Generating docker-compose.yml in ${OUTPUT_DIR}..."

    cat > "${OUTPUT_DIR}/docker-compose.yml" << 'EOF'
version: "3.9"

services:
  discord-ops-bot:
    image: strategickhaos/discord-ops-bot:latest
    restart: unless-stopped
    env_file: .env
    environment:
      - NAMESPACE=ops
    ports:
      - "8080:8080"
    depends_on:
      - event-gateway
      - db
    labels:
      - "app=strategickhaos-discord-ops"
      - "sagco.device=${SAGCO_DEVICE:-unknown}"
      - "sagco.status=SAGCO_FLEET_NODE"

  event-gateway:
    image: strategickhaos/event-gateway:latest
    restart: unless-stopped
    env_file: .env
    ports:
      - "4000:4000"
    labels:
      - "app=strategickhaos-discord-ops"

  db:
    image: pgvector/pgvector:pg16
    restart: unless-stopped
    environment:
      POSTGRES_DB: sagco
      POSTGRES_USER: sagco
      POSTGRES_PASSWORD: changeme_in_production
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
EOF

    echo_success "docker-compose.yml generated: ${OUTPUT_DIR}/docker-compose.yml"
    echo_info "Run with: cd ${OUTPUT_DIR} && cp discord-bot-env.template .env && docker compose up -d"
}

# Show next steps
show_next_steps() {
    local mode="$1"
    echo_info "🔥 Strategickhaos Discord DevOps Control Plane Bootstrap Complete!"
    echo

    if [[ "$mode" == "compose" ]]; then
        echo "Next steps (Compose mode):"
        echo "1. cd ${OUTPUT_DIR}"
        echo "2. cp discord-bot-env.template .env"
        echo "3. Edit .env with real Discord token + GitHub App values"
        echo "4. docker compose up -d"
        echo "5. docker compose logs -f discord-ops-bot"
    elif [[ "$mode" == "templates" ]]; then
        echo "Next steps (Templates mode):"
        echo "1. Review generated files in: ${OUTPUT_DIR}"
        echo "2. On HP SAGCO-OS with kubectl: ./bootstrap/deploy.sh deploy"
        echo "3. On any node with Docker:     ./bootstrap/deploy.sh compose"
    else
        echo "Next steps (k8s mode):"
        echo "1. Configure secrets in k8s/secrets.yaml with real values"
        echo "2. Create Discord bot at https://discord.com/developers/applications"
        echo "3. Create GitHub App using ${OUTPUT_DIR}/github-app-manifest.json"
        echo "4. Set up DNS for events.strategickhaos.com -> your ingress"
        echo "5. Test: ./gl2discord.sh \"\$PRS_CHANNEL\" \"Test\" \"Bootstrap complete!\""
    fi
    echo
    echo "SAGCO provenance: sagco-race && sagco-cloud-ping"
}

# Main k8s deploy
main_deploy() {
    echo_info "🔥 Strategickhaos Discord DevOps Control Plane Bootstrap"
    echo_info "Mode: Kubernetes"
    echo

    if ! check_prerequisites "k8s"; then
        echo_warning "k8s prerequisites not met — falling back to templates-only mode"
        generate_config_templates
        generate_compose_file
        show_next_steps "templates"
        echo_success "Templates generated — deploy when cluster is available"
        exit 0
    fi

    create_namespace
    apply_manifests
    wait_for_deployments
    verify_installation
    generate_config_templates
    show_next_steps "k8s"
    echo_success "Bootstrap complete!"
}

# Compose deploy (no k8s needed)
main_compose() {
    echo_info "🔥 Strategickhaos Discord DevOps Control Plane Bootstrap"
    echo_info "Mode: Docker Compose"
    echo

    check_prerequisites "compose" || true
    generate_config_templates
    generate_compose_file
    show_next_steps "compose"
    echo_success "Compose bootstrap complete!"
}

# Templates only (no runtime needed)
main_templates() {
    echo_info "🔥 Strategickhaos Bootstrap — Templates Only"
    echo

    generate_config_templates
    generate_compose_file
    show_next_steps "templates"
    echo_success "Templates generated!"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main_deploy
        ;;
    "compose")
        main_compose
        ;;
    "templates")
        main_templates
        ;;
    "verify")
        verify_installation
        ;;
    "clean")
        echo_warning "Cleaning up Strategickhaos Discord DevOps deployment..."
        if command -v kubectl &> /dev/null; then
            $KUBECTL delete namespace "$NAMESPACE" --ignore-not-found=true
            echo_success "Kubernetes cleanup complete"
        else
            echo_warning "kubectl not found — nothing to clean in k8s"
        fi
        ;;
    *)
        echo "Usage: $0 [deploy|compose|templates|verify|clean]"
        echo ""
        echo "  deploy     Deploy to Kubernetes (requires kubectl + cluster)"
        echo "  compose    Generate docker-compose.yml (works on any node)"
        echo "  templates  Generate config templates only (works everywhere)"
        echo "  verify     Verify existing k8s deployment"
        echo "  clean      Remove k8s deployment"
        echo ""
        echo "  deploy falls back to templates-only if kubectl is unavailable"
        echo "  compose and templates work on ZFold, iSH, HP, RPi — any node"
        exit 1
        ;;
esac
