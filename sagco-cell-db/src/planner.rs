/// Query planner — brick 5.
///
/// Chooses the cheapest execution path for a query:
///   - Index point lookup (O(1)) — when filter is key=<exact>
///   - Index existence check + scan  — when index says key exists
///   - Full table scan — fallback
///
/// Emits a Plan that the executor runs.

use crate::query::{Field, Filter, Op, Query};

#[derive(Debug, Clone, PartialEq)]
pub enum Plan {
    /// Single key lookup using the index. Fastest path.
    IndexGet { key: Vec<u8> },
    /// Index confirms key exists, then fetch from page.
    IndexScan { keys: Vec<Vec<u8>> },
    /// Walk every live cell in the page file.
    FullScan,
}

impl Plan {
    pub fn describe(&self) -> &'static str {
        match self {
            Plan::IndexGet { .. } => "INDEX_GET",
            Plan::IndexScan { .. } => "INDEX_SCAN",
            Plan::FullScan => "FULL_SCAN",
        }
    }
}

pub fn plan(q: &Query) -> Plan {
    // Look for a key=<exact> filter — best case
    for f in &q.filters {
        if f.field == Field::Key && f.op == Op::Eq {
            return Plan::IndexGet { key: f.value.clone() };
        }
    }

    // Look for key^= (prefix) — can walk index keys
    for f in &q.filters {
        if f.field == Field::Key && f.op == Op::StartsWith {
            // We don't have a B-tree yet, so this falls back to full scan
            // but the planner documents the intent
            return Plan::FullScan;
        }
    }

    // Named field or value filter — need full scan
    Plan::FullScan
}

/// Explain the plan for a query.
pub fn explain(q: &Query) -> String {
    let p = plan(q);
    let filters: Vec<String> = q.filters.iter().map(|f| {
        let field = match &f.field {
            crate::query::Field::Key => "key".to_string(),
            crate::query::Field::Value => "value".to_string(),
            crate::query::Field::Named(n) => n.clone(),
        };
        let op = match f.op {
            Op::Eq         => "=",
            Op::NotEq      => "!=",
            Op::StartsWith => "^=",
            Op::Contains   => "~=",
        };
        let val = String::from_utf8_lossy(&f.value).to_string();
        format!("{}{}{}", field, op, val)
    }).collect();

    format!(
        "PLAN: {}  FILTERS: [{}]  LIMIT: {}",
        p.describe(),
        filters.join(", "),
        q.limit.map(|l| l.to_string()).unwrap_or_else(|| "none".to_string()),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::query::{Filter, Query};

    #[test]
    fn exact_key_gets_index_get() {
        let q = Query::parse(&["key=PA8"]).unwrap();
        assert_eq!(plan(&q), Plan::IndexGet { key: b"PA8".to_vec() });
    }

    #[test]
    fn value_filter_gets_full_scan() {
        let q = Query::parse(&["value~=chain"]).unwrap();
        assert_eq!(plan(&q), Plan::FullScan);
    }

    #[test]
    fn named_field_gets_full_scan() {
        let q = Query::parse(&["concept=chain_rule"]).unwrap();
        assert_eq!(plan(&q), Plan::FullScan);
    }
}
