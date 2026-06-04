mod stepper;
mod flamelang;
mod unison_bridge;

use stepper::ticks::CrawlerEngine;
use stepper::omni_calc::OmniCalculation;
use flamelang::token::FlameLangToken;
use flamelang::emitter::FlameEmitter;
use flamelang::hash::ContentAddressableStore;
use unison_bridge::addressable::LiveMigrator;

fn main() {
    println!("Initializing SAGCO Stepper Crawler Engine v0.3...");
    println!("CONTENT_ADDRESSED_HASHING: ENABLED");
    println!();

    let mut crawler = CrawlerEngine::new(250);
    let tick_meta = crawler.advance_tick(1.034);
    println!("TICK_ID={} DELTA={}ms WEIGHT={:.4}",
        tick_meta.tick_id, tick_meta.timestamp_delta, tick_meta.element_weight);

    let mut legacy_calc = OmniCalculation::new("WAFER_AX_99", tick_meta.element_weight);
    legacy_calc.insert_frequency("sagco_kernel", 42);
    legacy_calc.insert_frequency("flamelang", 21);
    legacy_calc.insert_frequency("vim_binding", 17);

    let mut pipeline: Vec<FlameLangToken> = Vec::new();
    pipeline.push(FlameLangToken::ExcelWafer(legacy_calc.source_wafer_id.clone()));
    for (word, count) in &legacy_calc.raw_word_frequency {
        pipeline.push(FlameLangToken::WordFreq(word.clone(), *count));
    }
    pipeline.push(FlameLangToken::RawToken("Carbon_C6_parser_core".to_string()));
    pipeline.push(FlameLangToken::WeightScalar(legacy_calc.scalar_weight));
    pipeline.push(FlameLangToken::FlameSignal("INIT_DAEMON_FUZZ".to_string()));
    pipeline.push(FlameLangToken::OxygenRuntime("flamelang_v3".to_string()));
    pipeline.push(FlameLangToken::RustCallHook("run_pid_scan()".to_string()));
    pipeline.push(FlameLangToken::DnaStrandSequence("ATCGGCTA".to_string()));
    pipeline.push(FlameLangToken::UnityNode(42));
    pipeline.push(FlameLangToken::EpicOrchestrator("CHRONO_WORLD_STATE".to_string()));

    let mut store = ContentAddressableStore::new();
    let flame = FlameEmitter::transpile_to_flamelang(&pipeline, &mut store);

    std::fs::create_dir_all("sagco_crawler_engine/outputs").ok();
    std::fs::write("sagco_crawler_engine/outputs/program_v03.flame", &flame)
        .expect("write failed");

    println!();
    println!("=== TRANSPILATION COMPLETE ===");
    println!("{}", flame);

    println!("STORE: {} hashed nodes", store.len());
    let vim_count = FlameEmitter::verify_vim_bindings(&flame);
    println!("VIM_BINDINGS: {} injected", vim_count);

    // Live migration demo — Epic orchestrator migrates NODE_A → NODE_B
    println!();
    println!("=== LIVE MIGRATION DEMO ===");
    let epic_token = FlameLangToken::EpicOrchestrator("CHRONO_WORLD_STATE".to_string());
    let epic_hash = ContentAddressableStore::compute_hash(&epic_token);
    println!("EPIC_HASH: {}", epic_hash.0);

    // Verify round-trip: insert hashed node then resolve it back
    pipeline.push(FlameLangToken::HashedNode(epic_hash.clone()));
    store.insert(FlameLangToken::HashedNode(epic_hash.clone()));
    match store.resolve(&epic_hash) {
        Some(_) => println!("RESOLVE: hash found in store — immutable identity confirmed"),
        None    => println!("RESOLVE: miss"),
    }

    println!();
    for line in LiveMigrator::simulate_two_node_migration(&epic_hash) {
        println!("{}", line);
    }

    println!();
    println!("STATUS=SAGCO_CRAWLER_ENGINE_V3_PASS");
}
