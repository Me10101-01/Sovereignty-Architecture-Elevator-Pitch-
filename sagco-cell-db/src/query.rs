/// Query engine — brick 3.
///
/// Parses and evaluates filter expressions against cells.
///
/// Filter syntax:  key=value   concept=chain_rule   table.key=value
/// Compound:       concept=chain_rule AND subject=MAT225
/// Prefix scan:    key^=chain   (starts-with)
/// Substring:      key~=rule    (contains)

use crate::cell::Cell;

#[derive(Debug, Clone, PartialEq)]
pub enum Op {
    Eq,        // key=val
    StartsWith, // key^=val
    Contains,  // key~=val
    NotEq,     // key!=val
}

#[derive(Debug, Clone)]
pub struct Filter {
    pub field: Field,
    pub op: Op,
    pub value: Vec<u8>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Field {
    Key,
    Value,
    Named(String),  // for structured value fields (JSON)
}

impl Filter {
    /// Parse a filter string like `key=chain_rule` or `concept~=calculus`.
    pub fn parse(s: &str) -> Result<Self, String> {
        // Check operators in longest-first order
        if let Some(idx) = s.find("^=") {
            let field = parse_field(&s[..idx]);
            let val = s[idx + 2..].as_bytes().to_vec();
            return Ok(Filter { field, op: Op::StartsWith, value: val });
        }
        if let Some(idx) = s.find("~=") {
            let field = parse_field(&s[..idx]);
            let val = s[idx + 2..].as_bytes().to_vec();
            return Ok(Filter { field, op: Op::Contains, value: val });
        }
        if let Some(idx) = s.find("!=") {
            let field = parse_field(&s[..idx]);
            let val = s[idx + 2..].as_bytes().to_vec();
            return Ok(Filter { field, op: Op::NotEq, value: val });
        }
        if let Some(idx) = s.find('=') {
            let field = parse_field(&s[..idx]);
            let val = s[idx + 1..].as_bytes().to_vec();
            return Ok(Filter { field, op: Op::Eq, value: val });
        }
        Err(format!("cannot parse filter: {:?} — expected field=value", s))
    }

    /// Returns true if this cell matches the filter.
    pub fn matches(&self, cell: &Cell) -> bool {
        let target = match &self.field {
            Field::Key   => &cell.key,
            Field::Value => &cell.value,
            Field::Named(name) => {
                // Try to parse cell.value as JSON and extract the named field
                if let Ok(s) = std::str::from_utf8(&cell.value) {
                    if let Ok(v) = serde_json::from_str::<serde_json::Value>(s) {
                        if let Some(fv) = v.get(name) {
                            let fv_str = match fv {
                                serde_json::Value::String(s) => s.clone(),
                                other => other.to_string(),
                            };
                            return apply_op(&self.op, fv_str.as_bytes(), &self.value);
                        }
                    }
                }
                // Named field not found — treat value as flat string
                &cell.value
            }
        };
        apply_op(&self.op, target, &self.value)
    }
}

fn parse_field(s: &str) -> Field {
    match s {
        "key"   => Field::Key,
        "value" => Field::Value,
        other   => Field::Named(other.to_string()),
    }
}

fn apply_op(op: &Op, target: &[u8], value: &[u8]) -> bool {
    match op {
        Op::Eq         => target == value,
        Op::NotEq      => target != value,
        Op::StartsWith => target.starts_with(value),
        Op::Contains   => {
            target.windows(value.len()).any(|w| w == value)
        }
    }
}

/// A query is a list of filters (all must match — implicit AND).
#[derive(Debug, Clone, Default)]
pub struct Query {
    pub filters: Vec<Filter>,
    pub limit: Option<usize>,
}

impl Query {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn filter(mut self, f: Filter) -> Self {
        self.filters.push(f);
        self
    }

    pub fn limit(mut self, n: usize) -> Self {
        self.limit = Some(n);
        self
    }

    /// Parse a list of filter strings (space or AND separated).
    pub fn parse(args: &[&str]) -> Result<Self, String> {
        let mut q = Query::new();
        for arg in args {
            let part = arg.trim();
            if part.is_empty() || part.eq_ignore_ascii_case("AND") {
                continue;
            }
            q.filters.push(Filter::parse(part)?);
        }
        Ok(q)
    }

    pub fn matches(&self, cell: &Cell) -> bool {
        self.filters.iter().all(|f| f.matches(cell))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cell::Cell;

    fn cell(key: &str, val: &str) -> Cell {
        Cell::new(key.as_bytes().to_vec(), val.as_bytes().to_vec())
    }

    #[test]
    fn eq_key() {
        let f = Filter::parse("key=PA8").unwrap();
        assert!(f.matches(&cell("PA8", "anything")));
        assert!(!f.matches(&cell("PA9", "anything")));
    }

    #[test]
    fn contains_value() {
        let f = Filter::parse("value~=chain").unwrap();
        assert!(f.matches(&cell("any", "chain_rule")));
        assert!(!f.matches(&cell("any", "product_rule")));
    }

    #[test]
    fn starts_with_key() {
        let f = Filter::parse("key^=PA").unwrap();
        assert!(f.matches(&cell("PA8", "v")));
        assert!(!f.matches(&cell("HW1", "v")));
    }

    #[test]
    fn named_field_json() {
        let val = r#"{"concept":"chain_rule","subject":"MAT225"}"#;
        let c = cell("k", val);
        let f = Filter::parse("concept=chain_rule").unwrap();
        assert!(f.matches(&c));
        let f2 = Filter::parse("subject~=MAT").unwrap();
        assert!(f2.matches(&c));
    }

    #[test]
    fn compound_query() {
        let q = Query::parse(&["key^=PA", "value~=chain"]).unwrap();
        assert!(q.matches(&cell("PA8", "chain_rule")));
        assert!(!q.matches(&cell("PA8", "product_rule")));
        assert!(!q.matches(&cell("HW1", "chain_rule")));
    }
}
