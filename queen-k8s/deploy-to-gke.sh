#!/bin/bash
# Deploy ValorYield Sovereign OS and Queen Orchestrator to GKE
# One-shot deployment script for Strategickhaos infrastructure
#
# Legal Entities:
# - Strategickhaos DAO LLC (EIN: 39-2900295)
# - ValorYield Engine PBC (EIN: 39-2923503)
#
# Usage: ./deploy-to-gke.sh [CLUSTER_NAME] [ZONE]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
echo_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
echo_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $1"; }
echo_purple() { echo -e "${PURPLE}$1${NC}"; }

# Configuration
CLUSTER_NAME="${1:-jarvis-001}"
ZONE="${2:-us-central1-a}"
PROJECT="${GOOGLE_CLOUD_PROJECT:-}"
NAMESPACE="valoryield"

# Banner
print_banner() {
    echo_purple "
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    VALORYIELD SOVEREIGN FINANCIAL OS                          ║
║                    GKE Deployment Script                                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Legal Foundation:                                                            ║
║  ├── Strategickhaos DAO LLC (EIN: 39-2900295) - Wyoming DAO                  ║
║  └── ValorYield Engine PBC (EIN: 39-2923503) - Public Benefit Corp           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"
}

# Check prerequisites
check_prerequisites() {
    echo_info "Checking prerequisites..."
    
    # Check gcloud
    if ! command -v gcloud &> /dev/null; then
        echo_error "gcloud CLI is required but not installed"
        echo_info "Install from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        echo_error "kubectl is required but not installed"
        echo_info "Install with: gcloud components install kubectl"
        exit 1
    fi
    
    # Check project
    if [ -z "$PROJECT" ]; then
        PROJECT=$(gcloud config get-value project 2>/dev/null || true)
        if [ -z "$PROJECT" ]; then
            echo_error "No Google Cloud project configured"
            echo_info "Run: gcloud config set project YOUR_PROJECT_ID"
            exit 1
        fi
    fi
    
    echo_success "Prerequisites check passed"
    echo_info "Project: $PROJECT"
    echo_info "Cluster: $CLUSTER_NAME"
    echo_info "Zone: $ZONE"
}

# Authenticate and configure kubectl
configure_cluster() {
    echo_info "Configuring kubectl for cluster $CLUSTER_NAME..."
    
    # Check if cluster exists
    if ! gcloud container clusters describe "$CLUSTER_NAME" --zone="$ZONE" --project="$PROJECT" &>/dev/null; then
        echo_warning "Cluster $CLUSTER_NAME not found in zone $ZONE"
        echo_info "Available clusters:"
        gcloud container clusters list --project="$PROJECT" 2>/dev/null || echo "  (none found)"
        
        read -rp "Create new cluster $CLUSTER_NAME? [y/N] " create_cluster
        if [[ "$create_cluster" =~ ^[Yy]$ ]]; then
            create_new_cluster
        else
            echo_error "Cluster not available. Exiting."
            exit 1
        fi
    fi
    
    # Get credentials
    gcloud container clusters get-credentials "$CLUSTER_NAME" \
        --zone="$ZONE" \
        --project="$PROJECT"
    
    echo_success "kubectl configured for $CLUSTER_NAME"
}

# Create new GKE cluster
create_new_cluster() {
    echo_info "Creating new GKE cluster: $CLUSTER_NAME"
    
    gcloud container clusters create "$CLUSTER_NAME" \
        --zone="$ZONE" \
        --project="$PROJECT" \
        --num-nodes=3 \
        --machine-type=e2-medium \
        --enable-autoscaling \
        --min-nodes=2 \
        --max-nodes=5 \
        --enable-network-policy \
        --labels=app=valoryield-sovereign-os,org=strategickhaos
    
    echo_success "Cluster $CLUSTER_NAME created"
}

# Deploy manifests
deploy_manifests() {
    echo_info "Deploying ValorYield Sovereign OS..."
    
    # Apply the deployment manifest
    if [ -f "queen-deployment.yaml" ]; then
        kubectl apply -f queen-deployment.yaml
        echo_success "Manifests applied"
    else
        echo_error "queen-deployment.yaml not found"
        echo_info "Make sure you're running this script from the queen-k8s directory"
        exit 1
    fi
}

# Wait for deployments
wait_for_deployments() {
    echo_info "Waiting for deployments to be ready..."
    
    # Wait for ValorYield
    echo_info "Waiting for valoryield-os deployment..."
    kubectl wait --for=condition=available --timeout=300s \
        deployment/valoryield-os -n "$NAMESPACE" || {
        echo_warning "ValorYield deployment not ready yet, continuing..."
    }
    
    # Wait for Queen
    echo_info "Waiting for queen-orchestrator deployment..."
    kubectl wait --for=condition=available --timeout=300s \
        deployment/queen-orchestrator -n "$NAMESPACE" || {
        echo_warning "Queen deployment not ready yet, continuing..."
    }
    
    echo_success "Deployments ready"
}

# Get external IP
get_external_ip() {
    echo_info "Getting external IP address..."
    
    local ip=""
    local attempts=0
    local max_attempts=30
    
    while [ -z "$ip" ] && [ $attempts -lt $max_attempts ]; do
        ip=$(kubectl get svc queen-lb -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)
        if [ -z "$ip" ]; then
            echo_info "Waiting for LoadBalancer IP... (attempt $((attempts+1))/$max_attempts)"
            sleep 10
            ((attempts++))
        fi
    done
    
    if [ -n "$ip" ]; then
        echo_success "External IP: $ip"
        echo ""
        echo_purple "╔═══════════════════════════════════════════════════════════════╗"
        echo_purple "║  DEPLOYMENT COMPLETE                                          ║"
        echo_purple "╠═══════════════════════════════════════════════════════════════╣"
        echo_purple "║  Queen Orchestrator:  http://$ip                       ║"
        echo_purple "║  ValorYield API:      http://$ip/signals/financial     ║"
        echo_purple "╠═══════════════════════════════════════════════════════════════╣"
        echo_purple "║  DNS Configuration:                                           ║"
        echo_purple "║  Point queen.strategickhaos.ai → $ip                   ║"
        echo_purple "╚═══════════════════════════════════════════════════════════════╝"
    else
        echo_warning "LoadBalancer IP not yet assigned"
        echo_info "Check later with: kubectl get svc queen-lb -n $NAMESPACE"
    fi
}

# Show status
show_status() {
    echo ""
    echo_info "Deployment Status:"
    echo ""
    
    echo_info "Pods:"
    kubectl get pods -n "$NAMESPACE" -o wide
    
    echo ""
    echo_info "Services:"
    kubectl get svc -n "$NAMESPACE"
    
    echo ""
    echo_info "Deployments:"
    kubectl get deployments -n "$NAMESPACE"
}

# Cleanup function
cleanup() {
    echo_warning "Cleaning up ValorYield deployment..."
    kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
    echo_success "Cleanup complete"
}

# Main execution
main() {
    print_banner
    
    case "${1:-deploy}" in
        deploy)
            check_prerequisites
            configure_cluster
            deploy_manifests
            wait_for_deployments
            get_external_ip
            show_status
            ;;
        status)
            check_prerequisites
            configure_cluster
            show_status
            get_external_ip
            ;;
        cleanup|clean)
            check_prerequisites
            configure_cluster
            cleanup
            ;;
        *)
            echo "Usage: $0 [deploy|status|cleanup] [CLUSTER_NAME] [ZONE]"
            echo ""
            echo "Commands:"
            echo "  deploy   - Deploy ValorYield Sovereign OS to GKE (default)"
            echo "  status   - Show deployment status"
            echo "  cleanup  - Remove all deployed resources"
            echo ""
            echo "Examples:"
            echo "  $0 deploy jarvis-001 us-central1-a"
            echo "  $0 status"
            echo "  $0 cleanup"
            exit 1
            ;;
    esac
    
    echo ""
    echo_success "Done! 🚀"
}

# Run main
main "$@"
