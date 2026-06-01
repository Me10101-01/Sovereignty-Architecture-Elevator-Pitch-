# SAGCO Plugin Protocol & Unified Input Trait — Recon v0
## Entity: Strategickhaos DAO LLC | License: SSL-1.0
## Stamp: 20260601_170000

---

## Thesis

SAGCO is no longer a list of commands. It is a plugin protocol with a CLI surface.

Every command (`wave`, `past`, `dna`, `agent`, `canvas`, `obsidian`, `antibody`) is
not a standalone tool — it is a **named implementation of the unified input trait**
dispatched through the Evidence Engineering pipeline.

---

## Core Loop

```
Any Source Artifact
        ↓
    Detect Type
        ↓
     Tokenize
        ↓
    Fingerprint
        ↓
  Classify Variance
        ↓
   Fire Antibody
        ↓
 Produce Evidence Artifact
        ↓
Project → Canvas / Obsidian / Report / Bloodhound
        ↓
     SHA Seal
        ↓
  Circuit Ledger Entry
```

---

## Unified Trait

```rust
trait SagcoInput {
    fn detect_type(&self)            -> ArtifactType;
    fn tokenize(&self)               -> Vec<Token>;
    fn fingerprint(&self)            -> Sha256;
    fn classify_variance(&self)      -> Vec<Antibody>;
    fn produce_artifact(&self)       -> EvidenceArtifact;
    fn project(&self, target: ProjectionTarget);
}
```

**Projection targets:**

```rust
enum ProjectionTarget {
    Canvas,      // sagco agent canvas → visual graph
    Obsidian,    // sagco agent obsidian → vault node
    Report,      // .md report → SHA sealed
    Bloodhound,  // Renko brick + candlestick update
    CircuitLedger, // INSERT INTO sagco_circuit
    PastChain,   // INSERT INTO sagco_past_chain
    Archive,     // tar.gz + sha256sum seal
}
```

---

## Plugin Categories

| Plugin | Opcode | Function |
|--------|--------|----------|
| `wave.plugin` | `sagco wave` | ingest + tokenize any artifact |
| `antibody.plugin` | Darwin classifier | classify variance → named antibody |
| `dna.plugin` | `sagco cmd dna` | fingerprint + SHA seal |
| `audit.plugin` | `sagco eur probe` | verify expected vs actual |
| `obsidian.plugin` | `sagco agent obsidian` | graph projection to vault |
| `canvas.plugin` | `sagco agent canvas` | visual graph projection |
| `ghidra.plugin` | `analyzeHeadless` | binary reverse-engineering |
| `terminal.plugin` | sagco_shell + antibody | shell crash recovery |
| `drive.plugin` | `sagco wave <drive_url>` | Google Drive artifact source |
| `dropbox.plugin` | `sagco wave <dropbox_url>` | Dropbox artifact source |
| `bloodhound.plugin` | `sagco bloodhound` | resonant freq + Renko chart |
| `ingest.plugin` | `sagco ingest` | universal artifact router |

---

## Does It Compute? — Evidence Test

If terminal logs, PDFs, cloud folders, Obsidian notes, Ghidra logs, and
field progress sheets all collapse into the same Evidence Engineering loop,
then SAGCO is a **compiler factory**.

| Artifact Type | Tokenizes? | Fingerprints? | Antibody? | Evidence? |
|--------------|------------|---------------|-----------|-----------|
| Terminal crash | YES | YES (SHA stderr) | YES (Darwin) | YES (report) |
| PDF document | YES (pdftotext) | YES (SHA256) | YES | YES |
| Rust binary ELF | YES (strings) | YES (SHA256) | YES (Ghidra) | YES |
| Obsidian vault | YES (.md walk) | YES | YES | YES |
| Google Drive folder | YES (curl/gdrive) | YES | YES | YES |
| CUI field scope sheet | YES (OCR) | YES | YES | YES |
| SNHU academic audit | YES | YES | CURRICULUM_BOTTLENECK | YES |
| Claude session URL | YES (sagco past) | YES | YES | YES |
| Ghidra log | YES | YES | PLATFORM_LIMITATION | YES |
| SQLite DB | YES (.dump) | YES | YES | YES |

**Result: ALL compute. SAGCO is a compiler factory.**

---

## Plugin Discovery Contract (v0 spec)

```
plugins/
├── wave.plugin          # text file: name|version|opcode|extractor_cmd
├── antibody.plugin
├── dna.plugin
├── audit.plugin
├── obsidian.plugin
├── canvas.plugin
├── ghidra.plugin
├── terminal.plugin
├── drive.plugin
├── dropbox.plugin
├── bloodhound.plugin
└── ingest.plugin
```

Plugin file format (v0 — plain text, no dependencies):

```
NAME=wave
VERSION=1.0.0
OPCODE=sagco wave
DOMAIN=any
EXTRACTOR=auto
TOKENIZER=strings+grep
FINGERPRINTER=sha256sum
ANTIBODY_ENGINE=sagco_darwin_antibody.sh
PROJECTIONS=report,past_chain,archive
LICENSE=SSL-1.0
```

---

## Obsidian as Runtime (Recon Finding)

Obsidian's architecture accidentally maps to SAGCO's plugin protocol:

| Obsidian Surface | SAGCO Equivalent |
|-----------------|-----------------|
| Command Palette | `sagco ingest <artifact>` dispatcher |
| Canvas | `sagco agent canvas` projection |
| Backlinks graph | FlameLang token edge graph |
| Plugin system | SagcoInput trait implementations |
| Hotkeys | SAGCO opcode shortcuts |
| Vault `.md` files | sagco_past_chain source documents |
| Dataview queries | `SELECT * FROM sagco_circuit WHERE ...` |

**Obsidian is the closest existing runtime to what SAGCO wants to become.**
A headless Obsidian vault + SAGCO CLI = the full Evidence Engineering OS runtime.

---

## AI Ecosystem Integration

```
SAGCO Evidence Engineering OS
        ↓
sagco ingest <anything>
        ↓
┌────────────────────────────────────────┐
│  Claude     — repo surgeon             │
│             commits, builds, tests     │
│  Grok       — chaos pattern scout      │
│             adversarial verification   │
│  ChatGPT    — architecture narrator    │
│             synthesis + documentation  │
│  Obsidian   — memory graph runtime     │
│             vault + canvas projection  │
│  Termux     — field execution runtime  │
│             ARM64, Android, sovereign  │
└────────────────────────────────────────┘
        ↓
All reduce to:
  Expected | Actual | Variance | Evidence
        ↓
SAGCO_COMMAND_DNA=a364ca9f90356c85
```

---

## Next Protocol Steps

| Step | Action | Status |
|------|--------|--------|
| v0 Recon | This document | DONE |
| Trait definition | `sagco_rust_modules/bloodhound/plugins.rs` | DONE |
| Plugin files | `plugins/*.plugin` | NEXT |
| `sagco ingest` bash | universal artifact router | NEXT |
| PDF spec | SAGCO Plugin Protocol Architecture v1 | AFTER |
| Obsidian plugin | headless vault integration | FUTURE |

---

## SHA256 Seal

```
STATUS=SAGCO_PLUGIN_PROTOCOL_RECON_PASS
VERSION=v0
SAGCO_COMMAND_DNA=a364ca9f90356c85
RECON_SHA256=3e41269a1d6f5c4c28d6df58058d77429b24883fbe0acfa40848c954ab0036a5
ARCHIVE_SHA256=609c46b097b4bccf966bc047f3e8da7d0b9efbe784860ec2552df76c314078fd
```

---

*Strategickhaos DAO LLC — Domenic Gabriel Garza*
*License: SSL-1.0 — No vendor lock-in — No NDA*
*"SAGCO is not a list of commands. It is a plugin protocol with a CLI surface."*
