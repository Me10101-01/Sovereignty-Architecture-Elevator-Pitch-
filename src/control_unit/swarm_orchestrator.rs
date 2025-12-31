// Swarm Orchestrator Module
// Coordinates Strategickhaos swarm bots for parallel operations
// Implements multi-agent swarm patterns for domain mapping

use std::collections::HashMap;

/// Swarm bot agent
#[derive(Debug, Clone)]
pub struct SwarmBot {
    pub id: String,
    pub role: BotRole,
    pub state: BotState,
    pub fitness: f64,
}

/// Bot role specialization
#[derive(Debug, Clone, PartialEq)]
pub enum BotRole {
    Mapper,      // Domain mapping
    Transformer, // Data transformation
    Validator,   // Result validation
    Mutator,     // Genetic algorithm mutations
    Explorer,    // New domain discovery
}

/// Bot state
#[derive(Debug, Clone, PartialEq)]
pub enum BotState {
    Idle,
    Working,
    Complete,
    Failed,
}

/// Swarm orchestrator coordinates multiple bots
pub struct SwarmOrchestrator {
    bots: Vec<SwarmBot>,
    tasks: Vec<SwarmTask>,
    results: HashMap<String, TaskResult>,
}

/// Task assigned to swarm
#[derive(Debug, Clone)]
pub struct SwarmTask {
    pub id: String,
    pub description: String,
    pub domain: String,
    pub assigned_bots: Vec<String>,
    pub status: TaskStatus,
}

#[derive(Debug, Clone, PartialEq)]
pub enum TaskStatus {
    Pending,
    InProgress,
    Complete,
    Failed,
}

/// Result from task execution
#[derive(Debug, Clone)]
pub struct TaskResult {
    pub task_id: String,
    pub bot_id: String,
    pub output: String,
    pub fitness: f64,
}

impl SwarmOrchestrator {
    /// Create a new swarm orchestrator
    pub fn new() -> Self {
        SwarmOrchestrator {
            bots: Vec::new(),
            tasks: Vec::new(),
            results: HashMap::new(),
        }
    }

    /// Initialize swarm with specified number of bots per role
    pub fn initialize_swarm(&mut self, config: &SwarmConfig) {
        let mut bot_id = 0;

        for _ in 0..config.mappers {
            self.bots.push(SwarmBot {
                id: format!("bot_{}", bot_id),
                role: BotRole::Mapper,
                state: BotState::Idle,
                fitness: 0.5,
            });
            bot_id += 1;
        }

        for _ in 0..config.transformers {
            self.bots.push(SwarmBot {
                id: format!("bot_{}", bot_id),
                role: BotRole::Transformer,
                state: BotState::Idle,
                fitness: 0.5,
            });
            bot_id += 1;
        }

        for _ in 0..config.validators {
            self.bots.push(SwarmBot {
                id: format!("bot_{}", bot_id),
                role: BotRole::Validator,
                state: BotState::Idle,
                fitness: 0.5,
            });
            bot_id += 1;
        }
    }

    /// Add a task to the swarm
    pub fn add_task(&mut self, description: String, domain: String, required_role: BotRole) -> String {
        let task_id = format!("task_{}", self.tasks.len());
        
        // Find available bots with matching role
        let available_bots: Vec<String> = self.bots
            .iter()
            .filter(|b| b.role == required_role && b.state == BotState::Idle)
            .map(|b| b.id.clone())
            .collect();

        let task = SwarmTask {
            id: task_id.clone(),
            description,
            domain,
            assigned_bots: available_bots,
            status: TaskStatus::Pending,
        };

        self.tasks.push(task);
        task_id
    }

    /// Execute pending tasks
    pub fn execute_tasks(&mut self) -> Vec<String> {
        let mut completed_tasks = Vec::new();
        let mut tasks_to_process = Vec::new();

        // Collect tasks that need processing
        for task in self.tasks.iter_mut() {
            if task.status == TaskStatus::Pending && !task.assigned_bots.is_empty() {
                task.status = TaskStatus::InProgress;
                tasks_to_process.push((task.id.clone(), task.assigned_bots.clone(), task.description.clone()));
            }
        }

        // Process collected tasks
        for (task_id, bot_ids, description) in tasks_to_process {
            // Mark bots as working
            for bot_id in &bot_ids {
                if let Some(bot) = self.bots.iter_mut().find(|b| &b.id == bot_id) {
                    bot.state = BotState::Working;
                }
            }

            // Simulate task execution
            for bot_id in &bot_ids {
                let result = TaskResult {
                    task_id: task_id.clone(),
                    bot_id: bot_id.clone(),
                    output: format!("Processed: {}", description),
                    fitness: 0.75, // Simulated fitness score
                };
                
                self.results.insert(
                    format!("{}_{}", task_id, bot_id),
                    result
                );
            }
            
            // Mark task as complete
            if let Some(task) = self.tasks.iter_mut().find(|t| t.id == task_id) {
                task.status = TaskStatus::Complete;
                completed_tasks.push(task.id.clone());
            }

            // Mark bots as idle again
            for bot_id in &bot_ids {
                if let Some(bot) = self.bots.iter_mut().find(|b| &b.id == bot_id) {
                    bot.state = BotState::Idle;
                }
            }
        }

        completed_tasks
    }

    /// Simulate task execution (placeholder for actual logic)
    fn simulate_task_execution(&mut self, task: &SwarmTask) {
        for bot_id in &task.assigned_bots {
            let result = TaskResult {
                task_id: task.id.clone(),
                bot_id: bot_id.clone(),
                output: format!("Processed: {}", task.description),
                fitness: 0.75, // Simulated fitness score
            };
            
            self.results.insert(
                format!("{}_{}", task.id, bot_id),
                result
            );
        }
    }

    /// Get idle bots by role
    pub fn idle_bots(&self, role: Option<BotRole>) -> Vec<&SwarmBot> {
        self.bots
            .iter()
            .filter(|b| {
                b.state == BotState::Idle && 
                role.as_ref().map_or(true, |r| &b.role == r)
            })
            .collect()
    }

    /// Get swarm statistics
    pub fn stats(&self) -> SwarmStats {
        SwarmStats {
            total_bots: self.bots.len(),
            idle_bots: self.bots.iter().filter(|b| b.state == BotState::Idle).count(),
            working_bots: self.bots.iter().filter(|b| b.state == BotState::Working).count(),
            total_tasks: self.tasks.len(),
            completed_tasks: self.tasks.iter().filter(|t| t.status == TaskStatus::Complete).count(),
            average_fitness: self.bots.iter().map(|b| b.fitness).sum::<f64>() / self.bots.len() as f64,
        }
    }
}

/// Swarm configuration
pub struct SwarmConfig {
    pub mappers: usize,
    pub transformers: usize,
    pub validators: usize,
}

impl Default for SwarmConfig {
    fn default() -> Self {
        SwarmConfig {
            mappers: 3,
            transformers: 3,
            validators: 2,
        }
    }
}

/// Swarm statistics
#[derive(Debug)]
pub struct SwarmStats {
    pub total_bots: usize,
    pub idle_bots: usize,
    pub working_bots: usize,
    pub total_tasks: usize,
    pub completed_tasks: usize,
    pub average_fitness: f64,
}

impl Default for SwarmOrchestrator {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_initialize_swarm() {
        let mut orchestrator = SwarmOrchestrator::new();
        let config = SwarmConfig::default();
        
        orchestrator.initialize_swarm(&config);
        
        assert_eq!(orchestrator.bots.len(), 8); // 3 + 3 + 2
    }

    #[test]
    fn test_add_task() {
        let mut orchestrator = SwarmOrchestrator::new();
        orchestrator.initialize_swarm(&SwarmConfig::default());
        
        let task_id = orchestrator.add_task(
            "Map pipe to neural".to_string(),
            "pipe".to_string(),
            BotRole::Mapper
        );
        
        assert_eq!(orchestrator.tasks.len(), 1);
        assert!(task_id.starts_with("task_"));
    }

    #[test]
    fn test_execute_tasks() {
        let mut orchestrator = SwarmOrchestrator::new();
        orchestrator.initialize_swarm(&SwarmConfig::default());
        
        orchestrator.add_task(
            "Transform data".to_string(),
            "neural".to_string(),
            BotRole::Transformer
        );
        
        let completed = orchestrator.execute_tasks();
        
        assert_eq!(completed.len(), 1);
    }

    #[test]
    fn test_idle_bots() {
        let mut orchestrator = SwarmOrchestrator::new();
        orchestrator.initialize_swarm(&SwarmConfig::default());
        
        let idle = orchestrator.idle_bots(None);
        assert_eq!(idle.len(), 8);
        
        let idle_mappers = orchestrator.idle_bots(Some(BotRole::Mapper));
        assert_eq!(idle_mappers.len(), 3);
    }

    #[test]
    fn test_stats() {
        let mut orchestrator = SwarmOrchestrator::new();
        orchestrator.initialize_swarm(&SwarmConfig::default());
        
        let stats = orchestrator.stats();
        
        assert_eq!(stats.total_bots, 8);
        assert_eq!(stats.idle_bots, 8);
        assert_eq!(stats.working_bots, 0);
        assert!((stats.average_fitness - 0.5).abs() < 0.01);
    }
}
