#!/bin/bash
# ============================================================================
# SOVEREIGN EMPIRE DEPLOYMENT SCRIPT
# One-command deployment for complete Docker sovereignty
# ============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
EMPIRE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS_DIR="${EMPIRE_ROOT}/logs/empire"
BACKUP_DIR="${EMPIRE_ROOT}/backups"
CONFIG_DIR="${EMPIRE_ROOT}/config"

# Ensure directories exist
mkdir -p "${LOGS_DIR}" "${BACKUP_DIR}" "${CONFIG_DIR}"

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "ERROR")   echo -e "${RED}[$timestamp] [ERROR] $message${NC}" ;;
        "WARN")    echo -e "${YELLOW}[$timestamp] [WARN] $message${NC}" ;;
        "SUCCESS") echo -e "${GREEN}[$timestamp] [SUCCESS] $message${NC}" ;;
        "INFO")    echo -e "${CYAN}[$timestamp] [INFO] $message${NC}" ;;
        *)         echo -e "${NC}[$timestamp] [$level] $message${NC}" ;;
    esac
    
    # Also log to file
    echo "[$timestamp] [$level] $message" >> "${LOGS_DIR}/deployment-$(date '+%Y-%m-%d').log"
}

# Banner
show_banner() {
    echo -e "${PURPLE}"
    cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║               SOVEREIGN DOCKER EMPIRE DEPLOYMENT                      ║
║                    Complete Autonomous Infrastructure                 ║
║                                                                       ║
║  █████╗ ██╗   ██╗████████╗ ██████╗ ███╗   ██╗ ██████╗ ███╗   ███╗   ║
║ ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗████╗  ██║██╔═══██╗████╗ ████║   ║
║ ███████║██║   ██║   ██║   ██║   ██║██╔██╗ ██║██║   ██║██╔████╔██║   ║
║ ██╔══██║██║   ██║   ██║   ██║   ██║██║╚██╗██║██║   ██║██║╚██╔╝██║   ║
║ ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║ ╚████║╚██████╔╝██║ ╚═╝ ██║   ║
║ ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝   ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Prerequisites check
check_prerequisites() {
    log "INFO" "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log "ERROR" "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log "ERROR" "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log "ERROR" "Docker daemon is not running"
        exit 1
    fi
    
    # Check required files
    local required_files=(
        "docker-compose.unified-empire.yml"
        ".env.empire"
        "automate-sovereign-empire.ps1"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log "ERROR" "Required file missing: $file"
            exit 1
        fi
    done
    
    log "SUCCESS" "All prerequisites met"
}

# System resource check
check_resources() {
    log "INFO" "Checking system resources..."
    
    # Check available memory (minimum 8GB recommended)
    local mem_total=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $mem_total -lt 8 ]]; then
        log "WARN" "System has ${mem_total}GB RAM. Minimum 8GB recommended for full deployment"
    else
        log "SUCCESS" "Memory check passed: ${mem_total}GB available"
    fi
    
    # Check available disk space (minimum 50GB recommended)
    local disk_avail=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $disk_avail -lt 50 ]]; then
        log "WARN" "Available disk space: ${disk_avail}GB. Minimum 50GB recommended"
    else
        log "SUCCESS" "Disk space check passed: ${disk_avail}GB available"
    fi
    
    # Check CPU cores
    local cpu_cores=$(nproc)
    log "INFO" "CPU cores available: $cpu_cores"
}

# Network setup
setup_networks() {
    log "INFO" "Setting up Docker networks..."
    
    local networks=("empire-internal" "empire-secure" "empire-public")
    
    for network in "${networks[@]}"; do
        if docker network ls | grep -q "$network"; then
            log "INFO" "Network $network already exists"
        else
            log "INFO" "Creating network: $network"
            case "$network" in
                "empire-internal")
                    docker network create --driver bridge --internal \
                        --subnet 172.20.0.0/16 "$network"
                    ;;
                "empire-secure")
                    docker network create --driver bridge \
                        --subnet 172.21.0.0/16 "$network"
                    ;;
                "empire-public")
                    docker network create --driver bridge \
                        --subnet 172.22.0.0/16 "$network"
                    ;;
            esac
            log "SUCCESS" "Network $network created"
        fi
    done
}

# Build Docker images
build_images() {
    log "INFO" "Building Docker images..."
    
    # Check if Dockerfiles exist and build them
    local dockerfiles=(
        "Dockerfile.reflexshell:sovereignty-empire/reflexshell"
        "Dockerfile.legion:sovereignty-empire/legion"
        "Dockerfile.comms:sovereignty-empire/comms"
        "Dockerfile.gateway:sovereignty-empire/gateway"
        "Dockerfile.alignment:sovereignty-empire/alignment"
        "Dockerfile.refinory:sovereignty-empire/refinory"
        "Dockerfile.bot:sovereignty-empire/bot"
    )
    
    for dockerfile_tag in "${dockerfiles[@]}"; do
        IFS=':' read -r dockerfile tag <<< "$dockerfile_tag"
        
        if [[ -f "$dockerfile" ]]; then
            log "INFO" "Building $tag from $dockerfile..."
            if docker build -f "$dockerfile" -t "$tag:latest" .; then
                log "SUCCESS" "Built $tag successfully"
            else
                log "ERROR" "Failed to build $tag"
                exit 1
            fi
        else
            log "WARN" "Dockerfile not found: $dockerfile, will use base images"
        fi
    done
}

# Deploy infrastructure in stages
deploy_infrastructure() {
    log "INFO" "Deploying Sovereign Empire infrastructure..."
    
    # Stage 1: Core Infrastructure
    log "INFO" "Stage 1: Deploying core infrastructure..."
    docker-compose -f docker-compose.unified-empire.yml up -d \
        redis qdrant mongodb postgres elasticsearch
    
    log "INFO" "Waiting for core infrastructure to be ready..."
    sleep 30
    
    # Check core services health
    check_service_health "redis"
    check_service_health "qdrant"
    
    # Stage 2: Visual Cortex Systems
    log "INFO" "Stage 2: Deploying visual cortex systems..."
    docker-compose -f docker-compose.unified-empire.yml up -d \
        visual-cortex-motion visual-cortex-ocr \
        visual-cortex-watcher-1 visual-cortex-watcher-2 \
        visual-cortex-watcher-3 visual-cortex-watcher-4 \
        visual-cortex-watcher-5 visual-cortex-watcher-6
    
    sleep 20
    
    # Stage 3: Reconnaissance and Research
    log "INFO" "Stage 3: Deploying reconnaissance and research systems..."
    docker-compose -f docker-compose.unified-empire.yml up -d \
        recon-scanner recon-analyzer \
        research-swarm-1 research-swarm-2 research-swarm-3 \
        embeddings-service
    
    sleep 15
    
    # Stage 4: Core Applications
    log "INFO" "Stage 4: Deploying core applications..."
    docker-compose -f docker-compose.unified-empire.yml up -d \
        reflexshell legion comms gateway alignment refinory
    
    sleep 15
    
    # Stage 5: Automation and Factories
    log "INFO" "Stage 5: Deploying automation and factories..."
    docker-compose -f docker-compose.unified-empire.yml up -d \
        prototype-factory-1 prototype-factory-2 automation-engine \
        voting-engine-consensus voting-engine-democracy
    
    sleep 10
    
    # Stage 6: Monitoring and Security
    log "INFO" "Stage 6: Deploying monitoring and security..."
    docker-compose -f docker-compose.unified-empire.yml up -d \
        performance-monitor network-monitor security-scanner
    
    sleep 10
    
    # Stage 7: Data Processing and Analytics
    log "INFO" "Stage 7: Deploying data processing and analytics..."
    docker-compose -f docker-compose.unified-empire.yml up -d \
        data-processor analytics-engine
    
    sleep 10
    
    # Stage 8: Support Services
    log "INFO" "Stage 8: Deploying support services..."
    docker-compose -f docker-compose.unified-empire.yml up -d \
        backup-service log-aggregator
    
    log "SUCCESS" "All services deployed successfully"
}

# Service health check
check_service_health() {
    local service="$1"
    local max_attempts=30
    local attempt=1
    
    log "INFO" "Checking health of service: $service"
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose -f docker-compose.unified-empire.yml ps "$service" | grep -q "Up"; then
            log "SUCCESS" "Service $service is healthy"
            return 0
        fi
        
        log "INFO" "Waiting for $service to be ready... (attempt $attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done
    
    log "ERROR" "Service $service failed to become healthy within timeout"
    return 1
}

# Show deployment summary
show_deployment_summary() {
    log "INFO" "=== DEPLOYMENT SUMMARY ==="
    
    # Count running services
    local total_services=$(docker-compose -f docker-compose.unified-empire.yml config --services | wc -l)
    local running_services=$(docker-compose -f docker-compose.unified-empire.yml ps | grep -c "Up" || true)
    
    log "INFO" "Services Status: $running_services/$total_services running"
    
    # Show key access points
    log "INFO" "=== ACCESS POINTS ==="
    log "INFO" "Gateway (Main Entry):     http://localhost:8080"
    log "INFO" "ReflexShell:             http://localhost:8000"
    log "INFO" "Legion:                  http://localhost:8001"
    log "INFO" "Communications:          http://localhost:8002"
    log "INFO" "Embeddings Service:      http://localhost:8010"
    log "INFO" "Performance Monitor:     http://localhost:8020"
    log "INFO" "Analytics Engine:        http://localhost:8030"
    
    log "INFO" "=== DATABASES ==="
    log "INFO" "Redis:                   localhost:6379"
    log "INFO" "Qdrant Vector DB:        http://localhost:6333"
    log "INFO" "MongoDB:                 localhost:27017"
    log "INFO" "PostgreSQL:              localhost:5432"
    log "INFO" "Elasticsearch:           http://localhost:9200"
    
    # System resource usage
    log "INFO" "=== SYSTEM RESOURCES ==="
    local mem_usage=$(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')
    local disk_usage=$(df . | tail -1 | awk '{printf "%.1f%%", $3/$2 * 100.0}')
    
    log "INFO" "Memory Usage:            $mem_usage"
    log "INFO" "Disk Usage:              $disk_usage"
    
    # Container stats
    log "INFO" "=== CONTAINER STATISTICS ==="
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -10
}

# Monitoring setup
setup_monitoring() {
    log "INFO" "Setting up monitoring and alerts..."
    
    # Create monitoring scripts directory
    mkdir -p "${CONFIG_DIR}/monitoring"
    
    # Create system monitoring script
    cat > "${CONFIG_DIR}/monitoring/system_check.sh" << 'EOF'
#!/bin/bash
# System health monitoring script

LOG_FILE="/app/logs/system-monitor.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Memory check
MEM_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
if (( $(echo "$MEM_USAGE > 85" | bc -l) )); then
    echo "[$TIMESTAMP] ALERT: High memory usage: ${MEM_USAGE}%" >> "$LOG_FILE"
fi

# Disk check
DISK_USAGE=$(df . | tail -1 | awk '{printf "%.1f", $3/$2 * 100.0}')
if (( $(echo "$DISK_USAGE > 90" | bc -l) )); then
    echo "[$TIMESTAMP] ALERT: High disk usage: ${DISK_USAGE}%" >> "$LOG_FILE"
fi

# Service check
SERVICES_DOWN=$(docker-compose -f /app/docker-compose.unified-empire.yml ps | grep -c "Exit" || true)
if [[ $SERVICES_DOWN -gt 0 ]]; then
    echo "[$TIMESTAMP] ALERT: $SERVICES_DOWN services are down" >> "$LOG_FILE"
fi

echo "[$TIMESTAMP] System check completed. Memory: ${MEM_USAGE}%, Disk: ${DISK_USAGE}%, Services down: $SERVICES_DOWN" >> "$LOG_FILE"
EOF

    chmod +x "${CONFIG_DIR}/monitoring/system_check.sh"
    log "SUCCESS" "Monitoring setup completed"
}

# Security hardening
apply_security_hardening() {
    log "INFO" "Applying security hardening..."
    
    # Set proper file permissions
    chmod 600 .env.empire
    chmod 700 "${LOGS_DIR}"
    chmod 700 "${BACKUP_DIR}"
    
    # Create security configuration
    mkdir -p "${CONFIG_DIR}/security"
    
    cat > "${CONFIG_DIR}/security/firewall_rules.txt" << 'EOF'
# Empire Docker Firewall Rules
# Only allow localhost access to sensitive services

# Redis - localhost only
-A INPUT -p tcp --dport 6379 -s 127.0.0.1 -j ACCEPT
-A INPUT -p tcp --dport 6379 -j REJECT

# Databases - localhost only
-A INPUT -p tcp --dport 5432 -s 127.0.0.1 -j ACCEPT
-A INPUT -p tcp --dport 5432 -j REJECT
-A INPUT -p tcp --dport 27017 -s 127.0.0.1 -j ACCEPT
-A INPUT -p tcp --dport 27017 -j REJECT

# Elasticsearch - localhost only
-A INPUT -p tcp --dport 9200 -s 127.0.0.1 -j ACCEPT
-A INPUT -p tcp --dport 9200 -j REJECT
EOF

    log "SUCCESS" "Security hardening applied"
}

# Cleanup function
cleanup() {
    if [[ $? -ne 0 ]]; then
        log "ERROR" "Deployment failed. Running cleanup..."
        docker-compose -f docker-compose.unified-empire.yml down 2>/dev/null || true
    fi
}

# Main deployment function
main() {
    show_banner
    
    trap cleanup EXIT
    
    log "INFO" "Starting Sovereign Empire deployment..."
    
    check_prerequisites
    check_resources
    setup_networks
    
    # Build images if requested
    if [[ "${1:-}" == "--build" ]] || [[ "${BUILD_IMAGES:-false}" == "true" ]]; then
        build_images
    fi
    
    deploy_infrastructure
    setup_monitoring
    apply_security_hardening
    
    log "SUCCESS" "Waiting for all services to stabilize..."
    sleep 30
    
    show_deployment_summary
    
    log "SUCCESS" "=== SOVEREIGN EMPIRE DEPLOYMENT COMPLETED ==="
    log "INFO" "Access the main gateway at: http://localhost:8080"
    log "INFO" "View logs in: $LOGS_DIR"
    log "INFO" "Monitor with: docker-compose -f docker-compose.unified-empire.yml logs -f"
    log "INFO" "Stop with: docker-compose -f docker-compose.unified-empire.yml down"
}

# Command line argument handling
case "${1:-deploy}" in
    "deploy")
        main "$@"
        ;;
    "status")
        show_deployment_summary
        ;;
    "stop")
        log "INFO" "Stopping Sovereign Empire..."
        docker-compose -f docker-compose.unified-empire.yml down
        log "SUCCESS" "Empire stopped"
        ;;
    "restart")
        log "INFO" "Restarting Sovereign Empire..."
        docker-compose -f docker-compose.unified-empire.yml down
        sleep 5
        main "deploy"
        ;;
    "logs")
        docker-compose -f docker-compose.unified-empire.yml logs -f
        ;;
    "build")
        check_prerequisites
        build_images
        ;;
    "reset")
        log "WARN" "This will destroy all data. Are you sure? (y/N)"
        read -r confirmation
        if [[ "$confirmation" =~ ^[Yy]$ ]]; then
            log "INFO" "Resetting Empire..."
            docker-compose -f docker-compose.unified-empire.yml down -v --remove-orphans
            docker system prune -f
            log "SUCCESS" "Empire reset completed"
        else
            log "INFO" "Reset cancelled"
        fi
        ;;
    "help"|"--help"|"-h")
        cat << 'EOF'
SOVEREIGN EMPIRE DEPLOYMENT SCRIPT

USAGE:
  ./deploy-empire.sh [COMMAND]

COMMANDS:
  deploy     Deploy the complete sovereign empire (default)
  status     Show current deployment status
  stop       Stop all empire services
  restart    Restart the complete empire
  logs       Follow logs from all services
  build      Build Docker images only
  reset      Complete reset (destroys all data)
  help       Show this help message

OPTIONS:
  --build    Build images before deploying

EXAMPLES:
  ./deploy-empire.sh deploy --build
  ./deploy-empire.sh status
  ./deploy-empire.sh logs

EOF
        ;;
    *)
        log "ERROR" "Unknown command: $1"
        log "INFO" "Use './deploy-empire.sh help' for usage information"
        exit 1
        ;;
esac