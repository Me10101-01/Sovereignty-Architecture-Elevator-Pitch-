// Pipe Transform Module
// Implements pipefitting degree transformations mapped to code namespaces
// UDAP: skhaos://pipe/run/offset/travel?angle=45&offset=10

use std::f64::consts::PI;

/// Represents a pipefitting coordinate system
/// Maps to: Run/Offset/Travel → Module/Function/Depth
#[derive(Debug, Clone)]
pub struct PipeCoordinate {
    pub run: f64,
    pub offset: f64,
    pub travel: f64,
    pub angle: f64,
}

impl PipeCoordinate {
    /// Create a new pipe coordinate from run and angle
    pub fn from_run_angle(run: f64, angle: f64) -> Self {
        let radians = angle * PI / 180.0;
        let offset = run * radians.tan();
        let travel = run / radians.cos();
        
        PipeCoordinate {
            run,
            offset,
            travel,
            angle,
        }
    }

    /// Create from offset and angle
    pub fn from_offset_angle(offset: f64, angle: f64) -> Self {
        let radians = angle * PI / 180.0;
        let run = offset / radians.tan();
        let travel = offset / radians.sin();
        
        PipeCoordinate {
            run,
            offset,
            travel,
            angle,
        }
    }

    /// Convert to code namespace coordinates
    /// Run → Module depth
    /// Offset → Function index
    /// Travel → Execution depth
    pub fn to_code_namespace(&self) -> CodeNamespace {
        CodeNamespace {
            module_depth: self.run.floor() as usize,
            function_index: self.offset.floor() as usize,
            execution_depth: self.travel.floor() as usize,
            angle_metadata: self.angle,
        }
    }

    /// Apply a transform matrix (rotation/scaling)
    pub fn transform(&self, scale: f64, rotation: f64) -> Self {
        let rot_rad = rotation * PI / 180.0;
        let cos_r = rot_rad.cos();
        let sin_r = rot_rad.sin();
        
        let new_run = scale * (self.run * cos_r - self.offset * sin_r);
        let new_offset = scale * (self.run * sin_r + self.offset * cos_r);
        
        PipeCoordinate::from_run_angle(
            new_run,
            new_offset.atan2(new_run) * 180.0 / PI
        )
    }
}

/// Code namespace mapping from pipe coordinates
#[derive(Debug, Clone)]
pub struct CodeNamespace {
    pub module_depth: usize,
    pub function_index: usize,
    pub execution_depth: usize,
    pub angle_metadata: f64,
}

impl CodeNamespace {
    /// Generate a UDAP address for this namespace
    pub fn to_udap(&self) -> String {
        format!(
            "skhaos://pipe/run/{}/offset/{}/travel/{}?angle={}",
            self.module_depth,
            self.function_index,
            self.execution_depth,
            self.angle_metadata
        )
    }

    /// Parse from UDAP address
    pub fn from_udap(uri: &str) -> Result<Self, String> {
        // Simple parser for demonstration
        // Format: skhaos://pipe/run/{run}/offset/{offset}/travel/{travel}?angle={angle}
        
        if !uri.starts_with("skhaos://pipe/") {
            return Err("Invalid UDAP prefix".to_string());
        }
        
        // Extract path and query
        let parts: Vec<&str> = uri.split('?').collect();
        if parts.len() != 2 {
            return Err("Missing query parameters".to_string());
        }
        
        let path = parts[0];
        let query = parts[1];
        
        // Extract numeric values from path
        let path_parts: Vec<&str> = path.split('/').collect();
        if path_parts.len() < 8 {
            return Err("Invalid path format".to_string());
        }
        
        let module_depth = path_parts[4].parse::<usize>()
            .map_err(|_| "Invalid run value")?;
        let function_index = path_parts[6].parse::<usize>()
            .map_err(|_| "Invalid offset value")?;
        let execution_depth = path_parts[8].parse::<usize>()
            .map_err(|_| "Invalid travel value")?;
        
        // Extract angle from query
        let angle_str = query.strip_prefix("angle=")
            .ok_or("Missing angle parameter")?;
        let angle_metadata = angle_str.parse::<f64>()
            .map_err(|_| "Invalid angle value")?;
        
        Ok(CodeNamespace {
            module_depth,
            function_index,
            execution_depth,
            angle_metadata,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pipe_coordinate_from_run_angle() {
        let coord = PipeCoordinate::from_run_angle(10.0, 45.0);
        assert!((coord.offset - 10.0).abs() < 0.1);
        assert!((coord.travel - 14.14).abs() < 0.1);
    }

    #[test]
    fn test_to_code_namespace() {
        let coord = PipeCoordinate {
            run: 5.7,
            offset: 3.2,
            travel: 8.9,
            angle: 30.0,
        };
        
        let ns = coord.to_code_namespace();
        assert_eq!(ns.module_depth, 5);
        assert_eq!(ns.function_index, 3);
        assert_eq!(ns.execution_depth, 8);
    }

    #[test]
    fn test_udap_roundtrip() {
        let ns = CodeNamespace {
            module_depth: 5,
            function_index: 3,
            execution_depth: 8,
            angle_metadata: 45.5,
        };
        
        let udap = ns.to_udap();
        let parsed = CodeNamespace::from_udap(&udap).unwrap();
        
        assert_eq!(parsed.module_depth, ns.module_depth);
        assert_eq!(parsed.function_index, ns.function_index);
        assert_eq!(parsed.execution_depth, ns.execution_depth);
        assert!((parsed.angle_metadata - ns.angle_metadata).abs() < 0.01);
    }

    #[test]
    fn test_transform() {
        let coord = PipeCoordinate::from_run_angle(10.0, 45.0);
        let transformed = coord.transform(2.0, 90.0);
        
        // After 90° rotation and 2x scale, coordinates should be transformed
        assert!(transformed.run.abs() > 0.0);
        assert!(transformed.offset.abs() > 0.0);
    }
}
