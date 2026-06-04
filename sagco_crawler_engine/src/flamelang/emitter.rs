use crate::flamelang::token::FlameLangToken;
use crate::flamelang::hash::ContentAddressableStore;

pub struct FlameEmitter;

impl FlameEmitter {
    pub fn transpile_to_flamelang(
        tokens: &[FlameLangToken],
        store: &mut ContentAddressableStore,
    ) -> String {
        let mut script = String::new();
        script.push_str("# --- FLAME_LANG COMPILED OUTPUT v0.3 ---\n");
        script.push_str("# CONTENT_ADDRESSED_HASHING_ENABLED\n");
        script.push_str("# SAGCO_KERNEL_VIM_BINDING_ENABLED\n\n");

        for token in tokens {
            let hash = store.insert(token.clone());
            let h = &hash.0[..12]; // short prefix for readability

            match token {
                FlameLangToken::ExcelWafer(id) =>
                    script.push_str(&format!("INJECT_SUBSTRATE Silicon_Si14_Wafer[\"{}\" @{}]\n", id, h)),
                FlameLangToken::WordFreq(word, freq) =>
                    script.push_str(&format!("STREAM_FREQ Helium_He2_Metric[\"{}\" -> {} @{}]\n", word, freq, h)),
                FlameLangToken::RawToken(tok) =>
                    script.push_str(&format!("PARSE_ATOM Carbon_C6_Token[\"{}\" @{}]\n", tok, h)),
                FlameLangToken::WeightScalar(w) =>
                    script.push_str(&format!("APPLY_GRAVITY Lead_Pb82_Weight[{:.4} @{}]\n", w, h)),
                FlameLangToken::FlameSignal(sig) =>
                    script.push_str(&format!("IGNITE_HASHED Phosphorus_P15[{} -> \"{}\"]\n", h, sig)),
                FlameLangToken::OxygenRuntime(ctx) =>
                    script.push_str(&format!("BREATHE Oxygen_O8_FlameLang[\"{}\" @{}]\n", ctx, h)),
                FlameLangToken::RustCallHook(func) =>
                    script.push_str(&format!("NATIVE_CALL Iron_Fe26_Rust[\"{}\" @{}]\n", func, h)),
                FlameLangToken::DnaStrandSequence(dna) =>
                    script.push_str(&format!("GENCODE_BUILD Nitrogen_N7_DNA[\"{}\" @{}]\n", dna, h)),
                FlameLangToken::UnityNode(level) =>
                    script.push_str(&format!("BIND_UNITY Hydrogen_H1_Node[coherence_level={} @{}]\n", level, h)),
                FlameLangToken::EpicOrchestrator(state) =>
                    script.push_str(&format!("ORCHESTRATE_MIGRATE Au79_Epic[{} -> \"{}\"]\n", h, state)),
                FlameLangToken::HashedNode(fh) =>
                    script.push_str(&format!("RESOLVE_NODE {}\n", fh.0)),
            }
        }

        // === Vim Kernel Keybinding Layer ===
        script.push_str("\n# --- VIM_KERNEL_INTEGRATION ---\n");
        script.push_str("VIM_BIND flame :FlameIgnite\n");
        script.push_str("VIM_BIND tick :AdvanceStepperTick\n");
        script.push_str("VIM_BIND wafer :InjectSi14Wafer\n");
        script.push_str("VIM_BIND dnas :GencodeN7DNA\n");
        script.push_str("VIM_BIND epic :OrchestrateAu79\n");
        script.push_str("VIM_SET localleader=\\\\\n");
        script.push_str("VIM_AUTOCMD BufWritePost *.sagco :TranspileFlameLang\n");

        // === Live Migration Layer ===
        script.push_str("\n# --- LIVE_MIGRATION_LAYER ---\n");
        script.push_str("ENABLE_HASH_MIGRATION true\n");
        script.push_str("EMIT_STATE_GREEN\n");
        script.push_str("# Pipeline integrity: Unity H1 + Epic Au79 verified\n");
        script
    }

    pub fn verify_vim_bindings(script: &str) -> usize {
        script.lines().filter(|l| l.starts_with("VIM_BIND")).count()
    }
}
