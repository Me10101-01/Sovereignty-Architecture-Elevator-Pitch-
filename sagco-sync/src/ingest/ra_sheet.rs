#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct Cut {
    pub id: String,
    pub description: String,
    pub cost_code: String,
    pub lnf_total: f64,
    pub lnf_done: f64,
    pub estimate_hrs: f64,
    pub used_hrs: f64,
    pub elevation_ft: f64,
    pub bands: u32,
    pub metal: bool,
    pub access: String,
}

impl Cut {
    pub fn variance_hrs(&self) -> f64 {
        self.estimate_hrs - self.used_hrs
    }

    pub fn pct_lnf_done(&self) -> f64 {
        if self.lnf_total == 0.0 {
            0.0
        } else {
            self.lnf_done / self.lnf_total
        }
    }

    pub fn ev(&self) -> f64 {
        self.pct_lnf_done() * self.estimate_hrs
    }

    pub fn cpi(&self) -> f64 {
        if self.used_hrs == 0.0 {
            0.0
        } else {
            self.ev() / self.used_hrs
        }
    }

    pub fn implied_rate(&self) -> f64 {
        if self.lnf_total == 0.0 {
            0.0
        } else {
            self.estimate_hrs / self.lnf_total
        }
    }
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct Circuit {
    pub id: String,
    pub cuts: Vec<Cut>,
}

impl Circuit {
    pub fn total_pv(&self) -> f64 {
        self.cuts.iter().map(|c| c.estimate_hrs).sum()
    }

    pub fn total_ac(&self) -> f64 {
        self.cuts.iter().map(|c| c.used_hrs).sum()
    }

    pub fn total_ev(&self) -> f64 {
        self.cuts.iter().map(|c| c.ev()).sum()
    }

    pub fn circuit_cpi(&self) -> f64 {
        let ac = self.total_ac();
        if ac == 0.0 {
            0.0
        } else {
            self.total_ev() / ac
        }
    }

    pub fn circuit_eac(&self) -> f64 {
        let cpi = self.circuit_cpi();
        if cpi == 0.0 {
            f64::INFINITY
        } else {
            self.total_pv() / cpi
        }
    }
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct RASheet {
    pub project_name: String,
    pub circuits: Vec<Circuit>,
}

impl RASheet {
    pub fn total_pv(&self) -> f64 {
        self.circuits.iter().map(|c| c.total_pv()).sum()
    }

    pub fn total_ac(&self) -> f64 {
        self.circuits.iter().map(|c| c.total_ac()).sum()
    }

    pub fn total_ev(&self) -> f64 {
        self.circuits.iter().map(|c| c.total_ev()).sum()
    }

    pub fn project_cpi(&self) -> f64 {
        let ac = self.total_ac();
        if ac == 0.0 {
            0.0
        } else {
            self.total_ev() / ac
        }
    }

    pub fn project_eac(&self) -> f64 {
        let cpi = self.project_cpi();
        if cpi == 0.0 {
            f64::INFINITY
        } else {
            self.total_pv() / cpi
        }
    }
}
