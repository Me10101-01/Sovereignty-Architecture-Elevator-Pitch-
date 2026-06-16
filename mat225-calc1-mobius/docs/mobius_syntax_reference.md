# Mobius Syntax Reference — MAT-225
# Every input pattern decoded and antibody-tagged.

## Text Mode (1-line answer box)

| Want | Type | Trap | Antibody |
|------|------|------|----------|
| `(5x+1)/(y-2)` | `(5*x+1)/(y-2)` | Without parens → wrong order of ops | AB-PAREN-FRAC-001 |
| `(x+5)/(y+9z-11)` | `(x+5)/(y+9*z-11)` | Same trap, more variables | AB-PAREN-FRAC-001 |
| `1/(x+1)` | `1/(x+1)` | Without parens → `1/x + 1` | AB-PAREN-FRAC-001 |
| `x^n` | `x^n` | Standard caret | — |
| `\|x\|` | `abs(x)` | `abs()` function | AB-ABS-BARS-001 |
| `√x` | `sqrt(x)` | `sqrt()` function | AB-SQRT-SYMBOL-001 |
| `2x` | `2*x` | Implicit multiplication | AB-IMPLICIT-MUL-001 |
| `(x+7/15)/19 + 9` | `(x+7/15)/19+9` | Right-arrow exits | — |

## Symbol Mode (6-line box with toolbar)

| Action | How |
|--------|-----|
| Enter fraction | Click ÷ button → cursor in numerator |
| Exit numerator | Right-arrow key |
| Exit fraction | Right-arrow key again |
| Enter exponent | Click x^□ button |
| Exit exponent | Right-arrow key |
| Enter sqrt | Click √□ button |
| Type `sqrt` as text | **DO NOT** — fires AB-SQRT-SYMBOL-001 |
| Absolute value | Click \|□\| button |
| Toggle modes | Sigma button |
| Verify rendering | Preview button |

## Critical Antibodies

### AB-SQRT-SYMBOL-001 — The Sqrt Symbol Trap
**Trigger**: Typing `sqrt` in symbol mode
**Effect**: `sqrt` parsed as 4 separate variables `s·q·r·t`
**Kill**: Use `((n)/(d))^(1/2)±c` in symbol mode or `sqrt(x)` in text mode

### AB-PAREN-FRAC-001 — Missing Fraction Parens
**Trigger**: `a+b/c` without parens
**Effect**: Order of operations reads as `a + (b/c)` not `(a+b)/c`
**Kill**: Always `(numerator)/(denominator)`

### AB-ABS-BARS-001 — Absolute Value Bars
**Trigger**: `|x|` in text mode
**Effect**: Mobius may not parse bars as abs
**Kill**: Use `abs(x)` in text mode

### AB-IMPLICIT-MUL-001 — Missing Multiplication Sign
**Trigger**: `2x`, `3y`, `nx`
**Effect**: Mobius may read as variable name `2x` not `2*x`
**Kill**: Always use explicit `*` in text mode when submitting

## Sovereign Rule
Always type in **text mode** for graded answers.
Use symbol mode only for visual verification of complex expressions.
Text mode = auditable, copy-pasteable, version-controllable, SHA-256-hashable.

## Verification Protocol
1. Solve by hand in `notes/modules/##-*.md` (kinesthetic)
2. Validate with sympy: `python src/flamec_calc_validator.py check "expected" "actual"`
3. Sketch graph (spatial)
4. Write the why in plain English (narrative)
5. Submit to Mobius only after all 4 channels agree
6. Hash answer: `python src/flamec_calc_validator.py hash "answer"`
