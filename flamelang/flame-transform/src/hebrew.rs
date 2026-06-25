// L3 — Hebrew transform: walk the AST and collect gematria weights
// Each identifier and string literal is mapped to its cumulative value.

use anyhow::Result;
use flame_parser::{Expr, Program, Statement};
use flametoken::word_gematria;

pub fn extract(program: &Program) -> Result<Vec<(String, u32)>> {
    let mut out = Vec::new();
    for stmt in &program.stmts {
        collect_expr(&stmt.expr, &mut out);
    }
    Ok(out)
}

fn collect_expr(expr: &Expr, out: &mut Vec<(String, u32)>) {
    match expr {
        Expr::Ident(name) => {
            let g = word_gematria(name);
            if g > 0 { out.push((name.clone(), g)); }
        }
        Expr::StringLit(s) => {
            let g = word_gematria(s);
            if g > 0 { out.push((s.clone(), g)); }
        }
        Expr::HebChar { codepoint, gematria } => {
            out.push((codepoint.to_string(), *gematria));
        }
        Expr::GlyphRoute { namespace, modifier } => {
            out.push((namespace.clone(), word_gematria(namespace)));
            if let Some(m) = modifier {
                out.push((m.clone(), word_gematria(m)));
            }
        }
        Expr::BindingCode(n) => { out.push((format!("[{}]", n), *n)); }
        Expr::BinOp { lhs, rhs, .. } => {
            collect_expr(lhs, out);
            collect_expr(rhs, out);
        }
        Expr::Dispatch { payload, .. } => collect_expr(payload, out),
        Expr::Email { to, subject, body } => {
            collect_expr(to, out);
            collect_expr(subject, out);
            collect_expr(body, out);
        }
        Expr::Audit { component, event, data } => {
            out.push((component.clone(), word_gematria(component)));
            out.push((event.clone(), word_gematria(event)));
            collect_expr(data, out);
        }
        _ => {}
    }
}
