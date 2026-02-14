#!/bin/bash
# LEGION CURL ARSENAL — 30 Recon Patterns
# Strategickhaos DAO LLC | Node 137
# Output: /data/legion_report.md + JSON

REPORT="/data/legion/legion_report.md"
JSON="/data/legion/legion_report.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

mkdir -p /data/legion

echo "🏛️ LEGION OF MINDS — FULL RECON REPORT" > $REPORT
echo "Generated: $TIMESTAMP" >> $REPORT
echo "Operator: Domenic Garza (@strategickhaos)" >> $REPORT
echo "===================================================================" >> $REPORT
echo "" >> $REPORT

# Initialize JSON report
echo '{"timestamp":"'$TIMESTAMP'","patterns":[' > $JSON

run_pattern() {
    local name="$1"
    local url="$2"
    local selector="$3"
    local description="$4"
    
    echo "📡 PATTERN: $name" >> $REPORT
    echo "URL: $url" >> $REPORT
    echo "DESC: $description" >> $REPORT
    echo "-------------------------------------------------------------------" >> $REPORT
    
    # Execute curl and parse
    if [[ "$selector" == *"pup"* ]]; then
        curl -Ls "$url" 2>/dev/null | eval "$selector" >> $REPORT 2>/dev/null || echo "❌ Failed to fetch $name" >> $REPORT
    elif [[ "$selector" == *"jq"* ]]; then
        curl -Ls "$url" 2>/dev/null | eval "$selector" >> $REPORT 2>/dev/null || echo "❌ Failed to fetch $name" >> $REPORT
    else
        curl -Ls "$url" >> $REPORT 2>/dev/null || echo "❌ Failed to fetch $name" >> $REPORT
    fi
    
    echo "" >> $REPORT
    echo "" >> $REPORT
}

# === 30 RECON PATTERNS ===

# 1. GitHub Enterprise Terms
run_pattern "GitHub Enterprise Terms" \
    "https://docs.github.com/site-policy/github-terms/github-customer-terms" \
    "pup 'main text{}' | head -50" \
    "Enterprise licensing terms and conditions"

# 2. JetBrains EULA
run_pattern "JetBrains EULA" \
    "https://www.jetbrains.com/legal/docs/toolbox/user_eula/" \
    "pup '.content text{}' | head -50" \
    "JetBrains end user license agreement"

# 3. Obsidian Commercial License
run_pattern "Obsidian License" \
    "https://obsidian.md/license" \
    "pup 'main text{}' | head -50" \
    "Obsidian commercial usage terms"

# 4. Harbor Registry Terms
run_pattern "Harbor Registry" \
    "https://github.com/goharbor/harbor/blob/main/LICENSE" \
    "pup 'pre text{}' | head -30" \
    "Harbor container registry license"

# 5. SPDX License Database
run_pattern "SPDX Licenses" \
    "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json" \
    "jq '.licenses[] | select(.isOsiApproved == true) | .licenseId' | head -20" \
    "OSI approved open source licenses"

# 6. Docker Hub Terms
run_pattern "Docker Hub Terms" \
    "https://www.docker.com/legal/docker-terms-service/" \
    "pup '.content text{}' | head -40" \
    "Docker Hub service terms"

# 7. AWS Service Terms
run_pattern "AWS Service Terms" \
    "https://aws.amazon.com/service-terms/" \
    "pup 'main text{}' | head -40" \
    "Amazon Web Services terms"

# 8. Microsoft Azure Terms
run_pattern "Azure Terms" \
    "https://azure.microsoft.com/en-us/support/legal/" \
    "pup 'main text{}' | head -40" \
    "Microsoft Azure legal terms"

# 9. Google Cloud Terms
run_pattern "GCP Terms" \
    "https://cloud.google.com/terms/" \
    "pup 'main text{}' | head -40" \
    "Google Cloud Platform terms"

# 10. Kubernetes License
run_pattern "Kubernetes License" \
    "https://raw.githubusercontent.com/kubernetes/kubernetes/master/LICENSE" \
    "head -30" \
    "Kubernetes orchestration license"

# 11. Terraform License
run_pattern "Terraform License" \
    "https://raw.githubusercontent.com/hashicorp/terraform/main/LICENSE" \
    "head -30" \
    "HashiCorp Terraform license"

# 12. Ansible License
run_pattern "Ansible License" \
    "https://raw.githubusercontent.com/ansible/ansible/devel/COPYING" \
    "head -30" \
    "Red Hat Ansible license"

# 13. Prometheus License
run_pattern "Prometheus License" \
    "https://raw.githubusercontent.com/prometheus/prometheus/main/LICENSE" \
    "head -30" \
    "Prometheus monitoring license"

# 14. Grafana License
run_pattern "Grafana License" \
    "https://raw.githubusercontent.com/grafana/grafana/main/LICENSE" \
    "head -30" \
    "Grafana visualization license"

# 15. Elasticsearch License
run_pattern "Elasticsearch License" \
    "https://raw.githubusercontent.com/elastic/elasticsearch/main/LICENSE.txt" \
    "head -30" \
    "Elastic search and analytics license"

# 16. PostgreSQL License
run_pattern "PostgreSQL License" \
    "https://raw.githubusercontent.com/postgres/postgres/master/COPYRIGHT" \
    "head -30" \
    "PostgreSQL database license"

# 17. Redis License
run_pattern "Redis License" \
    "https://raw.githubusercontent.com/redis/redis/unstable/COPYING" \
    "head -30" \
    "Redis in-memory database license"

# 18. MongoDB License
run_pattern "MongoDB License" \
    "https://raw.githubusercontent.com/mongodb/mongo/master/LICENSE-Community.txt" \
    "head -30" \
    "MongoDB document database license"

# 19. Apache HTTP Server License
run_pattern "Apache License" \
    "https://raw.githubusercontent.com/apache/httpd/trunk/LICENSE" \
    "head -30" \
    "Apache HTTP Server license"

# 20. Nginx License
run_pattern "Nginx License" \
    "https://raw.githubusercontent.com/nginx/nginx/master/docs/text/LICENSE" \
    "head -30" \
    "Nginx web server license"

# 21. Node.js License
run_pattern "Node.js License" \
    "https://raw.githubusercontent.com/nodejs/node/main/LICENSE" \
    "head -30" \
    "Node.js runtime license"

# 22. Python License
run_pattern "Python License" \
    "https://raw.githubusercontent.com/python/cpython/main/LICENSE" \
    "head -30" \
    "Python programming language license"

# 23. Go License
run_pattern "Go License" \
    "https://raw.githubusercontent.com/golang/go/master/LICENSE" \
    "head -30" \
    "Go programming language license"

# 24. Rust License
run_pattern "Rust License" \
    "https://raw.githubusercontent.com/rust-lang/rust/master/LICENSE-APACHE" \
    "head -30" \
    "Rust programming language license"

# 25. VS Code License
run_pattern "VS Code License" \
    "https://raw.githubusercontent.com/microsoft/vscode/main/LICENSE.txt" \
    "head -30" \
    "Visual Studio Code editor license"

# 26. Git License
run_pattern "Git License" \
    "https://raw.githubusercontent.com/git/git/master/COPYING" \
    "head -30" \
    "Git version control license"

# 27. Linux Kernel License
run_pattern "Linux Kernel License" \
    "https://raw.githubusercontent.com/torvalds/linux/master/COPYING" \
    "head -30" \
    "Linux kernel license"

# 28. OpenSSL License
run_pattern "OpenSSL License" \
    "https://raw.githubusercontent.com/openssl/openssl/master/LICENSE.txt" \
    "head -30" \
    "OpenSSL cryptography license"

# 29. Curl License
run_pattern "Curl License" \
    "https://raw.githubusercontent.com/curl/curl/master/COPYING" \
    "head -30" \
    "Curl HTTP client license"

# 30. Vim License
run_pattern "Vim License" \
    "https://raw.githubusercontent.com/vim/vim/master/LICENSE" \
    "head -30" \
    "Vim text editor license"

# Close JSON array
echo ']}' >> $JSON

echo "===================================================================" >> $REPORT
echo "🎯 LEGION RECON COMPLETE" >> $REPORT
echo "Total Patterns Executed: 30" >> $REPORT
echo "Report Location: $REPORT" >> $REPORT
echo "JSON Data: $JSON" >> $REPORT
echo "Timestamp: $TIMESTAMP" >> $REPORT

echo "🏛️ LEGION OF MINDS — RECON COMPLETE"
echo "📊 Report generated: $REPORT"
echo "📋 JSON data: $JSON"