/// bubble.rs
/// SAGCO-Core Bubble State Machine
///
/// Converts engineering field data into executable logic states.
/// Origin: rope access pipe inspection tracking (RB = Red Bubble).
///
/// State encoding (3-bit):
///   000 = IDLE     — record exists, no inspection started
///   101 = ACTIVE   — inspection underway, partial data collected
///   111 = VERIFIED — all tasks complete, all data confirmed
///
/// Input: "RB-001 4 27 1 0 N E UP"
///   RB-001  = bubble identifier
///   4       = pipe diameter (inches)
///   27      = band count (inspection wraps applied)
///   1       = rope_access required (1=yes, 0=no)
///   0       = ground_accessible (1=yes, 0=no)
///   N E     = horizontal direction pins (compass)
///   UP      = vertical orientation

use std::f64::consts::PI;

// ─── STATE ─────────────────────────────────────────────────────

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BubbleState {
    Idle,       // 000
    Active,     // 101
    Verified,   // 111
}

impl BubbleState {
    pub fn code(&self) -> &'static str {
        match self {
            BubbleState::Idle     => "000_IDLE",
            BubbleState::Active   => "101_ACTIVE",
            BubbleState::Verified => "111_VERIFIED",
        }
    }

    pub fn bits(&self) -> u8 {
        match self {
            BubbleState::Idle     => 0b000,
            BubbleState::Active   => 0b101,
            BubbleState::Verified => 0b111,
        }
    }
}

// ─── FIELD RECORD ──────────────────────────────────────────────

#[derive(Debug, Clone)]
pub struct BubbleRecord {
    pub id:               String,
    pub pipe_diameter_in: f64,
    pub band_count:       u32,
    pub rope_access:      bool,
    pub ground_accessible: bool,
    pub dir_h:            String,    // compass: N, NE, E, SE, S, SW, W, NW
    pub dir_v:            String,    // UP or DOWN
    pub state:            BubbleState,
}

// ─── COMPUTED MEASUREMENTS ────────────────────────────────────

#[derive(Debug, Clone)]
pub struct BubbleMeasurements {
    pub linear_feet:   f64,
    pub square_feet:   f64,
    pub circumference: f64,    // feet
    pub state:         BubbleState,
    pub next_action:   &'static str,
}

impl BubbleRecord {
    /// Parse from tokenized field input.
    ///
    /// Format: <id> <pipe_dia_in> <band_count> <rope_access> <ground_accessible>
    ///         <dir_h> <dir_v> [<orientation>]
    ///
    /// Example: "RB-001 4 27 1 0 N E UP"
    pub fn parse(input: &str) -> Result<Self, String> {
        let parts: Vec<&str> = input.split_whitespace().collect();
        if parts.len() < 7 {
            return Err(format!(
                "Expected ≥7 fields, got {}. Format: <id> <pipe_dia> <bands> <rope> <ground> <dir_h> <dir_v>",
                parts.len()
            ));
        }

        let id = parts[0].to_string();

        let pipe_diameter_in: f64 = parts[1].parse()
            .map_err(|_| format!("pipe_diameter must be a number, got '{}'", parts[1]))?;
        if pipe_diameter_in <= 0.0 || pipe_diameter_in > 120.0 {
            return Err(format!("pipe_diameter {} out of range (0, 120]", pipe_diameter_in));
        }

        let band_count: u32 = parts[2].parse()
            .map_err(|_| format!("band_count must be an integer, got '{}'", parts[2]))?;

        let rope_access: bool = match parts[3] {
            "1" | "true"  | "yes" => true,
            "0" | "false" | "no"  => false,
            other => return Err(format!("rope_access must be 0 or 1, got '{}'", other)),
        };

        let ground_accessible: bool = match parts[4] {
            "1" | "true"  | "yes" => true,
            "0" | "false" | "no"  => false,
            other => return Err(format!("ground_accessible must be 0 or 1, got '{}'", other)),
        };

        let dir_h = parts[5].to_uppercase();
        let dir_v = parts[6].to_uppercase();

        // Determine initial state from field data
        let state = compute_state(band_count, rope_access, ground_accessible);

        Ok(BubbleRecord {
            id,
            pipe_diameter_in,
            band_count,
            rope_access,
            ground_accessible,
            dir_h,
            dir_v,
            state,
        })
    }

    /// Compute measurements from field record.
    pub fn measure(&self) -> BubbleMeasurements {
        // Pipe circumference in feet: π × diameter_in / 12
        let circumference = PI * self.pipe_diameter_in / 12.0;

        // Each band = 1 linear foot of pipe coverage (industry standard for this format)
        let linear_feet = self.band_count as f64;

        // Surface area = linear extent × circumference
        let square_feet = linear_feet * circumference;

        let next_action = next_action_for(self.state, self.rope_access, self.ground_accessible);

        BubbleMeasurements {
            linear_feet,
            square_feet,
            circumference,
            state: self.state,
            next_action,
        }
    }
}

// ─── STATE LOGIC ───────────────────────────────────────────────

fn compute_state(band_count: u32, rope_access: bool, ground_accessible: bool) -> BubbleState {
    if band_count == 0 {
        return BubbleState::Idle;
    }

    // Verified: bands recorded AND accessible by at least one method
    if band_count > 0 && (rope_access || ground_accessible) {
        // Full verification requires both directions confirmed
        if rope_access && ground_accessible {
            return BubbleState::Verified;
        }
        // Partial: one access method, bands recorded
        return BubbleState::Active;
    }

    BubbleState::Idle
}

fn next_action_for(state: BubbleState, rope_access: bool, ground_accessible: bool) -> &'static str {
    match state {
        BubbleState::Idle     => "INITIATE_INSPECTION — assign crew, begin band application",
        BubbleState::Active   => {
            if rope_access && !ground_accessible {
                "COMPLETE_ROPE_ACCESS — confirm ground isolation, then verify"
            } else {
                "CONFIRM_SECONDARY_ACCESS — verify remaining access path"
            }
        }
        BubbleState::Verified => "CLOSE_RECORD — submit for sign-off, archive evidence",
    }
}

// ─── PRINT ─────────────────────────────────────────────────────

pub fn print_bubble_result(rec: &BubbleRecord, m: &BubbleMeasurements) {
    println!("╔══════════════════════════════════════════╗");
    println!("║  SAGCO-CORE BUBBLE ENGINE               ║");
    println!("╠══════════════════════════════════════════╣");
    println!("║  ID:            {:25} ║", rec.id);
    println!("║  Pipe Dia:      {:.2} in  Circ: {:.4} ft  ║",
             rec.pipe_diameter_in, m.circumference);
    println!("║  Bands:         {:5}                    ║", rec.band_count);
    println!("║  Rope Access:   {:5}  Ground: {:5}     ║",
             rec.rope_access, rec.ground_accessible);
    println!("║  Direction:     {} {}                      ║", rec.dir_h, rec.dir_v);
    println!("╠══════════════════════════════════════════╣");
    println!("║  linear_feet:   {:.6}               ║", m.linear_feet);
    println!("║  square_feet:   {:.6}               ║", m.square_feet);
    println!("║  state:         {:25} ║", m.state.code());
    println!("╠══════════════════════════════════════════╣");
    println!("║  next_action:                            ║");
    // Wrap long next_action
    for chunk in m.next_action.as_bytes().chunks(40) {
        println!("║    {:<40} ║", std::str::from_utf8(chunk).unwrap_or("?"));
    }
    println!("╚══════════════════════════════════════════╝");
    println!("STATUS=BUBBLE_{}", m.state.code());
}

// ─── TESTS ─────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rb001_parse() {
        let rec = BubbleRecord::parse("RB-001 4 27 1 0 N E UP").unwrap();
        assert_eq!(rec.id, "RB-001");
        assert_eq!(rec.pipe_diameter_in, 4.0);
        assert_eq!(rec.band_count, 27);
        assert!(rec.rope_access);
        assert!(!rec.ground_accessible);
        assert_eq!(rec.dir_h, "N");
        assert_eq!(rec.dir_v, "E");
    }

    #[test]
    fn test_active_state_rope_only() {
        let rec = BubbleRecord::parse("RB-002 6 10 1 0 S W UP").unwrap();
        assert_eq!(rec.state, BubbleState::Active);  // rope only → Active
    }

    #[test]
    fn test_verified_state_both_access() {
        let rec = BubbleRecord::parse("RB-003 4 15 1 1 N E UP").unwrap();
        assert_eq!(rec.state, BubbleState::Verified); // rope + ground → Verified
    }

    #[test]
    fn test_idle_state_no_bands() {
        let rec = BubbleRecord::parse("RB-004 4 0 0 0 N E DOWN").unwrap();
        assert_eq!(rec.state, BubbleState::Idle);
    }

    #[test]
    fn test_measurements_rb001() {
        let rec = BubbleRecord::parse("RB-001 4 27 1 0 N E UP").unwrap();
        let m = rec.measure();
        // 4-inch pipe: circumference = π × 4 / 12 = 1.047 ft
        assert!((m.circumference - 1.047).abs() < 0.001);
        // 27 bands = 27 linear feet
        assert_eq!(m.linear_feet, 27.0);
        // square_feet = 27 × 1.047 = 28.27
        assert!((m.square_feet - 28.27).abs() < 0.1);
        // Rope only → ACTIVE
        assert_eq!(m.state, BubbleState::Active);
    }

    #[test]
    fn test_state_bits() {
        assert_eq!(BubbleState::Idle.bits(),     0b000);
        assert_eq!(BubbleState::Active.bits(),   0b101);
        assert_eq!(BubbleState::Verified.bits(), 0b111);
    }

    #[test]
    fn test_state_codes() {
        assert_eq!(BubbleState::Idle.code(),     "000_IDLE");
        assert_eq!(BubbleState::Active.code(),   "101_ACTIVE");
        assert_eq!(BubbleState::Verified.code(), "111_VERIFIED");
    }

    #[test]
    fn test_invalid_pipe_size() {
        assert!(BubbleRecord::parse("RB-005 0 10 1 0 N E UP").is_err());
        assert!(BubbleRecord::parse("RB-006 200 10 1 0 N E UP").is_err());
    }

    #[test]
    fn test_too_few_fields() {
        assert!(BubbleRecord::parse("RB-007 4 10 1").is_err());
    }
}
