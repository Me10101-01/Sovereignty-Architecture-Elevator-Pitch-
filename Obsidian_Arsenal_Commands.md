# Obsidian Arsenal Commands & Network Antibodies Integration

## 🛡️ NETWORK AUTHENTICATION ANTIBODIES

### GitKraken API 401 Unauthorized Errors

**Threat Analysis:**
- **Type:** API Authentication Failure
- **Pattern:** `GET https://gitkraken.dev/api/user 401 (Unauthorized)`
- **Impact:** MEDIUM - Blocks GitKraken functionality
- **Root Cause:** Missing or expired API token

**Antibody Commands:**
```bash
# Test GitKraken API with authentication
curl -H "Authorization: Bearer $GITKRAKEN_TOKEN" https://gitkraken.dev/api/user

# Configure GitKraken token globally
git config --global gitkraken.token "$GITKRAKEN_TOKEN"

# Verify endpoint availability
curl -I https://gitkraken.dev/api/user

# Check GitKraken account settings
echo "Navigate to GitKraken → Settings → API → Generate Token"
```

**Success Indicators:**
- HTTP/1.1 200 OK response
- User data returned in JSON format
- Token validation successful

### DNS Resolution & Resource Loading Failures

**Threat Analysis:**
- **Type:** Network Connectivity Issues
- **Pattern:** `Failed to load resource: net::ERR_NAME_NOT_RESOLVED`
- **Impact:** LOW - Cosmetic issues, missing assets
- **Root Cause:** DNS resolution or network connectivity

**Antibody Commands:**
```bash
# DNS resolution testing
nslookup gitkraken.dev
dig gitkraken.dev

# Network connectivity testing  
ping -c 4 gitkraken.dev
traceroute gitkraken.dev

# Check DNS configuration
systemd-resolve --status
cat /etc/resolv.conf

# Test specific endpoints
curl -I https://gitkraken.dev/monitoring
```

## 🧠 OBSIDIAN CANVAS INTEGRATION COMMANDS

### Primary Arsenal Access
```
obsidian://open?vault=AI_Brain_Unity&file=Untitled.canvas
```

### Node Creation Commands
```
# Create Network Antibody Node
obsidian://new?vault=AI_Brain_Unity&name=Network_Antibodies_{{date:YYYY-MM-DD}}

# Create GitKraken API Mitigation Node  
obsidian://new?vault=AI_Brain_Unity&name=GitKraken_API_Mitigation

# Create DNS Resolution Antibody Node
obsidian://new?vault=AI_Brain_Unity&name=DNS_Resolution_Antibodies

# Quick Threat Analysis Template
obsidian://new?vault=AI_Brain_Unity&name=Threat_{{time:HH-mm}}&content=%23%20New%20Threat%20Analysis%0A%0A%23%23%20Threat%20Details%0A-%20**Type%3A**%20%0A-%20**Impact%3A**%20%0A-%20**Antibody%3A**%20%0A%0A%23%23%20Commands%0A%60%60%60bash%0A%0A%60%60%60
```

### Search & Discovery Commands
```
# Search for existing antibodies
obsidian://search?vault=AI_Brain_Unity&query=antibody%20OR%20mitigation

# Search for network-related entries
obsidian://search?vault=AI_Brain_Unity&query=network%20OR%20api

# Search for GitKraken-specific content
obsidian://search?vault=AI_Brain_Unity&query=gitkraken%20OR%20git
```

### Advanced Canvas Operations
```
# Create new canvas file
obsidian://advanced-uri?vault=AI_Brain_Unity&commandid=canvas%3Anew-file

# Open graph view for connections
obsidian://advanced-uri?vault=AI_Brain_Unity&commandid=graph%3Aopen-local

# Get hook address (if Hook app installed)
obsidian://hook-get-address?vault=AI_Brain_Unity
```

## 📊 CANVAS NODE STRUCTURE

### Network Antibodies Node
```json
{
  "id": "network_antibodies_001",
  "type": "text", 
  "text": "# Network Authentication Antibodies\n\n## GitKraken API 401 Errors\n- **Threat:** Unauthorized API access\n- **Antibody:** Token refresh and validation\n- **Command:** curl -H \"Authorization: Bearer $TOKEN\" api/user\n\n## DNS Resolution Failures\n- **Threat:** Resource loading failures  \n- **Antibody:** DNS troubleshooting and fallbacks\n- **Command:** nslookup gitkraken.dev && ping gitkraken.dev",
  "position": {"x": 0, "y": 0},
  "size": {"width": 400, "height": 300}
}
```

### Command Center Node
```json
{
  "id": "command_center_003",
  "type": "group",
  "label": "LEGION Command Center",
  "position": {"x": 0, "y": 350}, 
  "size": {"width": 800, "height": 200}
}
```

## 🎯 AUTOMATED DEPLOYMENT

### Bash Script Integration
```bash
#!/bin/bash
# Deploy antibodies to Obsidian canvas

VAULT="AI_Brain_Unity"
CANVAS_FILE="Untitled.canvas"

# Open main canvas
open "obsidian://open?vault=$VAULT&file=$CANVAS_FILE"

# Create new antibody nodes
open "obsidian://new?vault=$VAULT&name=Network_Antibodies_$(date +%Y-%m-%d)"
open "obsidian://new?vault=$VAULT&name=GitKraken_API_Fix_$(date +%H-%M)"

# Search for related content
open "obsidian://search?vault=$VAULT&query=antibody+OR+network"
```

### PowerShell Integration (Windows)
```powershell
# Deploy to Obsidian via PowerShell
$vault = "AI_Brain_Unity"
$canvas = "Untitled.canvas"

Start-Process "obsidian://open?vault=$vault&file=$canvas"
Start-Process "obsidian://new?vault=$vault&name=Network_Antibodies_$(Get-Date -Format 'yyyy-MM-dd')"
```

## 📚 ARSENAL THESAURUS MAPPINGS

### Network Terms
- **Antibody** → countermeasure, mitigation, remedy, antidote, neutralizer
- **API** → interface, endpoint, service_layer, integration_point  
- **Authentication** → verification, validation, credential_check
- **Network** → connectivity, infrastructure, communication_layer

### Obsidian Terms
- **Canvas** → knowledge_graph, mind_map, visual_workspace
- **Vault** → knowledge_base, repository, information_store
- **Node** → information_unit, knowledge_element, concept_block
- **URI** → deep_link, automation_trigger, protocol_scheme