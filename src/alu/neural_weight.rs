// Neural Weight Module
// Maps neural network layer/neuron/weight structures to UDAP addressing
// UDAP: skhaos://neural/layer/{layer}/neuron/{neuron}/weight?value=0.5

/// Represents a neural network coordinate in UDAP space
#[derive(Debug, Clone)]
pub struct NeuralCoordinate {
    pub layer: usize,
    pub neuron: usize,
    pub weight_index: usize,
    pub value: f64,
}

impl NeuralCoordinate {
    /// Create a new neural coordinate
    pub fn new(layer: usize, neuron: usize, weight_index: usize, value: f64) -> Self {
        NeuralCoordinate {
            layer,
            neuron,
            weight_index,
            value,
        }
    }

    /// Convert to UDAP address
    pub fn to_udap(&self) -> String {
        format!(
            "skhaos://neural/layer/{}/neuron/{}/weight/{}?value={}",
            self.layer,
            self.neuron,
            self.weight_index,
            self.value
        )
    }

    /// Parse from UDAP address
    pub fn from_udap(uri: &str) -> Result<Self, String> {
        if !uri.starts_with("skhaos://neural/") {
            return Err("Invalid UDAP prefix for neural coordinate".to_string());
        }

        let parts: Vec<&str> = uri.split('?').collect();
        if parts.len() != 2 {
            return Err("Missing query parameters".to_string());
        }

        let path = parts[0];
        let query = parts[1];

        // Extract path components
        let path_parts: Vec<&str> = path.split('/').collect();
        if path_parts.len() < 8 {
            return Err("Invalid path format".to_string());
        }

        let layer = path_parts[4].parse::<usize>()
            .map_err(|_| "Invalid layer value")?;
        let neuron = path_parts[6].parse::<usize>()
            .map_err(|_| "Invalid neuron value")?;
        let weight_index = path_parts[8].parse::<usize>()
            .map_err(|_| "Invalid weight index")?;

        // Extract value from query
        let value_str = query.strip_prefix("value=")
            .ok_or("Missing value parameter")?;
        let value = value_str.parse::<f64>()
            .map_err(|_| "Invalid value")?;

        Ok(NeuralCoordinate {
            layer,
            neuron,
            weight_index,
            value,
        })
    }

    /// Apply activation function (sigmoid example)
    pub fn sigmoid(&self) -> f64 {
        1.0 / (1.0 + (-self.value).exp())
    }

    /// Apply ReLU activation
    pub fn relu(&self) -> f64 {
        self.value.max(0.0)
    }

    /// Apply tanh activation
    pub fn tanh(&self) -> f64 {
        self.value.tanh()
    }

    /// Calculate weight gradient (simplified)
    pub fn gradient(&self, learning_rate: f64, error: f64) -> f64 {
        self.value - learning_rate * error
    }
}

/// Neural layer representation
#[derive(Debug, Clone)]
pub struct NeuralLayer {
    pub index: usize,
    pub neurons: Vec<Neuron>,
}

impl NeuralLayer {
    pub fn new(index: usize, neuron_count: usize) -> Self {
        let neurons = (0..neuron_count)
            .map(|i| Neuron::new(i))
            .collect();

        NeuralLayer {
            index,
            neurons,
        }
    }

    /// Get all weights as UDAP addresses
    pub fn to_udap_map(&self) -> Vec<String> {
        let mut addresses = Vec::new();
        for neuron in &self.neurons {
            for (weight_idx, weight) in neuron.weights.iter().enumerate() {
                let coord = NeuralCoordinate::new(
                    self.index,
                    neuron.index,
                    weight_idx,
                    *weight
                );
                addresses.push(coord.to_udap());
            }
        }
        addresses
    }
}

/// Individual neuron
#[derive(Debug, Clone)]
pub struct Neuron {
    pub index: usize,
    pub weights: Vec<f64>,
    pub bias: f64,
}

impl Neuron {
    pub fn new(index: usize) -> Self {
        Neuron {
            index,
            weights: Vec::new(),
            bias: 0.0,
        }
    }

    pub fn with_weights(index: usize, weights: Vec<f64>, bias: f64) -> Self {
        Neuron {
            index,
            weights,
            bias,
        }
    }

    /// Forward pass calculation
    pub fn forward(&self, inputs: &[f64]) -> f64 {
        let sum: f64 = self.weights.iter()
            .zip(inputs.iter())
            .map(|(w, i)| w * i)
            .sum();
        sum + self.bias
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_neural_coordinate_udap() {
        let coord = NeuralCoordinate::new(2, 5, 3, 0.75);
        let udap = coord.to_udap();
        
        assert!(udap.contains("layer/2"));
        assert!(udap.contains("neuron/5"));
        assert!(udap.contains("weight/3"));
        assert!(udap.contains("value=0.75"));
    }

    #[test]
    fn test_udap_roundtrip() {
        let coord = NeuralCoordinate::new(1, 2, 3, 0.5);
        let udap = coord.to_udap();
        let parsed = NeuralCoordinate::from_udap(&udap).unwrap();
        
        assert_eq!(parsed.layer, coord.layer);
        assert_eq!(parsed.neuron, coord.neuron);
        assert_eq!(parsed.weight_index, coord.weight_index);
        assert!((parsed.value - coord.value).abs() < 0.001);
    }

    #[test]
    fn test_activation_functions() {
        let coord = NeuralCoordinate::new(0, 0, 0, 0.5);
        
        let sig = coord.sigmoid();
        assert!(sig > 0.5 && sig < 1.0);
        
        let relu = coord.relu();
        assert_eq!(relu, 0.5);
        
        let coord_neg = NeuralCoordinate::new(0, 0, 0, -0.5);
        assert_eq!(coord_neg.relu(), 0.0);
    }

    #[test]
    fn test_neural_layer() {
        let layer = NeuralLayer::new(1, 3);
        assert_eq!(layer.neurons.len(), 3);
        assert_eq!(layer.index, 1);
    }

    #[test]
    fn test_neuron_forward() {
        let neuron = Neuron::with_weights(0, vec![0.5, 0.3, 0.2], 0.1);
        let inputs = vec![1.0, 2.0, 3.0];
        let output = neuron.forward(&inputs);
        
        // 0.5*1.0 + 0.3*2.0 + 0.2*3.0 + 0.1 = 0.5 + 0.6 + 0.6 + 0.1 = 1.8
        assert!((output - 1.8).abs() < 0.001);
    }
}
