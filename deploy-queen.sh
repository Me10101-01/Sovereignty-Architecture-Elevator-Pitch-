#!/bin/bash
# Queen GKE Deployment Script
# Deploys Queen orchestrator to jarvis-swarm-personal-001
# Usage: ./deploy-queen.sh [deploy|verify|clean]

set -euo pipefail

# Configuration
NAMESPACE="${NAMESPACE:-queen}"
CLUSTER="${CLUSTER:-jarvis-swarm-personal-001}"
REGION="${REGION:-us-central1}"
PROJECT="${PROJECT:-jarvis-swarm-personal}"
KUBECTL="${KUBECTL:-kubectl}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

echo_header() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
}

# Check prerequisites
check_prerequisites() {
    echo_info "Checking prerequisites..."
    
    if ! command -v kubectl &> /dev/null; then
        echo_error "kubectl is required but not installed"
        echo_info "Install: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi
    
    if ! command -v gcloud &> /dev/null; then
        echo_warning "gcloud CLI not found - cluster authentication may fail"
        echo_info "Install: https://cloud.google.com/sdk/docs/install"
    fi
    
    echo_success "Prerequisites check passed"
}

# Connect to GKE cluster
connect_cluster() {
    echo_info "Connecting to GKE cluster: $CLUSTER..."
    
    if command -v gcloud &> /dev/null; then
        gcloud container clusters get-credentials "$CLUSTER" \
            --region "$REGION" \
            --project "$PROJECT"
        echo_success "Connected to $CLUSTER"
    else
        echo_warning "gcloud not available - assuming kubectl is already configured"
    fi
    
    # Verify connectivity
    if ! $KUBECTL cluster-info &> /dev/null; then
        echo_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    echo_success "Cluster connection verified"
}

# Apply Queen manifests
deploy_queen() {
    echo_header "👑 DEPLOYING QUEEN ORCHESTRATOR"
    echo_info "Target cluster: $CLUSTER (34.29.28.27)"
    echo_info "Namespace: $NAMESPACE"
    echo
    
    local manifests_dir="bootstrap/k8s/queen"
    
    if [[ ! -d "$manifests_dir" ]]; then
        echo_error "Manifests directory not found: $manifests_dir"
        echo_info "Run from repository root directory"
        exit 1
    fi
    
    local manifests=(
        "namespace.yaml"
        "secrets.yaml"
        "rbac.yaml"
        "deployment.yaml"
        "service.yaml"
        "ingress.yaml"
        "autoscaling.yaml"
    )
    
    for manifest in "${manifests[@]}"; do
        if [[ -f "$manifests_dir/$manifest" ]]; then
            echo_info "Applying $manifest..."
            $KUBECTL apply -f "$manifests_dir/$manifest"
            echo_success "$manifest applied"
        else
            echo_warning "Manifest $manifest not found, skipping"
        fi
    done
}

# Wait for deployment
wait_for_deployment() {
    echo_info "Waiting for Queen deployment to be ready..."
    
    if $KUBECTL get deployment queen -n "$NAMESPACE" &> /dev/null; then
        $KUBECTL wait --for=condition=available --timeout=300s deployment/queen -n "$NAMESPACE"
        echo_success "Queen deployment is ready"
    else
        echo_error "Queen deployment not found"
        return 1
    fi
}

# Get LoadBalancer IP
get_loadbalancer_ip() {
    echo_info "Waiting for LoadBalancer IP assignment..."
    
    local max_attempts=30
    local attempt=0
    local lb_ip=""
    
    while [[ $attempt -lt $max_attempts ]]; do
        lb_ip=$($KUBECTL get svc queen -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
        
        if [[ -n "$lb_ip" ]]; then
            echo_success "LoadBalancer IP: $lb_ip"
            echo
            echo_header "🌐 DNS CONFIGURATION"
            echo_info "Point queen.strategickhaos.ai → $lb_ip"
            echo
            echo "Cloudflare:"
            echo "  Type: A"
            echo "  Name: queen"
            echo "  Content: $lb_ip"
            echo "  TTL: 300"
            echo "  Proxied: Yes"
            echo
            return 0
        fi
        
        ((attempt++))
        echo_info "Waiting for LoadBalancer... ($attempt/$max_attempts)"
        sleep 10
    done
    
    echo_warning "LoadBalancer IP not yet assigned"
    echo_info "Check status: kubectl get svc queen -n $NAMESPACE -w"
    return 1
}

# Verify deployment
verify_deployment() {
    echo_header "🔍 VERIFYING DEPLOYMENT"
    
    echo_info "Checking namespace..."
    $KUBECTL get namespace "$NAMESPACE" || echo_warning "Namespace not found"
    
    echo
    echo_info "Checking pods..."
    $KUBECTL get pods -n "$NAMESPACE" -l app=strategickhaos-queen
    
    echo
    echo_info "Checking services..."
    $KUBECTL get services -n "$NAMESPACE" -l app=strategickhaos-queen
    
    echo
    echo_info "Checking ingress..."
    $KUBECTL get ingress -n "$NAMESPACE" 2>/dev/null || echo_info "No ingress found"
    
    echo
    echo_info "Checking HPA..."
    $KUBECTL get hpa -n "$NAMESPACE" 2>/dev/null || echo_info "No HPA found"
    
    # Get running pods count
    local running_pods
    running_pods=$($KUBECTL get pods -n "$NAMESPACE" -l app=strategickhaos-queen --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
    
    echo
    if [[ $running_pods -gt 0 ]]; then
        echo_success "Deployment verified - $running_pods pods running"
        
        # Try to get LoadBalancer IP
        local lb_ip
        lb_ip=$($KUBECTL get svc queen -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
        
        if [[ -n "$lb_ip" ]]; then
            echo
            echo_header "✅ QUEEN IS LIVE"
            echo "LoadBalancer IP: $lb_ip"
            echo "Health Check:    http://$lb_ip/health"
            echo "API Endpoint:    http://$lb_ip/api/v1/status"
            echo
            echo "Test with:"
            echo "  curl http://$lb_ip/health"
        fi
    else
        echo_warning "No running pods found - check logs for issues"
        echo_info "Get logs: kubectl logs -l app=strategickhaos-queen -n $NAMESPACE"
        return 1
    fi
}

# Clean up deployment
clean_deployment() {
    echo_header "🧹 CLEANING UP QUEEN DEPLOYMENT"
    echo_warning "This will delete the Queen namespace and all resources"
    echo
    
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        $KUBECTL delete namespace "$NAMESPACE" --ignore-not-found=true
        echo_success "Queen namespace deleted"
    else
        echo_info "Cleanup cancelled"
    fi
}

# Show logs
show_logs() {
    echo_header "📋 QUEEN LOGS"
    $KUBECTL logs -l app=strategickhaos-queen -n "$NAMESPACE" --tail=100 -f
}

# Show next steps
show_next_steps() {
    echo
    echo_header "🚀 NEXT STEPS"
    echo "1. Get LoadBalancer IP: kubectl get svc queen -n $NAMESPACE"
    echo "2. Configure DNS: queen.strategickhaos.ai → LoadBalancer IP"
    echo "3. Verify health: curl https://queen.strategickhaos.ai/health"
    echo "4. Configure secrets with real values in bootstrap/k8s/queen/secrets.yaml"
    echo "5. Enable TLS via Google-managed certificate"
    echo
    echo "Useful commands:"
    echo "  - View pods: kubectl get pods -n $NAMESPACE"
    echo "  - View logs: kubectl logs -l app=strategickhaos-queen -n $NAMESPACE"
    echo "  - Scale:     kubectl scale deployment/queen --replicas=3 -n $NAMESPACE"
    echo "  - HPA status: kubectl get hpa -n $NAMESPACE"
    echo
}

# Main execution
main() {
    echo_header "👑 STRATEGICKHAOS QUEEN DEPLOYMENT"
    echo "Cluster: $CLUSTER ($PROJECT)"
    echo "Region:  $REGION"
    echo "Target:  34.29.28.27"
    echo
    
    check_prerequisites
    connect_cluster
    deploy_queen
    wait_for_deployment
    get_loadbalancer_ip
    verify_deployment
    show_next_steps
    
    echo_success "Queen deployment complete! 🎉"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "verify")
        check_prerequisites
        connect_cluster
        verify_deployment
        ;;
    "clean")
        check_prerequisites
        connect_cluster
        clean_deployment
        ;;
    "logs")
        check_prerequisites
        connect_cluster
        show_logs
        ;;
    "ip")
        check_prerequisites
        connect_cluster
        get_loadbalancer_ip
        ;;
    *)
        echo "Usage: $0 [deploy|verify|clean|logs|ip]"
        echo ""
        echo "Commands:"
        echo "  deploy  - Deploy Queen to GKE (default)"
        echo "  verify  - Verify existing deployment"
        echo "  clean   - Remove Queen deployment"
        echo "  logs    - Tail Queen logs"
        echo "  ip      - Get LoadBalancer IP"
        exit 1
        ;;
esac
