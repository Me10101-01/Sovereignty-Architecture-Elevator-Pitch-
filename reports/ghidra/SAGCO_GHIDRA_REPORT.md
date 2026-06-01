# SAGCO Ghidra Headless Analysis Report
## Target: `target/release/sagco_rust_command_compiler`
## Session: sagco-rust-compiler-archive — 2026-06-01, Corpus Christi TX

---

## Status

```
STATUS: JDK21_PASS — BINARY_RESTORE_REQUIRED — GHIDRA_READY
```

| Stage | Tool | Result | Notes |
|-------|------|--------|-------|
| Archive seal | `sha256sum` | PASS | `6b1924a45f5c68cb2b5a6a5e3cfc83bc2413521cee69817e8267ea59095491dc` |
| JDK 21 install | `pkg install openjdk-21` | **PASS** | 21.0.10 aarch64 installed |
| binutils install | `pkg install binutils` | **PASS** | 2.46.0-3 — `strings`/`readelf`/`nm` live |
| tesseract install | `pkg install tesseract` | **PASS** | 5.5.2 — OCR pipeline live |
| Ghidra download | `wget ghidra_12.1_PUBLIC` | **PASS** | 541.52MB at 30MB/s |
| Binary name | `sagco_rust_command_compiler` | CORRECTED | NOT `sagco` — Cargo package name |
| `src/main.rs` | stub overwrite | **CRITICAL** | Restore from `src/main.rs.backup` immediately |
| ELF headers | `readelf -h` | READY | binutils installed, binary needs restore |
| Symbol table | `nm -D` | READY | binutils installed |
| String extraction | `strings` | READY | binutils installed |
| Ghidra headless | `analyzeHeadless` | READY | JDK 21 satisfied |

---

## CRITICAL: Restore main.rs Before Running

The session accidentally overwrote `src/main.rs` with a 3-line stub.
The real source is in `src/main.rs.backup`. **Run this first:**

```sh
cd ~/downloads/sagco_rust_command_compiler
cp src/main.rs.backup src/main.rs
cargo build --release
# confirm real binary: ./target/release/sagco_rust_command_compiler past
```

---

## Binary Name Correction

The Cargo package name is `sagco_rust_command_compiler`. The binary at:

```
target/release/sagco_rust_command_compiler   ← CORRECT
target/release/sagco                          ← DOES NOT EXIST
```

The `sagco` command in PATH is a **separate installed binary** (at `~/sagco/` or `~/bin/`).
The Rust compiler project builds to `sagco_rust_command_compiler`.

---

## Run the Full Pipeline

After restoring main.rs:

```sh
cd ~/downloads/sagco_rust_command_compiler

# Set JDK (Termux $PREFIX path — NOT /usr/lib)
export JAVA_HOME="$PREFIX/lib/jvm/java-21-openjdk"
export GHIDRA_HOME="$HOME/downloads/ghidra_12.1_PUBLIC"
export PATH="$JAVA_HOME/bin:$PATH"

# Verify JDK 21 is active
java -version    # must show 21.0.10

# Run full pipeline (auto-restores main.rs if stub detected)
bash ~/sagco_pr_lab/repo/sagco_ghidra_flametoken.sh
```

Or step by step:

```sh
BINARY="target/release/sagco_rust_command_compiler"

# ELF
readelf -h "$BINARY"

# Symbols
nm -D "$BINARY" 2>/dev/null | head -40

# FlameTokens
strings "$BINARY" \
  | grep -iE "sagco|past|wave|weather|agent|flame|treasure|cmd|dna|evolution" \
  | sort -u | tee reports/ghidra/flametokens.txt
echo "TOKENS: $(wc -l < reports/ghidra/flametokens.txt)"
sha256sum reports/ghidra/flametokens.txt

# Ghidra
mkdir -p ~/ghidra_projects
$GHIDRA_HOME/support/analyzeHeadless \
  ~/ghidra_projects SAGCO_FLAMETOKEN \
  -import "$BINARY" \
  -overwrite \
  2>&1 | tee reports/ghidra/ghidra_sagco.log
```

---

## Case Study Portfolio Seal

```
SAGCO_HEADLESS_VM_FUZZ_CASE_STUDY.tar.gz
SHA256: 9d95f793179bd6d8b80bb2e035aa00ca46fccd58696855d52d0ef1476926206f
Size: 15M
Sealed: 2026-06-01 06:26 CDT
```

**Contains:**
- `portfolio_case_study/reports/` — all SAGCO PAST memory reports, ghidra reports
- `portfolio_case_study/proofs/` — Cargo.toml, Cargo.lock
- `portfolio_case_study/sandbox/sagco` — binary copy
- `portfolio_case_study/commands/` — sagco_status_archeologist.sh
- `portfolio_case_study/README.md` — pipeline description

---

## Environmental Record

| Field | Value |
|-------|-------|
| JDK | `openjdk-21 21.0.10 aarch64` — INSTALLED |
| binutils | `2.46.0-3` — INSTALLED |
| tesseract | `5.5.2` — INSTALLED |
| poppler | `26.02.0` — INSTALLED |
| Ghidra | `12.1 PUBLIC` — DOWNLOADED @ `~/downloads/ghidra_12.1_PUBLIC` |
| JAVA_HOME | `$PREFIX/lib/jvm/java-21-openjdk` (Termux path) |
| GPS | 27°50'48"N, 97°33'58"W — Corpus Christi TX |
| Weather SHA | `101fb3bd0c10dc6f` |
| Session seal | `2026-06-01` |

---

## Reverse Engineering Pipeline

```
src/main.rs.backup (RESTORE FIRST)
        │
        └── cargo build --release
                │
                └── target/release/sagco_rust_command_compiler (ARM64 ELF64 Rust)
                        │
                        ├── readelf -h ────────────► elf_headers.txt
                        ├── nm -D ─────────────────► elf_symbols.txt
                        ├── strings ───────────────► flametokens.txt
                        │       └── grep filter ──► 23-command DNA check
                        └── Ghidra 12.1 headless ─► ghidra_sagco.log
                                (JDK 21 ✓ READY)
```

---

*SAGCO-OS — Sovereign Autonomous General Compute OS*
*Strategickhaos DAO LLC — Domenic Gabriel Garza*
*Archive branch: claude/sagco-rust-compiler-archive-ZQXKs*
*Generated: 2026-06-01 — Corpus Christi, TX (27°50'48"N 97°33'58"W)*
