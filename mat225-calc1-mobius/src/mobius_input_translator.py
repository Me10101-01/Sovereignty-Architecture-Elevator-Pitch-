#!/usr/bin/env python3
"""
mobius_input_translator.py — text ↔ symbol mode converter
MAT-225 / SAGCO antibody layer for Mobius UX failures

Converts natural math notation → Mobius-safe text-mode strings.
Every conversion failure is an INV candidate.
"""

import re
import sys


TRANSLATION_TABLE = [
    # (pattern, replacement, antibody_id, description)
    # Bare fractions without parens — AB-PAREN-FRAC-001
    (r"(\w[\w\s\+\-\*]*)/(\w[\w\s\+\-\*]*)",
     r"(\1)/(\2)",
     "AB-PAREN-FRAC-001",
     "Wrap numerator/denominator in parens"),

    # |x| → abs(x) — AB-ABS-BARS-001
    (r"\|([^|]+)\|",
     r"abs(\1)",
     "AB-ABS-BARS-001",
     "Convert |expr| to abs(expr)"),

    # √x or sqrt without parens → sqrt(x) — AB-SQRT-SYMBOL-001
    (r"√\s*(\w+)",
     r"sqrt(\1)",
     "AB-SQRT-SYMBOL-001",
     "Convert √x to sqrt(x)"),

    # x² → x^2 — AB-SUPERSCRIPT-001
    (r"(\w)²", r"\1^2", "AB-SUPERSCRIPT-001", "Convert ² to ^2"),
    (r"(\w)³", r"\1^3", "AB-SUPERSCRIPT-001", "Convert ³ to ^3"),

    # Implicit multiplication: 2x → 2*x — AB-IMPLICIT-MUL-001
    (r"(\d)([a-zA-Z])", r"\1*\2", "AB-IMPLICIT-MUL-001", "Insert * for implicit multiplication"),
]


def text_to_mobius(expr: str, verbose: bool = False) -> tuple[str, list[str]]:
    """
    Convert a natural-notation math string to Mobius text-mode safe format.
    Returns (converted_string, list_of_antibodies_fired).
    """
    result = expr
    fired = []

    for pattern, replacement, ab_id, desc in TRANSLATION_TABLE:
        new_result = re.sub(pattern, replacement, result)
        if new_result != result:
            fired.append(f"[{ab_id}] {desc}: {result!r} → {new_result!r}")
            result = new_result

    return result, fired


def mobius_to_latex(expr: str) -> str:
    """Convert Mobius text-mode string to LaTeX for verification rendering."""
    s = expr
    # a/b → \frac{a}{b} (simplified)
    s = re.sub(r"\(([^)]+)\)/\(([^)]+)\)", r"\\frac{\1}{\2}", s)
    s = re.sub(r"sqrt\(([^)]+)\)", r"\\sqrt{\1}", s)
    s = re.sub(r"abs\(([^)]+)\)", r"\\left|\1\\right|", s)
    s = re.sub(r"\^(\w+)", r"^{\1}", s)
    s = re.sub(r"\*", r"\\cdot ", s)
    return s


SYMBOL_MODE_GUIDE = """
SYMBOL MODE NAVIGATION (6-line toolbar box)
───────────────────────────────────────────
  ENTER FRACTION : Click ÷ or fraction button → cursor lands in numerator
  EXIT NUMERATOR : Right-arrow key → moves to denominator
  EXIT FRACTION  : Right-arrow key again → exits fraction entirely
  ENTER EXPONENT : Click x^□ button → cursor lands in exponent
  EXIT EXPONENT  : Right-arrow key → exits exponent
  ENTER SQRT     : Click √□ button → cursor lands under radical
  EXIT SQRT      : Right-arrow key → exits radical
  ABS VALUE      : Click |□| button
  EXIT ABS       : Right-arrow key

TRAPS:
  - Typing sqrt in symbol mode → s·q·r·t as separate variables [AB-SQRT-SYMBOL-001]
  - Getting stuck in denominator → must right-arrow out, NOT click outside
  - Sigma button toggles text↔symbol — use Preview to verify rendering

SOVEREIGN RULE: Always answer in TEXT MODE for graded submissions.
Use symbol mode ONLY to verify visual rendering of complex expressions.
"""


def print_guide() -> None:
    print(SYMBOL_MODE_GUIDE)


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "guide":
        print_guide()

    elif args[0] == "translate" and len(args) >= 2:
        expr = " ".join(args[1:])
        converted, fired = text_to_mobius(expr, verbose=True)
        print(f"\n  INPUT    : {expr}")
        print(f"  OUTPUT   : {converted}")
        print(f"  LATEX    : {mobius_to_latex(converted)}")
        if fired:
            print(f"\n  ANTIBODIES FIRED:")
            for f in fired:
                print(f"    {f}")
        else:
            print(f"\n  No antibodies fired — input already Mobius-safe.")

    elif args[0] == "latex" and len(args) >= 2:
        expr = " ".join(args[1:])
        print(mobius_to_latex(expr))

    else:
        print("""
mobius_input_translator.py — text ↔ symbol mode converter

USAGE:
  python mobius_input_translator.py guide
    Print symbol mode navigation guide

  python mobius_input_translator.py translate "expr"
    Convert natural notation to Mobius text-mode safe format

  python mobius_input_translator.py latex "expr"
    Convert Mobius text-mode string to LaTeX

EXAMPLES:
  python mobius_input_translator.py translate "5x+1/y-2"
  python mobius_input_translator.py translate "|x+1|"
  python mobius_input_translator.py translate "√x"
        """)
