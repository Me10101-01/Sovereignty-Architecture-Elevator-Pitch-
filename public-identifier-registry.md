# PUBLIC IDENTIFIER REGISTRY

## Strategickhaos DAO LLC — Verified Identity & Credential Bundle

**Document ID:** `PUB-ID-2025-001`  
**Version:** `2.1.0`  
**Last Updated:** December 3, 2025  
**Verification Status:** ✅ VERIFIED  

---

## 1. Legal Entity Registry

### 1.1 — Strategickhaos DAO LLC (Primary)

```yaml
entity:
  legal_name: "Strategickhaos DAO LLC"
  type: "Decentralized Autonomous Organization LLC"
  jurisdiction: "Wyoming, United States"
  governing_statute: "W.S. §17-31-101 et seq."
  
filing:
  date: "June 25, 2025 at 2:08 PM"
  entity_id: "2025-001708194"
  effective_date: "July 4, 2025"
  duration: "Perpetual"
  status: "Active"
  
tax:
  ein: "39-2900295"
  irs_notice: "CP 575 G"
  notice_date: "June 26, 2025"
  
addresses:
  principal: "1216 S Fredonia St, Longview, TX 75602"
  registered_agent:
    name: "Northwest Registered Agent LLC"
    address: "30 N Gould St Ste N, Sheridan, WY 82801"
    
trade_names:
  - "ValorYield Engine"
```

### 1.2 — ValorYield Engine (Nonprofit)

```yaml
entity:
  legal_name: "ValorYield Engine"
  type: "Public Benefit Nonprofit Corporation"
  jurisdiction: "Wyoming"
  
filing:
  date: "June 25, 2025 at 3:49 PM"
  entity_id: "2025-001708312"
  has_members: false
  status: "Active"
  
tax:
  ein: "39-2923503"
  irs_notice: "CP 575 E"
  notice_date: "June 27, 2025"
  501c3_status: "Pending (Form 1023/1023-EZ required)"
  
mission: |
  AI-driven dividend allocation system that pays vehicle and 
  housing expenses for veterans and underserved communities.
```

### 1.3 — Skyline Strategies (Louisiana)

```yaml
entity:
  legal_name: "Skyline Strategies Rope Access & Rescue Production LLC"
  type: "LLC"
  jurisdiction: "Louisiana"
  
filing:
  date: "May 7, 2024"
  status: "Active"
  
tax:
  ein: "99-2899134"
  irs_notice: "CP 575 G"
  
address: "702 E School St Ste B103, Lake Charles, LA 70607"
industry: "Industrial rope access, rescue, services"
```

### 1.4 — Garza's Organic Greens (Texas)

```yaml
entity:
  legal_name: "Garza's Happy Healthy Organic Greens and More LLC"
  type: "LLC"
  jurisdiction: "Texas"
  
filing:
  date: "December 2, 2022"
  state_file_number: "804827477"
  document_number: "1202609460002"
  status: "Active"
  
tax:
  ein: "92-1288715"
  irs_notice: "CP 575 G"
  
addresses:
  principal: "440 Louisiana St Ste 900, Houston, TX 77002"
  registered_agent: "1060 Clarence Dr Suite 250, Frisco, TX 75033"
  
preparer: "Tamara Schoonmaker"
industry: "Agriculture, microgreens"
```

---

## 2. Founder Identification

```yaml
founder:
  full_name: "Domenic Gabriel Garza"
  role: "Sole Organizer, Managing Member, Core Architect"
  
academic:
  orcid: "0000-0005-2996-3526"
  orcid_url: "https://orcid.org/0000-0005-2996-3526"
  
education:
  current:
    institution: "Southern New Hampshire University"
    program: "BS Computer Science + Cybersecurity (Dual Major)"
    concentration: "Software Engineering"
    student_id: "3413281"
    gpa: "3.732"
    progress: "45/120 credits (38%)"
    status: "Active"
  previous:
    institution: "San Jacinto College"
    email: "garza.d678936@stu.sanjac.edu"
    status: "Verify with 281-998-6137"
    
affiliations:
  - name: "UIDP.org"
    type: "Community Partner"
    description: "University-Industry Demonstration Partnership"
```

---

## 3. Smart Contract & Blockchain Identity

### 3.1 — Smart Contracts

```yaml
contracts:
  primary:
    name: "StrategickhaosUIDP.sol"
    type: "UIDP-based governance and NFT licensing"
    source: "https://github.com/Strategickhaos/DAO_Compliance/blob/main/contracts/StrategickhaosUIDP.sol"
    deployed_address: "TBD (pending deployment)"
    
notarization:
  ipfs_announcement: "https://github.com/Strategickhaos/DAO_Compliance/blob/main/docs/contracts/uidp/STRATEGICKHAOS_UIDP_IPFS_ANNOUNCEMENT.txt"
  nft_license_hash: "https://github.com/Strategickhaos/DAO_Compliance/blob/main/docs/contracts/uidp/hashes/UIDP_NFT_LICENSES.md.sha256"
```

### 3.2 — Wyoming Utility Token (Pending Verification)

```yaml
token:
  statute_references:
    - "W.S. §34-29-106 (Digital Asset Exemption)"
    - "W.S. §17-4-206 (Utility Token)"
  filing_status: "Notice of Intent filed"
  verification: "Contact Wyoming SOS at 307-777-7370"
```

---

## 4. Platform Identities

### 4.1 — Developer Platforms

```yaml
github:
  enterprise_org: "Strategickhaos Swarm Intelligence"
  personal_handles:
    - "Strategickhaos"
    - "Me10101-01"
  github_app: "StrategickhaosControlAI"
  repositories:
    compliance: "https://github.com/Strategickhaos/DAO_Compliance"
    uplink: "https://github.com/Me10101-01/Node137_Uplink_Receipt"

azure_devops:
  organization: "at-strategickhaos"
  url: "https://dev.azure.com/at-strategickhaos"
  token_expires: "2025-12-29"
  access: "Full (Codespace CLI)"

security:
  bugcrowd: "https://bugcrowd.com/h/Strategickhaos"
  ngrok:
    license_type: "Personal"
    invoice: "UTNCEV-00003"
```

### 4.2 — AI Platforms

```yaml
claude:
  accounts:
    - type: "SNHU .edu"
      workspaces:
        - "domenic.garza@snhu.edu's Organization"
        - "Legends Of Minds OS"
    - type: "Personal"
      workspaces:
        - "Strategickhaos"

openai:
  plan: "Pro"
  custom_assistants:
    - "Baby"
    - "Legion Node Advisor"

grok:
  status: "Active"
```

---

## 5. Infrastructure Identifiers

### 5.1 — Google Cloud Platform

```yaml
projects:
  - name: "Jarvis Swarm Personal"
    project_id: "jarvis-swarm-personal"
    project_number: "451173083E"
  - name: "My First Project"
    project_id: "central-achy-463919-r1"
    project_number: "331015150353"

clusters:
  - name: "jarvis-swarm-personal-001"
    region: "us-central1"
    mode: "Autopilot"
    endpoint: "34.89.88.27"
    role: "PRIMARY_SWARM"
    status: "Running"
  - name: "autopilot-cluster-1"
    region: "us-central1"
    mode: "Autopilot"
    endpoint: "35.192.28.199"
    role: "RED_TEAM"
    status: "Running"
```

### 5.2 — Domains

```yaml
domains:
  - domain: "strategickhaos.com"
    status: "Owned"
  - domain: "swarm.strategickhaos.com"
    status: "Pending DNS (requires A record → ingress LB)"
```

---

## 6. Cryptographic Identities

```yaml
gpg:
  key_server: "keys.openpgp.org"
  fingerprint_segments:
    - "CEB"
    - "E55"
    - "C8FA"
    - "7880"
    - "E19769"
    - "B0B"
    - "CB3464"
    - "7214"
    - "E15F9"
  full_fingerprint: "CEBE55C8FA7880E19769B0BCB34647214E15F9"

timestamping:
  method: "OpenTimestamps"
  blockchain: "Bitcoin"

content_addressing:
  method: "IPFS"
```

---

## 7. Legal & Governance Documents

### 7.1 — DAO Compliance Repository

```yaml
base_url: "https://github.com/Strategickhaos/DAO_Compliance"

documents:
  constitution: "/legal/constitution/Strategickhaos_DAO_Constitution.md"
  uidp_license: "/legal/uidp/UIDP_Terms_License.md"
  ein_registry: "/legal/ein/EIN_registry.txt"
  stripe_compliance: "/docs/contracts/uidp/compliance/stripe_checkout/"
  notarize_workflow: "/.github/workflows/notarize.yml"
```

### 7.2 — Node137 Uplink Repository

```yaml
base_url: "https://github.com/Me10101-01/Node137_Uplink_Receipt"

documents:
  trust_declaration: "/governance/TRUST_DECLARATION.md"
  non_aggression_clause: "/governance/NON_AGGRESSION_CLAUSE.md"
  public_identifiers: "/governance/public-identifier-registry.md"
  system_status: "/schemas/sovereign-empire-alert.json"
```

---

## 8. Verification Instructions

### For Humans

```bash
# Wyoming Secretary of State
# Visit: https://wyobiz.wyo.gov
# Search Entity ID: 2025-001708194 (DAO)
# Search Entity ID: 2025-001708312 (Nonprofit)

# ORCID Verification
# Visit: https://orcid.org/0000-0005-2996-3526

# GitHub Verification
# Visit: https://github.com/Strategickhaos
# Visit: https://github.com/Me10101-01
```

### For AI Auditors

```bash
# Clone and verify repository
git clone https://github.com/Me10101-01/Node137_Uplink_Receipt.git
cd Node137_Uplink_Receipt

# Verify GPG signatures
gpg --keyserver keys.openpgp.org --recv-keys CEBE55C8FA7880E19769B0BCB34647214E15F9
git log --show-signature

# Verify OpenTimestamps
ots verify governance/TRUST_DECLARATION.md.ots

# Verify file integrity
sha256sum governance/*.md
blake3 governance/*.md
```

### Emergency Contacts

```yaml
security: "security@strategickhaos.ai"
wyoming_sos: "307-777-7370"
texas_sos: "512-463-5555"
```

---

## Document Integrity

```
SHA256: [COMPUTED_ON_COMMIT]
BLAKE3: [COMPUTED_ON_COMMIT]
OTS:    [ANCHOR_ON_COMMIT]
```

**Last Verification:** December 3, 2025  
**Next Scheduled Audit:** January 3, 2026  

---

*Canonical public identity reference for Strategickhaos DAO LLC.*
