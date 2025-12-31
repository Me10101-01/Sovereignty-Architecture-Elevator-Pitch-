// Swarm Bots Module
// Strategickhaos swarms: Multi-agent swarms for parallel domain mapping
// Evolves via genetic algorithms in sandbox

/// Swarm bot for autonomous operations
#[derive(Debug, Clone)]
pub struct SwarmBot {
    pub id: String,
    pub generation: u32,
    pub genome: Genome,
    pub fitness: f64,
    pub state: BotState,
}

/// Bot genome (genetic encoding of behavior)
#[derive(Debug, Clone)]
pub struct Genome {
    /// Genes controlling bot behavior
    pub genes: Vec<Gene>,
}

/// Individual gene
#[derive(Debug, Clone)]
pub struct Gene {
    pub name: String,
    pub value: f64,
}

#[derive(Debug, Clone, PartialEq)]
pub enum BotState {
    Idle,
    Exploring,
    Mapping,
    Mutating,
    Complete,
}

impl SwarmBot {
    /// Create a new swarm bot with random genome
    pub fn new(id: String, generation: u32) -> Self {
        let genome = Genome::random();
        
        SwarmBot {
            id,
            generation,
            genome,
            fitness: 0.0,
            state: BotState::Idle,
        }
    }

    /// Create bot from parent genomes (crossover)
    pub fn from_parents(id: String, parent1: &SwarmBot, parent2: &SwarmBot) -> Self {
        let genome = Genome::crossover(&parent1.genome, &parent2.genome);
        
        SwarmBot {
            id,
            generation: parent1.generation + 1,
            genome,
            fitness: 0.0,
            state: BotState::Idle,
        }
    }

    /// Mutate the bot's genome
    pub fn mutate(&mut self, mutation_rate: f64) {
        self.genome.mutate(mutation_rate);
    }

    /// Evaluate fitness for a task
    pub fn evaluate_fitness(&mut self, task_result: f64) {
        self.fitness = task_result;
    }

    /// Execute a domain mapping task
    pub fn execute_mapping(&mut self, from_domain: &str, to_domain: &str) -> String {
        self.state = BotState::Mapping;
        
        // Simulate mapping based on genome
        let result = format!(
            "Mapped {} to {} with fitness {}",
            from_domain,
            to_domain,
            self.fitness
        );
        
        self.state = BotState::Complete;
        result
    }

    /// Convert to UDAP address
    pub fn to_udap(&self) -> String {
        format!(
            "skhaos://agent/swarm_bot/{}?gen={}&fitness={}&state={:?}",
            self.id,
            self.generation,
            self.fitness,
            self.state
        )
    }
}

impl Genome {
    /// Create a random genome
    pub fn random() -> Self {
        let genes = vec![
            Gene { name: "exploration".to_string(), value: rand_f64() },
            Gene { name: "mapping_accuracy".to_string(), value: rand_f64() },
            Gene { name: "mutation_tolerance".to_string(), value: rand_f64() },
            Gene { name: "cooperation".to_string(), value: rand_f64() },
        ];

        Genome { genes }
    }

    /// Crossover between two genomes
    pub fn crossover(parent1: &Genome, parent2: &Genome) -> Self {
        let mut genes = Vec::new();
        
        for i in 0..parent1.genes.len().min(parent2.genes.len()) {
            // Randomly choose gene from either parent
            let gene = if rand_bool() {
                parent1.genes[i].clone()
            } else {
                parent2.genes[i].clone()
            };
            genes.push(gene);
        }

        Genome { genes }
    }

    /// Mutate genome
    pub fn mutate(&mut self, mutation_rate: f64) {
        for gene in &mut self.genes {
            if rand_f64() < mutation_rate {
                gene.value = (gene.value + (rand_f64() - 0.5) * 0.2).clamp(0.0, 1.0);
            }
        }
    }

    /// Get gene value by name
    pub fn get_gene(&self, name: &str) -> Option<f64> {
        self.genes.iter()
            .find(|g| g.name == name)
            .map(|g| g.value)
    }
}

/// Swarm population manager
pub struct SwarmPopulation {
    bots: Vec<SwarmBot>,
    generation: u32,
    population_size: usize,
}

impl SwarmPopulation {
    /// Create a new population
    pub fn new(population_size: usize) -> Self {
        let mut bots = Vec::new();
        
        for i in 0..population_size {
            bots.push(SwarmBot::new(format!("bot_{}", i), 0));
        }

        SwarmPopulation {
            bots,
            generation: 0,
            population_size,
        }
    }

    /// Evolve population for one generation
    pub fn evolve(&mut self, mutation_rate: f64) {
        // Sort by fitness (descending)
        self.bots.sort_by(|a, b| b.fitness.partial_cmp(&a.fitness).unwrap());

        // Keep top 50% as parents
        let parent_count = self.population_size / 2;
        let parents: Vec<SwarmBot> = self.bots.iter().take(parent_count).cloned().collect();

        // Generate new population
        let mut new_bots = Vec::new();

        // Keep elite (top 10%)
        let elite_count = self.population_size / 10;
        for bot in self.bots.iter().take(elite_count) {
            new_bots.push(bot.clone());
        }

        // Create offspring from parents
        while new_bots.len() < self.population_size {
            let parent1 = &parents[rand_usize(parent_count)];
            let parent2 = &parents[rand_usize(parent_count)];
            
            let mut offspring = SwarmBot::from_parents(
                format!("bot_gen{}_{}", self.generation + 1, new_bots.len()),
                parent1,
                parent2
            );

            offspring.mutate(mutation_rate);
            new_bots.push(offspring);
        }

        self.bots = new_bots;
        self.generation += 1;
    }

    /// Get all bots
    pub fn bots(&self) -> &[SwarmBot] {
        &self.bots
    }

    /// Get best bot
    pub fn best_bot(&self) -> Option<&SwarmBot> {
        self.bots.iter().max_by(|a, b| a.fitness.partial_cmp(&b.fitness).unwrap())
    }

    /// Get average fitness
    pub fn average_fitness(&self) -> f64 {
        if self.bots.is_empty() {
            return 0.0;
        }

        let sum: f64 = self.bots.iter().map(|b| b.fitness).sum();
        sum / self.bots.len() as f64
    }

    /// Current generation
    pub fn generation(&self) -> u32 {
        self.generation
    }
}

// Simple random number generators (in production, use proper RNG)
fn rand_f64() -> f64 {
    0.5 // Placeholder
}

fn rand_bool() -> bool {
    true // Placeholder
}

fn rand_usize(max: usize) -> usize {
    if max == 0 { 0 } else { max / 2 } // Placeholder
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_swarm_bot() {
        let bot = SwarmBot::new("bot_0".to_string(), 0);
        
        assert_eq!(bot.id, "bot_0");
        assert_eq!(bot.generation, 0);
        assert_eq!(bot.fitness, 0.0);
        assert_eq!(bot.state, BotState::Idle);
    }

    #[test]
    fn test_bot_from_parents() {
        let parent1 = SwarmBot::new("parent1".to_string(), 0);
        let parent2 = SwarmBot::new("parent2".to_string(), 0);
        
        let offspring = SwarmBot::from_parents("child".to_string(), &parent1, &parent2);
        
        assert_eq!(offspring.generation, 1);
    }

    #[test]
    fn test_mutate() {
        let mut bot = SwarmBot::new("bot".to_string(), 0);
        let original_genes = bot.genome.genes.clone();
        
        bot.mutate(1.0); // 100% mutation rate
        
        // Genes might have changed (depending on random)
        assert_eq!(bot.genome.genes.len(), original_genes.len());
    }

    #[test]
    fn test_evaluate_fitness() {
        let mut bot = SwarmBot::new("bot".to_string(), 0);
        
        bot.evaluate_fitness(0.85);
        assert_eq!(bot.fitness, 0.85);
    }

    #[test]
    fn test_execute_mapping() {
        let mut bot = SwarmBot::new("bot".to_string(), 0);
        
        let result = bot.execute_mapping("pipe", "neural");
        
        assert!(result.contains("pipe"));
        assert!(result.contains("neural"));
        assert_eq!(bot.state, BotState::Complete);
    }

    #[test]
    fn test_bot_to_udap() {
        let bot = SwarmBot::new("bot_0".to_string(), 5);
        let udap = bot.to_udap();
        
        assert!(udap.contains("skhaos://agent/swarm_bot/bot_0"));
        assert!(udap.contains("gen=5"));
    }

    #[test]
    fn test_genome_random() {
        let genome = Genome::random();
        assert!(!genome.genes.is_empty());
    }

    #[test]
    fn test_genome_crossover() {
        let parent1 = SwarmBot::new("p1".to_string(), 0);
        let parent2 = SwarmBot::new("p2".to_string(), 0);
        
        let child_genome = Genome::crossover(&parent1.genome, &parent2.genome);
        
        assert_eq!(child_genome.genes.len(), parent1.genome.genes.len());
    }

    #[test]
    fn test_swarm_population() {
        let population = SwarmPopulation::new(10);
        
        assert_eq!(population.bots().len(), 10);
        assert_eq!(population.generation(), 0);
    }

    #[test]
    fn test_population_evolve() {
        let mut population = SwarmPopulation::new(10);
        
        // Set some fitness values
        for bot in &mut population.bots {
            bot.fitness = 0.5;
        }
        
        population.evolve(0.1);
        
        assert_eq!(population.generation(), 1);
        assert_eq!(population.bots().len(), 10);
    }

    #[test]
    fn test_best_bot() {
        let mut population = SwarmPopulation::new(5);
        
        population.bots[0].fitness = 0.9;
        population.bots[1].fitness = 0.5;
        population.bots[2].fitness = 0.7;
        
        let best = population.best_bot().unwrap();
        assert_eq!(best.fitness, 0.9);
    }

    #[test]
    fn test_average_fitness() {
        let mut population = SwarmPopulation::new(3);
        
        population.bots[0].fitness = 0.6;
        population.bots[1].fitness = 0.8;
        population.bots[2].fitness = 1.0;
        
        let avg = population.average_fitness();
        assert!((avg - 0.8).abs() < 0.01);
    }
}
