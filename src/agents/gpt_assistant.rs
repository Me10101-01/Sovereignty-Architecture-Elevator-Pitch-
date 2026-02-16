// GPT Assistant Module
// Hooks to GPT for reasoning and code generation per phase
// Interfaces with external LLM APIs for intelligent assistance

/// GPT Assistant for AI-powered reasoning and code generation
pub struct GPTAssistant {
    /// Model configuration
    model: String,
    /// Temperature for generation
    temperature: f64,
    /// Conversation history
    history: Vec<Message>,
    /// Custom instructions
    system_prompt: String,
}

/// Message in conversation
#[derive(Debug, Clone)]
pub struct Message {
    pub role: Role,
    pub content: String,
    pub timestamp: std::time::Instant,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Role {
    System,
    User,
    Assistant,
}

/// Reasoning level (Bloom's taxonomy)
#[derive(Debug, Clone, PartialEq)]
pub enum ReasoningLevel {
    Remember,   // Recall facts
    Understand, // Explain concepts
    Apply,      // Use knowledge in new situations
    Analyze,    // Break down information
    Evaluate,   // Make judgments
    Create,     // Generate new ideas/solutions
}

impl GPTAssistant {
    /// Create a new GPT Assistant
    pub fn new(model: String, system_prompt: String) -> Self {
        GPTAssistant {
            model,
            temperature: 0.7,
            history: Vec::new(),
            system_prompt,
        }
    }

    /// Set temperature for generation
    pub fn set_temperature(&mut self, temperature: f64) {
        self.temperature = temperature.clamp(0.0, 2.0);
    }

    /// Add a message to history
    pub fn add_message(&mut self, role: Role, content: String) {
        self.history.push(Message {
            role,
            content,
            timestamp: std::time::Instant::now(),
        });
    }

    /// Generate a response (simulated - in production, call actual GPT API)
    pub fn generate(&mut self, prompt: String) -> Result<String, String> {
        self.add_message(Role::User, prompt.clone());

        // Simulate GPT response
        let response = format!("GPT response to: {}", prompt);

        self.add_message(Role::Assistant, response.clone());

        Ok(response)
    }

    /// Reason at a specific Bloom's level
    pub fn reason(&mut self, prompt: String, level: ReasoningLevel) -> Result<String, String> {
        let level_instruction = match level {
            ReasoningLevel::Remember => "Recall and list the key facts:",
            ReasoningLevel::Understand => "Explain the concept in detail:",
            ReasoningLevel::Apply => "Apply this knowledge to solve:",
            ReasoningLevel::Analyze => "Analyze the components and relationships:",
            ReasoningLevel::Evaluate => "Evaluate and make a judgment on:",
            ReasoningLevel::Create => "Create a novel solution for:",
        };

        let enhanced_prompt = format!("{} {}", level_instruction, prompt);
        self.generate(enhanced_prompt)
    }

    /// Generate code based on specification
    pub fn generate_code(&mut self, spec: String, language: &str) -> Result<String, String> {
        let prompt = format!(
            "Generate {} code for the following specification: {}",
            language,
            spec
        );

        self.generate(prompt)
    }

    /// Generate UDAP parser code
    pub fn generate_udap_parser(&mut self, domain: &str) -> Result<String, String> {
        let spec = format!(
            "Create a UDAP parser for the {} domain that can parse addresses like skhaos://{}/...",
            domain,
            domain
        );

        self.generate_code(spec, "Rust")
    }

    /// Synthesize visual map code
    pub fn generate_visual_map(&mut self, domains: Vec<String>) -> Result<String, String> {
        let spec = format!(
            "Generate visualization code for mapping between these domains: {}",
            domains.join(", ")
        );

        self.generate_code(spec, "Rust")
    }

    /// Get conversation history
    pub fn history(&self) -> &[Message] {
        &self.history
    }

    /// Clear conversation history
    pub fn clear_history(&mut self) {
        self.history.clear();
    }

    /// Export history to UDAP addresses
    pub fn export_to_udap(&self) -> Vec<String> {
        self.history
            .iter()
            .enumerate()
            .map(|(i, msg)| {
                format!(
                    "skhaos://agent/gpt/message/{}?role={:?}&length={}",
                    i,
                    msg.role,
                    msg.content.len()
                )
            })
            .collect()
    }
}

impl Default for GPTAssistant {
    fn default() -> Self {
        Self::new(
            "gpt-4".to_string(),
            "You are a helpful AI assistant for the SkhaOS quantum-symbolic emulator.".to_string()
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_assistant() {
        let assistant = GPTAssistant::new(
            "gpt-4".to_string(),
            "Test prompt".to_string()
        );

        assert_eq!(assistant.model, "gpt-4");
        assert_eq!(assistant.history.len(), 0);
    }

    #[test]
    fn test_add_message() {
        let mut assistant = GPTAssistant::default();
        
        assistant.add_message(Role::User, "Hello".to_string());
        assert_eq!(assistant.history.len(), 1);
        assert_eq!(assistant.history[0].role, Role::User);
    }

    #[test]
    fn test_generate() {
        let mut assistant = GPTAssistant::default();
        
        let response = assistant.generate("Test prompt".to_string()).unwrap();
        
        assert!(response.contains("Test prompt"));
        assert_eq!(assistant.history.len(), 2); // User + Assistant
    }

    #[test]
    fn test_reason_at_level() {
        let mut assistant = GPTAssistant::default();
        
        let response = assistant.reason(
            "UDAP addressing".to_string(),
            ReasoningLevel::Create
        ).unwrap();
        
        assert!(!response.is_empty());
    }

    #[test]
    fn test_generate_code() {
        let mut assistant = GPTAssistant::default();
        
        let code = assistant.generate_code(
            "A function to parse UDAP addresses".to_string(),
            "Rust"
        ).unwrap();
        
        assert!(code.contains("Rust"));
    }

    #[test]
    fn test_generate_udap_parser() {
        let mut assistant = GPTAssistant::default();
        
        let parser = assistant.generate_udap_parser("pipe").unwrap();
        
        assert!(parser.contains("pipe"));
    }

    #[test]
    fn test_export_to_udap() {
        let mut assistant = GPTAssistant::default();
        
        assistant.add_message(Role::User, "Test".to_string());
        assistant.add_message(Role::Assistant, "Response".to_string());
        
        let udap_addresses = assistant.export_to_udap();
        
        assert_eq!(udap_addresses.len(), 2);
        assert!(udap_addresses[0].contains("skhaos://agent/gpt/message/"));
    }

    #[test]
    fn test_clear_history() {
        let mut assistant = GPTAssistant::default();
        
        assistant.add_message(Role::User, "Test".to_string());
        assistant.clear_history();
        
        assert_eq!(assistant.history.len(), 0);
    }

    #[test]
    fn test_temperature() {
        let mut assistant = GPTAssistant::default();
        
        assistant.set_temperature(1.5);
        assert_eq!(assistant.temperature, 1.5);
        
        assistant.set_temperature(3.0); // Should clamp to 2.0
        assert_eq!(assistant.temperature, 2.0);
    }
}
