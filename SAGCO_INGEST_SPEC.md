# SAGCO `ingest` — Artifact Router + Variance Engine v1
## SAGCO Evidence Engineering OS — Command Specification
## Entity: Strategickhaos DAO LLC | License: SSL-1.0
## Stamp: 20260601_164000

---

## The Command

```
sagco ingest <artifact>
```

`<artifact>` is ONE universal object. Type doesn't matter.
The router detects it and dispatches through the Evidence Engineering Loop.

---

## Auto-Route Table

| Input Type | Detection | Route |
|-----------|-----------|-------|
| `.pdf` | file extension | `wave` → pdftotext → FlameTokens |
| `.md` `.txt` `.rs` `.yaml` | text file | `past` → tokenize → fingerprint |
| `http://` `https://` | URL prefix | `wave` → curl -L → extract |
| `drive.google.com` | URL pattern | `wave` → gdrive → extract |
| `dropbox.com` | URL pattern | `wave` → curl -L → extract |
| `*.db` `*.sqlite` | file extension | `audit` → sqlite3 dump → circuit |
| `image.*` `.png` `.jpg` | file extension | `wave` → tesseract OCR → tokens |
| `terminal:<cmd>` | prefix | run cmd → capture stderr → antibody |
| `obsidian:<vault>` | prefix | `obsidian` → graph all .md → PAST chain |
| `claude:<session>` | prefix | `past` → session log → chain |
| ELF binary | file magic `\x7fELF` | `wave` → strings + Ghidra → FlameTokens |
| directory | is_dir | walk all files → batch ingest |

---

## Pipeline (same for every input)

```
sagco ingest <artifact>
    │
    ▼
DETECT type (PluginKind::from_path)
    │
    ▼
EXTRACT raw signals
  PDF    → pdftotext | strings
  URL    → curl -L | strings
  Image  → tesseract | strings
  Binary → strings | readelf | nm
  Text   → cat | strings
  SQL    → sqlite3 .dump
    │
    ▼
TOKENIZE → FlameTokens (FL_xx_xx vocabulary)
    │
    ▼
FINGERPRINT → 64-bit FNV hash (content-addressable)
    │
    ▼
VERIFY  → Did extraction succeed? (exit code gate)
VALIDATE → Did tokens match expected domain vocabulary?
VARIANCE → delta = |expected_tokens - actual_tokens|
    │
    ▼
ANTIBODY → classify_polyglot(stderr, exit_code, domain)
TRAJECTORY → stabilized | adaptation | evolution | mutation
    │
    ▼
EVIDENCE → SHA256 seal
         → INSERT INTO sagco_circuit
         → INSERT INTO sagco_past_chain (if text)
         → INSERT INTO sagco_archive (if sealed)
    │
    ▼
BLOODHOUND → resonant frequency update
           → Renko brick drawn (if maturity changes)
           → WHEN gates re-evaluated
    │
    ▼
OUTPUT → sagco_ingest_<stamp>.md report
       → DNA seal: SAGCO_COMMAND_DNA=a364ca9f90356c85
```

---

## WHEN Logic (auto-triggered after ingest)

```
WHEN extraction_exit = 0 AND tokens > 0
  → PASS_IMMUNITY | stabilized
  → Renko UP brick if maturity improves

WHEN extraction_exit = 0 AND tokens = 0
  → EMPTY_RESPONSE_ANTIBODY | adaptation
  → no brick drawn; HOLD signal

WHEN curl returns "Host not in allowlist"
  → NETWORK_POLICY_ANTIBODY | evolution
  → recovery: run on Termux

WHEN file is PDF AND pdftotext missing
  → DEPENDENCY_ANTIBODY | adaptation
  → recovery: pkg install poppler

WHEN file is ELF AND Ghidra missing
  → PLATFORM_LIMITATION_ANTIBODY | evolution
  → recovery: already installed in $GHIDRA_HOME

WHEN tokens > 100
  → update sagco_past_chain
  → recalculate maturity dashboard
  → redraw Bloodhound Renko chart

WHEN maturity crosses 10% threshold
  → Renko brick drawn
  → candlestick OHLC updated
  → SIGNAL: BUY_EVOLUTION or HOLD_ADAPTATION
```

---

## Plugin Protocol (Rust trait)

```rust
pub trait SagcoInput {
    fn source_id(&self)  -> &str;
    fn tokenize(&self)   -> Vec<String>;
    fn fingerprint(&self) -> String;
    fn classify(&self)    -> (Antibody, Trajectory);
    fn artifact(&self)    -> SagcoArtifact;
}
```

Every input type implements this single trait.
The plugin registry dispatches to the right implementation at runtime.

Implemented plugins:
- `PdfPlugin`         → pdftotext extractor
- `UrlPlugin`         → curl -L extractor
- `TerminalPlugin`    → bash -c + stderr classifier
- `ImagePlugin`       → tesseract OCR
- `SqlPlugin`         → sqlite3 dump
- `ObsidianPlugin`    → vault .md walker
- `GoogleDrivePlugin` → gdrive download
- `DropboxPlugin`     → curl -L with token
- `ClaudePlugin`      → session log parser
- `BinaryPlugin`      → strings + readelf + Ghidra
- `MarkdownPlugin`    → direct text tokenizer
- `YamlPlugin`        → YAML key-value extractor

---

## Usage Examples

```bash
# PDF
sagco ingest "SAGCO Computable Reality Engineering Blueprint- v1.pdf"

# URL
sagco ingest "https://book-of-the-dead.fitzmuseum.cam.ac.uk/explore/the-book-of-the-dead/spell-77"

# Binary
sagco ingest target/release/sagco_rust_command_compiler

# Terminal command
sagco ingest "terminal:sagco past"

# Obsidian vault
sagco ingest "obsidian:~/documents/sagco-os-vault"

# SQL database
sagco ingest data_engineering/sagco_circuit.db

# Directory (batch)
sagco ingest reports/

# Google Drive (with share URL)
sagco ingest "https://drive.google.com/file/d/<id>/view"
```

---

## Output

```
SAGCO INGEST REPORT — stamp
────────────────────────────
Source:      SAGCO_Blueprint_v1.pdf
Type:        PDF
Tokens:      138
Fingerprint: cr_blueprint_v1_a7f2d39e
SHA256:      9ce65bd0...
Antibody:    PASS_IMMUNITY
Trajectory:  stabilized
Score:       PASS

BLOODHOUND UPDATE:
  Maturity: 84% → 84% (no brick)
  Signal:   BUY_EVOLUTION (69% PASS_IMMUNITY resonance)
  WHEN GATE 3: Golden Hawk delta = +11%

STATUS=SAGCO_INGEST_PASS
DNA=a364ca9f90356c85
```

---

## Implementation Status

| Component | Status |
|-----------|--------|
| `SagcoInput` trait | DONE — `sagco_rust_modules/bloodhound/plugins.rs` |
| `PluginRegistry` | DONE — auto-routes by kind |
| `PluginKind::from_path()` | DONE — detects all types |
| `sagco_bloodhound.sh` | DONE — live Renko + candlestick |
| `sagco ingest` bash wrapper | NEXT → `sagco_ingest.sh` |
| Rust binary integration | NEXT → `sagco ingest` subcommand in `src/spl/` |

---

## Relation to AI Ecosystem

```
SAGCO-OS Evidence Engineering OS
       ↓
sagco ingest <anything>
       ↓
┌──────────────────────────────────┐
│  Claude  — repo surgeon          │
│  Grok    — chaos pattern scout   │
│  ChatGPT — architecture narrator │
│  Obsidian — memory graph         │
│  Termux  — field runtime         │
└──────────────────────────────────┘
       ↓
All reduce to:
  Expected | Actual | Variance | Evidence
```

SAGCO is the machine that makes the chaos computable.
Every AI, every tool, every field report is just another `<artifact>`.

---

```
STATUS=SAGCO_INGEST_SPEC_PASS
VERSION=v1.0
NEXT_COMMAND=sagco_ingest.sh
SAGCO_COMMAND_DNA=a364ca9f90356c85
```

*Strategickhaos DAO LLC — Domenic Gabriel Garza*
*License: SSL-1.0 — Sovereign by Design*
