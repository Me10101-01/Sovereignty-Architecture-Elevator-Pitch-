#!/bin/bash
# empire-recon.sh - SovereignMesh Empire Reconnaissance Script
# Maps your entire multi-cloud AI agent infrastructure
#
# Usage: ./empire-recon.sh [--full|--quick|--json]
#
# Options:
#   --full    Complete reconnaissance including all pods and services
#   --quick   Quick status check (default)
#   --json    Output in JSON format for automation

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
MODE="${1:---quick}"
JSON_OUTPUT=false
if [[ "$MODE" == "--json" ]]; then
    JSON_OUTPUT=true
fi

# Header
print_header() {
    if [[ "$JSON_OUTPUT" == true ]]; then
        return
    fi
    echo -e "${PURPLE}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║        🧠✨ SovereignMesh Empire Reconnaissance              ║"
    echo "║           Multi-AI Agent Infrastructure Map                   ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo -e "Timestamp: ${CYAN}$(date -u +"%Y-%m-%dT%H:%M:%SZ")${NC}"
    echo -e "Mode: ${YELLOW}${MODE}${NC}"
    echo ""
}

# Section divider
section() {
    if [[ "$JSON_OUTPUT" == true ]]; then
        return
    fi
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🔍 $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Warning message
warn() {
    if [[ "$JSON_OUTPUT" == true ]]; then
        return
    fi
    echo -e "  ${YELLOW}⚠️  $1${NC}"
}

# Success message
success() {
    if [[ "$JSON_OUTPUT" == true ]]; then
        return
    fi
    echo -e "  ${GREEN}✅ $1${NC}"
}

# Check if command exists
cmd_exists() {
    command -v "$1" &> /dev/null
}

# GCP Project Discovery
gcp_projects() {
    section "GCP Projects"
    if cmd_exists gcloud; then
        if gcloud projects list --format="table(projectId,name,projectNumber)" 2>/dev/null; then
            success "GCP projects retrieved"
        else
            warn "Failed to list GCP projects (auth may be required)"
        fi
    else
        warn "gcloud CLI not installed"
    fi
    echo ""
}

# GKE Cluster Discovery
gke_clusters() {
    section "GKE Clusters"
    if cmd_exists gcloud; then
        if gcloud container clusters list --format="table(name,location,status,currentMasterVersion,currentNodeCount)" 2>/dev/null; then
            success "GKE clusters retrieved"
        else
            warn "No GKE clusters found or auth required"
        fi
    else
        warn "gcloud CLI not installed"
    fi
    echo ""
}

# Kubernetes Context
k8s_context() {
    section "Kubernetes Context"
    if cmd_exists kubectl; then
        echo -e "  Current Context: ${CYAN}$(kubectl config current-context 2>/dev/null || echo 'Not set')${NC}"
        echo -e "  Cluster: ${CYAN}$(kubectl config view --minify -o jsonpath='{.clusters[0].name}' 2>/dev/null || echo 'Unknown')${NC}"
        echo ""
    else
        warn "kubectl not installed"
    fi
}

# Kubernetes Namespaces
k8s_namespaces() {
    section "Kubernetes Namespaces"
    if cmd_exists kubectl; then
        if kubectl get namespaces 2>/dev/null; then
            success "Namespaces retrieved"
        else
            warn "Cannot reach Kubernetes cluster"
        fi
    else
        warn "kubectl not installed"
    fi
    echo ""
}

# Pod Inventory
k8s_pods() {
    section "Pod Inventory (All Namespaces)"
    if cmd_exists kubectl; then
        local pods_output running_count
        pods_output=$(kubectl get pods -A --no-headers 2>/dev/null || echo "")
        if [ -n "$pods_output" ]; then
            TOTAL_PODS=$(echo "$pods_output" | wc -l | tr -d ' ')
            RUNNING_PODS=$(echo "$pods_output" | grep -c "Running" || echo "0")
        else
            TOTAL_PODS="0"
            RUNNING_PODS="0"
        fi
        echo -e "  Total Pods: ${CYAN}${TOTAL_PODS}${NC}"
        echo -e "  Running: ${GREEN}${RUNNING_PODS}${NC}"
        echo ""
        
        if [[ "$MODE" == "--full" ]]; then
            kubectl get pods -A -o wide 2>/dev/null || warn "Cannot retrieve pod details"
        else
            echo "  (Use --full for complete pod list)"
            kubectl get pods -A -o wide 2>/dev/null | head -15 || warn "Cannot retrieve pods"
        fi
    else
        warn "kubectl not installed"
    fi
    echo ""
}

# Service Endpoints
k8s_services() {
    section "Service Endpoints"
    if cmd_exists kubectl; then
        if [[ "$MODE" == "--full" ]]; then
            kubectl get svc -A 2>/dev/null || warn "Cannot retrieve services"
        else
            kubectl get svc -A 2>/dev/null | head -15 || warn "Cannot retrieve services"
            echo "  (Use --full for complete service list)"
        fi
    else
        warn "kubectl not installed"
    fi
    echo ""
}

# Node Health
k8s_nodes() {
    section "Node Health"
    if cmd_exists kubectl; then
        if kubectl get nodes -o wide 2>/dev/null; then
            success "Node status retrieved"
        else
            warn "Cannot retrieve node status"
        fi
    else
        warn "kubectl not installed"
    fi
    echo ""
}

# Resource Usage
k8s_resources() {
    section "Resource Usage"
    if cmd_exists kubectl; then
        echo -e "${CYAN}Node Resources:${NC}"
        kubectl top nodes 2>/dev/null || warn "Metrics server not available"
        echo ""
        echo -e "${CYAN}Top Pod Consumers:${NC}"
        kubectl top pods -A --sort-by=memory 2>/dev/null | head -10 || warn "Metrics server not available"
    else
        warn "kubectl not installed"
    fi
    echo ""
}

# Local Docker Services
docker_services() {
    section "Local Docker Services"
    if cmd_exists docker; then
        CONTAINER_COUNT=$(docker ps -q 2>/dev/null | wc -l || echo "0")
        echo -e "  Running Containers: ${CYAN}${CONTAINER_COUNT}${NC}"
        echo ""
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null | head -15 || warn "Docker not running"
    else
        warn "Docker not installed"
    fi
    echo ""
}

# AI Agent Status
ai_agents() {
    section "AI Agent Integration Points"
    echo -e "  ${PURPLE}Cloud AI Agents:${NC}"
    echo "    • Gemini CLI    → GCP Cloud Shell / MCP Protocol"
    echo "    • Amazon Q      → VSCode Extension / Kiro.dev"
    echo "    • GitHub Copilot → Codespaces / PR Review"
    echo "    • Claude        → Architecture / Mobile"
    echo "    • Grok          → Real-time Analysis / xAI API"
    echo ""
    echo -e "  ${PURPLE}Local AI Agents:${NC}"
    if cmd_exists ollama; then
        echo "    • Ollama: $(ollama list 2>/dev/null | tail -n +2 | wc -l) models available"
        ollama list 2>/dev/null | head -5 || warn "Ollama not responding"
    else
        echo "    • Ollama: Not installed"
    fi
    echo ""
}

# AWS Context (if configured)
aws_context() {
    section "AWS Context"
    if cmd_exists aws; then
        if aws sts get-caller-identity 2>/dev/null; then
            success "AWS identity retrieved"
        else
            warn "AWS not configured or auth expired"
        fi
    else
        warn "AWS CLI not installed"
    fi
    echo ""
}

# Summary
print_summary() {
    section "Empire Summary"
    echo -e "  ${GREEN}GCP${NC}:    $(gcloud config get-value project 2>/dev/null || echo 'Not configured')"
    echo -e "  ${GREEN}K8s${NC}:    $(kubectl config current-context 2>/dev/null || echo 'Not configured')"
    echo -e "  ${GREEN}AWS${NC}:    $(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo 'Not configured')"
    echo -e "  ${GREEN}Docker${NC}: $(docker ps -q 2>/dev/null | wc -l || echo '0') containers"
    echo ""
    echo -e "${PURPLE}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║           🎯 Empire Reconnaissance Complete                   ║${NC}"
    echo -e "${PURPLE}╚═══════════════════════════════════════════════════════════════╝${NC}"
}

# JSON Output Mode
json_output() {
    local timestamp gcp_project k8s_context aws_account docker_count pod_count node_count
    
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    gcp_project=$(gcloud config get-value project 2>/dev/null || echo "")
    k8s_context=$(kubectl config current-context 2>/dev/null || echo "")
    aws_account=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "")
    docker_count=$(docker ps -q 2>/dev/null | wc -l | tr -d ' ' || echo "0")
    pod_count=$(kubectl get pods -A --no-headers 2>/dev/null | wc -l | tr -d ' ' || echo "0")
    node_count=$(kubectl get nodes --no-headers 2>/dev/null | wc -l | tr -d ' ' || echo "0")
    
    # Handle empty strings
    [ -z "$gcp_project" ] && gcp_project="null"
    [ -z "$k8s_context" ] && k8s_context="null"
    [ -z "$aws_account" ] && aws_account="null"
    [ -z "$docker_count" ] && docker_count="0"
    [ -z "$pod_count" ] && pod_count="0"
    [ -z "$node_count" ] && node_count="0"
    
    echo "{"
    echo "  \"timestamp\": \"${timestamp}\","
    echo "  \"gcp_project\": \"${gcp_project}\","
    echo "  \"k8s_context\": \"${k8s_context}\","
    echo "  \"aws_account\": \"${aws_account}\","
    echo "  \"docker_containers\": ${docker_count},"
    echo "  \"k8s_pods\": ${pod_count},"
    echo "  \"k8s_nodes\": ${node_count}"
    echo "}"
}

# Main execution
main() {
    if [[ "$JSON_OUTPUT" == true ]]; then
        json_output
        exit 0
    fi

    print_header
    gcp_projects
    gke_clusters
    k8s_context
    k8s_namespaces
    k8s_pods
    k8s_services
    k8s_nodes
    
    if [[ "$MODE" == "--full" ]]; then
        k8s_resources
        aws_context
    fi
    
    docker_services
    ai_agents
    print_summary
}

# Run
main
