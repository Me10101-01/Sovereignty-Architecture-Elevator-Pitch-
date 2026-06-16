#!/usr/bin/env python3
"""
test_validator.py — ERU unit tests for flamec_calc_validator.py
Every test case is a real MAT-225 / Mobius gotcha turned into a provable claim.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from flamec_calc_validator import eru_verdict, fire_antibodies, mobius_parse

import sympy


def test_exact_fraction_match():
    r = eru_verdict("(5*x+1)/(y-2)", "(5*x+1)/(y-2)")
    assert r["verdict"] == "PROVEN", f"Expected PROVEN, got {r['verdict']}: {r['notes']}"


def test_implicit_mul_equivalent():
    r = eru_verdict("2*x + 1", "2*x+1")
    assert r["verdict"] == "PROVEN", f"Expected PROVEN, got {r}"


def test_paren_trap_catches_wrong():
    r = eru_verdict("(x+1)/2", "x+1/2")
    assert r["verdict"] != "PROVEN", f"Should not be PROVEN: parens missing in actual"


def test_reciprocal_paren_trap():
    r = eru_verdict("1/(x+1)", "1/x+1")
    assert r["verdict"] != "PROVEN", f"Should not be PROVEN: 1/(x+1) != 1/x+1"


def test_sqrt_text_mode():
    r = eru_verdict("sqrt(x)", "sqrt(x)")
    assert r["verdict"] == "PROVEN"


def test_abs_text_mode():
    r = eru_verdict("Abs(x)", "Abs(x)")
    assert r["verdict"] == "PROVEN"


def test_antibody_paren_frac():
    fired = fire_antibodies("5x+1/y-2")
    assert any("AB-PAREN-FRAC-001" in f for f in fired), f"Expected AB-PAREN-FRAC-001, got {fired}"


def test_antibody_abs_bars():
    fired = fire_antibodies("|x|")
    assert any("AB-ABS-SYMBOL-001" in f for f in fired), f"Expected AB-ABS-SYMBOL-001, got {fired}"


def test_power_rule_derivative():
    import sympy
    x = sympy.Symbol("x")
    expr = x**3
    deriv = sympy.diff(expr, x)
    expected = 3 * x**2
    assert sympy.simplify(deriv - expected) == 0


def test_flamelang_type_note_populated():
    r = eru_verdict("x + 1", "x + 1")
    assert "flamelang_type_note" in r
    assert len(r["flamelang_type_note"]) > 0


TESTS = [
    ("exact_fraction_match",        test_exact_fraction_match),
    ("implicit_mul_equivalent",     test_implicit_mul_equivalent),
    ("paren_trap_catches_wrong",    test_paren_trap_catches_wrong),
    ("reciprocal_paren_trap",       test_reciprocal_paren_trap),
    ("sqrt_text_mode",              test_sqrt_text_mode),
    ("abs_text_mode",               test_abs_text_mode),
    ("antibody_paren_frac",         test_antibody_paren_frac),
    ("antibody_abs_bars",           test_antibody_abs_bars),
    ("power_rule_derivative",       test_power_rule_derivative),
    ("flamelang_type_note_pop",     test_flamelang_type_note_populated),
]


if __name__ == "__main__":
    passed = 0
    failed = 0
    for name, fn in TESTS:
        try:
            fn()
            print(f"  PASS  {name}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {name}: {e}")
            failed += 1

    total = passed + failed
    burnrate = passed / total * 100 if total > 0 else 0
    print(f"\n  BurnRate: {passed}/{total} = {burnrate:.0f}%")
    verdict = "PROVEN" if burnrate == 100 else "PROMISING" if burnrate >= 50 else "UNPROVEN"
    print(f"  Verdict: {verdict}")
    sys.exit(0 if failed == 0 else 1)
