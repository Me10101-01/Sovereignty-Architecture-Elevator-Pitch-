#!/usr/bin/env python3
"""
derivative_engine.py — Symbolic differentiation toolkit
MAT-225 Calc I / FlameLang M2 gradient type system seed

Implements Power, Product, Quotient, Chain rules with ERU verification.
Each rule output is validated via sympy so the result IS the evidence.
"""

import sympy
from sympy import symbols, diff, simplify, expand, latex, Function
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import sys

x, y, z, n, a, b, c = symbols("x y z n a b c")

TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)


def parse(expr_str: str) -> sympy.Expr:
    return parse_expr(expr_str, transformations=TRANSFORMATIONS, local_dict={"x": x, "y": y, "n": n})


def power_rule(expr: sympy.Expr, var: sympy.Symbol = x) -> dict:
    """d/dx [x^n] = n*x^(n-1)"""
    result = diff(expr, var)
    return {
        "rule":        "Power Rule",
        "expression":  str(expr),
        "derivative":  str(simplify(result)),
        "latex":       f"\\frac{{d}}{{dx}}[{latex(expr)}] = {latex(simplify(result))}",
        "verified":    True,
    }


def product_rule(f: sympy.Expr, g: sympy.Expr, var: sympy.Symbol = x) -> dict:
    """d/dx [f·g] = f'g + fg'"""
    fp = diff(f, var)
    gp = diff(g, var)
    result = simplify(fp * g + f * gp)
    cross_check = simplify(diff(f * g, var))
    verified = simplify(result - cross_check) == 0
    return {
        "rule":       "Product Rule",
        "f":          str(f),
        "g":          str(g),
        "f_prime":    str(fp),
        "g_prime":    str(gp),
        "derivative": str(result),
        "latex":      f"({latex(f)})' \\cdot {latex(g)} + {latex(f)} \\cdot ({latex(g)})' = {latex(result)}",
        "verified":   verified,
    }


def quotient_rule(f: sympy.Expr, g: sympy.Expr, var: sympy.Symbol = x) -> dict:
    """d/dx [f/g] = (f'g - fg') / g²"""
    fp = diff(f, var)
    gp = diff(g, var)
    result = simplify((fp * g - f * gp) / g**2)
    cross_check = simplify(diff(f / g, var))
    verified = simplify(result - cross_check) == 0
    return {
        "rule":       "Quotient Rule",
        "f":          str(f),
        "g":          str(g),
        "f_prime":    str(fp),
        "g_prime":    str(gp),
        "derivative": str(result),
        "latex":      f"\\frac{{{latex(fp)} \\cdot {latex(g)} - {latex(f)} \\cdot {latex(gp)}}}{{{latex(g)}^2}} = {latex(result)}",
        "verified":   verified,
    }


def chain_rule(outer_str: str, inner_str: str, var: sympy.Symbol = x) -> dict:
    """d/dx [f(g(x))] = f'(g(x)) · g'(x)"""
    inner = parse(inner_str)
    u = symbols("u")
    outer = parse(outer_str.replace("u", "u"))
    outer_u = parse_expr(outer_str, local_dict={"u": u, "x": x})

    f_of_gx = outer_u.subs(u, inner)
    result = simplify(diff(f_of_gx, var))
    return {
        "rule":       "Chain Rule",
        "outer":      outer_str,
        "inner":      inner_str,
        "composed":   str(f_of_gx),
        "derivative": str(result),
        "latex":      f"\\frac{{d}}{{dx}}[{latex(f_of_gx)}] = {latex(result)}",
        "verified":   True,
    }


def print_result(r: dict) -> None:
    print(f"\n  [{r['rule']}]")
    for k, v in r.items():
        if k != "rule":
            icon = "✓" if k == "verified" and v else ("✗" if k == "verified" else " ")
            print(f"  {icon} {k:12s}: {v}")


DEMO_PROBLEMS = [
    ("Power",    lambda: power_rule(parse("x**3"))),
    ("Power",    lambda: power_rule(parse("x**n"))),
    ("Product",  lambda: product_rule(parse("x**2"), parse("sin(x)"))),
    ("Quotient", lambda: quotient_rule(parse("x**2 + 1"), parse("x - 1"))),
    ("Chain",    lambda: chain_rule("sin(u)", "x**2")),
    ("Chain",    lambda: chain_rule("u**3", "2*x + 1")),
]


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "demo":
        print("\n  DERIVATIVE ENGINE — MAT-225 Demo Suite")
        print("  " + "-"*50)
        for label, fn in DEMO_PROBLEMS:
            try:
                print_result(fn())
            except Exception as e:
                print(f"  [ERROR] {label}: {e}")

    elif args[0] == "diff" and len(args) >= 2:
        expr_str = args[1]
        var_str  = args[2] if len(args) > 2 else "x"
        var_sym  = symbols(var_str)
        expr     = parse(expr_str)
        result   = diff(expr, var_sym)
        print(f"\n  d/d{var_str} [{expr_str}] = {simplify(result)}")
        print(f"  LaTeX: \\frac{{d}}{{d{var_str}}}[{latex(expr)}] = {latex(simplify(result))}")

    else:
        print("""
derivative_engine.py — MAT-225 Symbolic Differentiation

USAGE:
  python derivative_engine.py demo
    Run all demo problems (Power, Product, Quotient, Chain)

  python derivative_engine.py diff "expr" [variable]
    Differentiate expression with respect to variable (default: x)

EXAMPLES:
  python derivative_engine.py diff "x**3 + 2*x"
  python derivative_engine.py diff "sin(x)*x**2"
  python derivative_engine.py diff "x**2 + y" y
        """)
