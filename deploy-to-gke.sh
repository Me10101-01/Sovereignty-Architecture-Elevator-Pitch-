#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# 👑 Queen Deploy Script - Deploy to GKE in 60 Seconds
# ═══════════════════════════════════════════════════════════════════════════════
# 
# Usage:
#   ./deploy-to-gke.sh [options]
#
# Options:
#   --dry-run     Preview what would be deployed without applying
#   --delete      Remove Queen deployment from cluster
#   --status      Check current deployment status
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - kubectl installed
#   - Access to jarvis-swarm-personal-001 GKE cluster
#
# ═══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

# Configuration
CLUSTER_NAME="${CLUSTER_NAME:-jarvis-swarm-personal-001}"
CLUSTER_ZONE="${CLUSTER_ZONE:-us-central1-c}"
PROJECT_ID="${PROJECT_ID:-strategickhaos}"
NAMESPACE="queen-system"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="${SCRIPT_DIR}/bootstrap/k8s/queen"

# Check if running from repo root
if [[ ! -d "$K8S_DIR" ]]; then
    K8S_DIR="${SCRIPT_DIR}/k8s/queen"
fi
if [[ ! -d "$K8S_DIR" ]]; then
    K8S_DIR="${SCRIPT_DIR}"
fi

echo_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                     👑 QUEEN DEPLOYMENT                          ║"
    echo "║              StrategicKhaos Swarm Intelligence                   ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

echo_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

echo_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

echo_error() {
    echo -e "${RED}[✗]${NC} $1"
}

check_prerequisites() {
    echo_step "Checking prerequisites..."
    
    local missing=0
    
    if ! command -v gcloud &> /dev/null; then
        echo_error "gcloud CLI not found. Install: https://cloud.google.com/sdk/docs/install"
        missing=1
    else
        echo_success "gcloud CLI found"
    fi
    
    if ! command -v kubectl &> /dev/null; then
        echo_error "kubectl not found. Install: https://kubernetes.io/docs/tasks/tools/"
        missing=1
    else
        echo_success "kubectl found"
    fi
    
    if [[ $missing -eq 1 ]]; then
        echo_error "Missing prerequisites. Please install and try again."
        exit 1
    fi
}

get_gke_credentials() {
    echo_step "Getting GKE credentials for ${CLUSTER_NAME}..."
    
    if gcloud container clusters get-credentials "$CLUSTER_NAME" \
        --zone "$CLUSTER_ZONE" \
        --project "$PROJECT_ID" 2>/dev/null; then
        echo_success "Connected to GKE cluster: ${CLUSTER_NAME}"
    else
        echo_warning "Could not get credentials automatically. Trying current context..."
        if kubectl cluster-info &>/dev/null; then
            echo_success "Using current kubectl context"
        else
            echo_error "Cannot connect to any Kubernetes cluster"
            exit 1
        fi
    fi
}

create_namespace() {
    echo_step "Creating namespace: ${NAMESPACE}..."
    
    if kubectl get namespace "$NAMESPACE" &>/dev/null; then
        echo_warning "Namespace ${NAMESPACE} already exists"
    else
        kubectl apply -f "${K8S_DIR}/namespace.yaml"
        echo_success "Namespace ${NAMESPACE} created"
    fi
}

deploy_queen() {
    echo_step "Deploying Queen components..."
    
    local manifests=(
        "configmap.yaml"
        "secrets.yaml"
        "deployment.yaml"
        "service.yaml"
        "ingress.yaml"
    )
    
    for manifest in "${manifests[@]}"; do
        local file="${K8S_DIR}/${manifest}"
        if [[ -f "$file" ]]; then
            echo "  Applying ${manifest}..."
            if [[ "$DRY_RUN" == "true" ]]; then
                kubectl apply -f "$file" --dry-run=client
            else
                kubectl apply -f "$file"
            fi
            echo_success "${manifest} applied"
        else
            echo_warning "Manifest ${manifest} not found, skipping"
        fi
    done
}

wait_for_deployment() {
    echo_step "Waiting for Queen deployment to be ready..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo_warning "Dry run - skipping wait"
        return
    fi
    
    kubectl wait --for=condition=available --timeout=300s \
        deployment/queen -n "$NAMESPACE" || {
        echo_warning "Deployment not ready yet. Check status with: kubectl get pods -n ${NAMESPACE}"
    }
    
    echo_success "Queen deployment is ready!"
}

get_loadbalancer_ip() {
    echo_step "Getting LoadBalancer IP..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo_warning "Dry run - no IP available"
        return
    fi
    
    echo "  Waiting for external IP (this may take 1-2 minutes)..."
    
    local attempts=0
    local max_attempts=30
    local external_ip=""
    
    while [[ -z "$external_ip" || "$external_ip" == "<pending>" ]] && [[ $attempts -lt $max_attempts ]]; do
        external_ip=$(kubectl get svc queen -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
        if [[ -z "$external_ip" ]]; then
            sleep 5
            attempts=$((attempts + 1))
            echo -n "."
        fi
    done
    echo ""
    
    if [[ -n "$external_ip" && "$external_ip" != "<pending>" ]]; then
        echo_success "LoadBalancer IP: ${external_ip}"
        EXTERNAL_IP="$external_ip"
    else
        echo_warning "External IP not yet assigned. Check later with:"
        echo "  kubectl get svc queen -n ${NAMESPACE}"
        EXTERNAL_IP=""
    fi
}

show_dns_instructions() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                     📡 DNS CONFIGURATION                          ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if [[ -n "${EXTERNAL_IP:-}" ]]; then
        echo "Point your DNS to the LoadBalancer IP:"
        echo ""
        echo "  If using Cloudflare:"
        echo -e "    Type: ${GREEN}A${NC}"
        echo -e "    Name: ${GREEN}queen${NC}"
        echo -e "    Content: ${GREEN}${EXTERNAL_IP}${NC}"
        echo -e "    Proxy: ${YELLOW}Off (initially)${NC}"
        echo ""
        echo "  If using Route53 or other DNS:"
        echo -e "    Type: ${GREEN}A${NC}"
        echo -e "    Name: ${GREEN}queen.strategickhaos.ai${NC}"
        echo -e "    Value: ${GREEN}${EXTERNAL_IP}${NC}"
    else
        echo "Once you have the LoadBalancer IP, configure DNS:"
        echo "  kubectl get svc queen -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"
    fi
    echo ""
}

show_github_app_instructions() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                 🔗 GITHUB APP CONFIGURATION                       ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "After DNS is working, update your GitHub App:"
    echo ""
    echo "  1. Go to: https://github.com/organizations/strategickhaos-swarm-intelligence/settings/apps/estrategi-khaos-queen-app"
    echo ""
    echo "  2. Set Webhook URL:"
    echo -e "     ${GREEN}https://queen.strategickhaos.ai/webhooks/github${NC}"
    echo ""
    echo "  3. Set Callback URL:"
    echo -e "     ${GREEN}https://queen.strategickhaos.ai/oauth/callback${NC}"
    echo ""
    echo "  4. Save changes"
    echo ""
}

show_summary() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                      🎉 DEPLOYMENT COMPLETE                       ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Queen is now deployed to ${CLUSTER_NAME}!"
    echo ""
    echo "📊 Deployment Status:"
    kubectl get pods,svc -n "$NAMESPACE" 2>/dev/null || echo "  (run kubectl get pods -n ${NAMESPACE})"
    echo ""
    echo "🔍 Useful Commands:"
    echo "  View logs:     kubectl logs -f deployment/queen -n ${NAMESPACE}"
    echo "  Check status:  kubectl get all -n ${NAMESPACE}"
    echo "  Get IP:        kubectl get svc queen -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"
    echo "  Port forward:  kubectl port-forward svc/queen 3000:80 -n ${NAMESPACE}"
    echo ""
    echo "🌐 Test locally (before DNS):"
    echo "  kubectl port-forward svc/queen 3000:80 -n ${NAMESPACE}"
    echo "  curl http://localhost:3000/health"
    echo ""
}

show_status() {
    echo_banner
    echo_step "Queen Deployment Status"
    echo ""
    
    echo "Namespace: ${NAMESPACE}"
    kubectl get namespace "$NAMESPACE" 2>/dev/null || echo "  Not found"
    echo ""
    
    echo "Pods:"
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=queen 2>/dev/null || echo "  None"
    echo ""
    
    echo "Services:"
    kubectl get svc -n "$NAMESPACE" 2>/dev/null || echo "  None"
    echo ""
    
    echo "Ingress:"
    kubectl get ingress -n "$NAMESPACE" 2>/dev/null || echo "  None"
    echo ""
    
    local external_ip
    external_ip=$(kubectl get svc queen -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    if [[ -n "$external_ip" ]]; then
        echo "LoadBalancer IP: ${external_ip}"
        echo "Health check: curl http://${external_ip}/health"
    fi
}

delete_deployment() {
    echo_banner
    echo_step "Deleting Queen deployment..."
    
    local reply
    read -p "Are you sure you want to delete the Queen deployment? [y/N] " -n 1 -r reply
    echo ""
    if [[ ! $reply =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
    
    kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
    echo_success "Queen deployment deleted"
}

# Main
main() {
    DRY_RUN="false"
    
    # Parse arguments
    for arg in "$@"; do
        case $arg in
            --dry-run)
                DRY_RUN="true"
                echo_warning "DRY RUN MODE - No changes will be applied"
                ;;
            --delete)
                delete_deployment
                exit 0
                ;;
            --status)
                show_status
                exit 0
                ;;
            --help|-h)
                echo "Usage: $0 [--dry-run|--delete|--status|--help]"
                exit 0
                ;;
        esac
    done
    
    echo_banner
    
    check_prerequisites
    get_gke_credentials
    create_namespace
    deploy_queen
    wait_for_deployment
    get_loadbalancer_ip
    show_summary
    show_dns_instructions
    show_github_app_instructions
    
    echo_success "👑 Queen is ready to serve!"
    echo ""
}

main "$@"
