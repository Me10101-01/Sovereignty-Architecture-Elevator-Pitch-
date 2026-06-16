#!/usr/bin/env python3
"""
flamec_calc_validator.py — Sympy + FlameLang M2 bridge
MAT-225 MAT-225 Calc I / SAGCO ERU verification layer

ERU loop:
  Expected  = what the answer should be (symbolic)
  Actual    = what was typed into Mobius (text-mode string)
  Variance  = delta between sympy-simplified forms
  Verdict   = PROVEN | PROMISING | UNPROVEN | INFLATED

FlameLang M2 hook:
  Every Mobius answer string IS a type-check problem.
  x + 1/2 vs (x+1)/2 is the same as a variable-vs-function disambiguation.
"""

import sympy
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)
import hashlib
import datetime
import json
import sys
import os

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

VERDICTS = {
    "PROVEN":    "≥100% — exact symbolic match",
    "PROMISING": "structurally equivalent with simplification",
    "UNPROVEN":  "partial credit — different form, same domain",
    "INFLATED":  "wrong — sympy reports mismatch",
}


def mobius_parse(expr_str: str) -> sympy.Expr:
    """Parse a Mobius text-mode answer string into a sympy expression."""
    return parse_expr(expr_str, transformations=TRANSFORMATIONS)


def eru_verdict(expected_str: str, actual_str: str) -> dict:
    """
    Run the ERU loop on a single Mobius answer.
    Returns a verdict dict compatible with sagco-missing-links/registry format.
    """
    result = {
        "expected": expected_str,
        "actual":   actual_str,
        "verdict":  "INFLATED",
        "coverage": 0.0,
        "notes":    "",
        "simplified_expected": "",
        "simplified_actual":   "",
        "flamelang_type_note": "",
    }

    try:
        e_expr = mobius_parse(expected_str)
        a_expr = mobius_parse(actual_str)

        result["simplified_expected"] = str(sympy.simplify(e_expr))
        result["simplified_actual"]   = str(sympy.simplify(a_expr))

        diff = sympy.simplify(e_expr - a_expr)

        if diff == 0:
            result["verdict"]  = "PROVEN"
            result["coverage"] = 100.0
            result["notes"]    = "Exact match after simplification."
        elif sympy.simplify(sympy.expand(diff)) == 0:
            result["verdict"]  = "PROVEN"
            result["coverage"] = 100.0
            result["notes"]    = "Expand-equivalent match."
        else:
            # Check structural similarity via ratio
            try:
                ratio = sympy.simplify(e_expr / a_expr)
                if ratio.is_number and abs(float(ratio) - 1.0) < 1e-9:
                    result["verdict"]  = "PROVEN"
                    result["coverage"] = 100.0
                    result["notes"]    = "Ratio = 1 after simplification."
                else:
                    # Partial — same variables, different form
                    e_vars = e_expr.free_symbols
                    a_vars = a_expr.free_symbols
                    if e_vars == a_vars and len(e_vars) > 0:
                        result["verdict"]  = "PROMISING"
                        result["coverage"] = 50.0
                        result["notes"]    = f"Same variable set {e_vars} but forms differ. diff={diff}"
                    elif e_vars & a_vars:
                        result["verdict"]  = "UNPROVEN"
                        result["coverage"] = 25.0
                        result["notes"]    = f"Partial variable overlap. diff={diff}"
                    else:
                        result["verdict"]  = "INFLATED"
                        result["coverage"] = 0.0
                        result["notes"]    = f"No symbolic overlap. diff={diff}"
            except Exception as ratio_err:
                result["notes"] = f"Ratio check failed: {ratio_err}. diff={diff}"

        # FlameLang M2 type note — does the parse produce the same AST structure?
        if e_expr.func == a_expr.func:
            result["flamelang_type_note"] = f"Top-level type MATCH: {e_expr.func.__name__}"
        else:
            result["flamelang_type_note"] = (
                f"Top-level type MISMATCH: expected={e_expr.func.__name__} "
                f"actual={a_expr.func.__name__} — FlameLang M2 type error"
            )

    except Exception as parse_err:
        result["verdict"]  = "INFLATED"
        result["coverage"] = 0.0
        result["notes"]    = f"Parse error: {parse_err}"
        result["flamelang_type_note"] = "PARSE_FAIL — FlameLang M2 would reject at token level"

    return result


def sha256_log(answer_str: str, log_path: str = None) -> str:
    """Hash an answer string and append to evidence/submissions.log."""
    h = hashlib.sha256(answer_str.encode()).hexdigest()
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    entry = f"{ts}  SHA256={h}  answer={answer_str!r}\n"
    if log_path:
        with open(log_path, "a") as f:
            f.write(entry)
    return h


def validate(expected: str, actual: str, log: bool = True) -> None:
    """CLI-friendly validator. Prints ERU result and optionally logs."""
    result = eru_verdict(expected, actual)

    log_path = os.path.join(os.path.dirname(__file__), "../evidence/submissions.log")

    print(f"\n{'='*60}")
    print(f"  EXPECTED : {expected}")
    print(f"  ACTUAL   : {actual}")
    print(f"  VERDICT  : {result['verdict']} ({result['coverage']:.0f}%)")
    print(f"  NOTES    : {result['notes']}")
    print(f"  SIMPLIFIED EXPECTED : {result['simplified_expected']}")
    print(f"  SIMPLIFIED ACTUAL   : {result['simplified_actual']}")
    print(f"  FLAMELANG-M2        : {result['flamelang_type_note']}")
    if log:
        h = sha256_log(actual, log_path)
        print(f"  SHA-256  : {h}")
    print(f"{'='*60}")


MOBIUS_ANTIBODIES = [
    {
        "id":      "AB-PAREN-FRAC-001",
        "trigger": lambda s: "/" in s and "(" not in s,
        "msg":     "MISSING PARENS around numerator/denominator. '5x+1/y-2' → '(5x+1)/(y-2)'",
    },
    {
        "id":      "AB-SQRT-SYMBOL-001",
        "trigger": lambda s: s.strip().startswith("s") and "q" in s and "r" in s and "t" in s,
        "msg":     "SQRT SYMBOL MODE TRAP. Use 'sqrt(x)' in text mode or '((x)/(1))^(1/2)' in symbol mode.",
    },
    {
        "id":      "AB-ABS-SYMBOL-001",
        "trigger": lambda s: "|" in s,
        "msg":     "ABS BARS TRAP. Use 'abs(x)' in text mode, not |x|.",
    },
    {
        "id":      "AB-IMPLICIT-MUL-001",
        "trigger": lambda s: any(
            c.isdigit() and s[i+1:i+2].isalpha()
            for i, c in enumerate(s[:-1])
        ),
        "msg":     "IMPLICIT MULTIPLICATION. '2x' is accepted in sympy but Mobius may need '2*x'.",
    },
]


def fire_antibodies(expr_str: str) -> list[str]:
    """Check a Mobius input string against all known antibodies."""
    fired = []
    for ab in MOBIUS_ANTIBODIES:
        try:
            if ab["trigger"](expr_str):
                fired.append(f"  [{ab['id']}] {ab['msg']}")
        except Exception:
            pass
    return fired


def run_antibodies(expr_str: str) -> None:
    fired = fire_antibodies(expr_str)
    if fired:
        print(f"\n  ANTIBODIES FIRED for: {expr_str!r}")
        for msg in fired:
            print(msg)
    else:
        print(f"  No antibodies fired for: {expr_str!r}")


KNOWN_PROBLEMS = [
    # (description, expected_text_mode, correct_text_mode_answer)
    ("Fraction: (x+7/15)/19 + 9",        "(x+7/15)/19 + 9",    "(x + 7/15)/19 + 9"),
    ("Simple fraction: (5x+1)/(y-2)",     "(5*x+1)/(y-2)",      "(5*x+1)/(y-2)"),
    ("Reciprocal: 1/(x+1)",               "1/(x+1)",            "1/(x+1)"),
    ("Exponent: x^n",                     "x**n",               "x**n"),
    ("Absolute value: |x|",               "Abs(x)",             "Abs(x)"),
    ("Square root: sqrt(x)",              "sqrt(x)",            "sqrt(x)"),
    ("Complex frac: (x+5)/(y+9z-11)",     "(x+5)/(y+9*z-11)",   "(x+5)/(y+9*z-11)"),
]


def run_known_problems() -> None:
    print("\n  MAT-225 KNOWN PROBLEM SUITE")
    print("  " + "-"*56)
    passed = 0
    for desc, expected, actual in KNOWN_PROBLEMS:
        r = eru_verdict(expected, actual)
        status = "PASS" if r["verdict"] == "PROVEN" else "FAIL"
        if status == "PASS":
            passed += 1
        print(f"  [{status}] {desc}")
        if status == "FAIL":
            print(f"         diff={r['notes']}")
    print(f"\n  BurnRate: {passed}/{len(KNOWN_PROBLEMS)} = {passed/len(KNOWN_PROBLEMS)*100:.0f}%")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "suite":
        run_known_problems()

    elif args[0] == "check" and len(args) >= 3:
        validate(args[1], args[2])

    elif args[0] == "antibody" and len(args) >= 2:
        run_antibodies(args[1])

    elif args[0] == "hash" and len(args) >= 2:
        log_path = os.path.join(os.path.dirname(__file__), "../evidence/submissions.log")
        h = sha256_log(args[1], log_path)
        print(f"SHA-256: {h}")
        print(f"Logged to: {log_path}")

    else:
        print("""
flamec_calc_validator.py — MAT-225 ERU Validator / FlameLang M2 Bridge

USAGE:
  python flamec_calc_validator.py suite
    Run all known MAT-225 problems and report BurnRate

  python flamec_calc_validator.py check "expected_expr" "actual_expr"
    Run ERU verdict on a single pair (text-mode strings)

  python flamec_calc_validator.py antibody "expr_str"
    Fire antibodies against a single expression string

  python flamec_calc_validator.py hash "answer_str"
    SHA-256 hash an answer and append to evidence/submissions.log

EXAMPLES:
  python flamec_calc_validator.py check "(5*x+1)/(y-2)" "(5x+1)/(y-2)"
  python flamec_calc_validator.py check "1/(x+1)" "1/x+1"
  python flamec_calc_validator.py antibody "sqrtx"
  python flamec_calc_validator.py antibody "5x+1/y-2"
        """)
