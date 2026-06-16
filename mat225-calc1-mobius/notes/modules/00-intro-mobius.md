# Module 00 — Introduction to Mobius
# Status: IN PROGRESS | Grade: 6.0/20.0 → target 20/20

## What This Module Is
Mobius interface familiarization. NOT calc content.
Points come from completing every practice activity section.

## Grade Recovery Plan
| Section | Status | Points |
|---------|--------|--------|
| Fractions in Symbol Mode (pt 1) | done | ? |
| Fractions in Symbol Mode (pt 2) | NEXT | ? |
| Entering Exponents | TODO | ? |
| Entering Absolute Values | TODO | ? |
| Entering Square Roots | TODO | ? |

Hit "How Did I Do?" on every ungraded practice — no penalty, fingerprints input syntax for graded ones.

## Answer Patterns Confirmed

### Complex Fraction: (x+7/15)/19 + 9
```
Text mode: (x+7/15)/19+9
Right-arrow exits denominator after 15
```

### Simple Fraction: (5x+1)/(y-2)
```
Text mode: (5*x+1)/(y-2)
Parens required around both numerator and denominator
```

### Fraction with multiple terms: (x+5)/(y+9z-11)
```
Text mode: (x+5)/(y+9*z-11)
Explicit * required between coefficient and variable
```

### Reciprocal: 1/(x+1)
```
Text mode: 1/(x+1)
Without parens → Mobius reads as 1/x + 1 (wrong!)
```

## Antibodies Fired This Module
- AB-PAREN-FRAC-001: every complex fraction problem
- AB-SQRT-SYMBOL-001: documented, not yet triggered (avoid symbol mode sqrt)

## Symbol Mode Navigation (decoded)
See `docs/mobius_syntax_reference.md` for full table.

Key survival moves:
- RIGHT ARROW = exit denominator (memorize this)
- PREVIEW button = verify rendering before submit
- SIGMA button = toggle text/symbol

## Cross-Domain Hooks
- Fraction entry rules → FlameLang M2 tokenizer: `(a+b)/c` vs `a+b/c` = same type disambiguation problem as variable vs function
- Mobius UX failures → INV candidates for mobius_input_translator
