use crate::ingest::ra_sheet::{Circuit, RASheet};

#[derive(Debug, Clone, serde::Serialize)]
pub struct EVMSnapshot {
    pub id: String,
    /// Planned Value = estimate_hrs
    pub pv: f64,
    /// Actual Cost = used_hrs
    pub ac: f64,
    /// Earned Value = pct_done × pv
    pub ev: f64,
    /// Cost Variance = ev - ac
    pub cv: f64,
    /// Schedule Variance = ev - pv
    pub sv: f64,
    /// Cost Performance Index = ev / ac
    pub cpi: f64,
    /// Schedule Performance Index = ev / pv
    pub spi: f64,
    /// Estimate at Completion = pv / cpi
    pub eac: f64,
    /// Estimate to Complete = eac - ac
    pub etc: f64,
    /// To-Complete CPI = (pv - ev) / (pv - ac)
    pub tcpi: f64,
    /// ev / pv
    pub pct_complete: f64,
    /// ac / pv
    pub pct_spent: f64,
}

impl EVMSnapshot {
    pub fn from_circuit(c: &Circuit) -> Self {
        let pv = c.total_pv();
        let ac = c.total_ac();
        let ev = c.total_ev();
        Self::compute(c.id.clone(), pv, ac, ev)
    }

    pub fn from_project(p: &RASheet) -> Self {
        let pv = p.total_pv();
        let ac = p.total_ac();
        let ev = p.total_ev();
        Self::compute(p.project_name.clone(), pv, ac, ev)
    }

    fn compute(id: String, pv: f64, ac: f64, ev: f64) -> Self {
        let cv = ev - ac;
        let sv = ev - pv;

        let cpi = if ac == 0.0 { 0.0 } else { ev / ac };
        let spi = if pv == 0.0 { 0.0 } else { ev / pv };

        let eac = if cpi == 0.0 { f64::INFINITY } else { pv / cpi };
        let etc = if eac.is_infinite() { f64::INFINITY } else { eac - ac };

        let work_remaining = pv - ev;
        let budget_remaining = pv - ac;
        let tcpi = if budget_remaining == 0.0 {
            if work_remaining == 0.0 { 1.0 } else { f64::INFINITY }
        } else {
            work_remaining / budget_remaining
        };

        let pct_complete = if pv == 0.0 { 0.0 } else { ev / pv };
        let pct_spent = if pv == 0.0 { 0.0 } else { ac / pv };

        EVMSnapshot {
            id,
            pv,
            ac,
            ev,
            cv,
            sv,
            cpi,
            spi,
            eac,
            etc,
            tcpi,
            pct_complete,
            pct_spent,
        }
    }

    pub fn status(&self) -> &'static str {
        if self.cpi >= 1.0 {
            "AHEAD"
        } else if self.cpi >= 0.8 {
            "WARNING"
        } else {
            "OVERRUN"
        }
    }

    pub fn status_icon(&self) -> &'static str {
        match self.status() {
            "AHEAD" => "✓",
            "WARNING" => "~",
            _ => "✗",
        }
    }
}
