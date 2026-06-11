#[derive(Debug, Clone)]
pub enum AccessType {
    Ground,
    Ladder,
    Rope,
    Manlift,
}

impl Default for AccessType {
    fn default() -> Self {
        AccessType::Ground
    }
}

impl std::fmt::Display for AccessType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            AccessType::Ground  => write!(f, "ground"),
            AccessType::Ladder  => write!(f, "ladder"),
            AccessType::Rope    => write!(f, "rope"),
            AccessType::Manlift => write!(f, "manlift"),
        }
    }
}

#[derive(Debug, Clone)]
pub struct CutNode {
    pub id: String,
    pub description: Option<String>,
    pub cost_code: Option<String>,
    pub lnf_total: f64,
    pub lnf_done: f64,
    pub estimate_hrs: f64,
    pub used_hrs: f64,
    pub elevation_ft: f64,
    pub bands: u32,
    pub metal: bool,
    pub access: AccessType,
}

impl Default for CutNode {
    fn default() -> Self {
        CutNode {
            id: String::new(),
            description: None,
            cost_code: None,
            lnf_total: 0.0,
            lnf_done: 0.0,
            estimate_hrs: 0.0,
            used_hrs: 0.0,
            elevation_ft: 0.0,
            bands: 1,
            metal: false,
            access: AccessType::Ground,
        }
    }
}

#[derive(Debug, Clone)]
pub struct CircuitNode {
    pub id: String,
    pub cuts: Vec<CutNode>,
}

#[derive(Debug, Clone)]
pub struct ProjectNode {
    pub name: String,
    pub circuits: Vec<CircuitNode>,
}
