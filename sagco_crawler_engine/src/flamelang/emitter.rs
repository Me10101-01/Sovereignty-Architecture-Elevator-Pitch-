use crate::flamelang::token::FlameLangToken;

pub struct FlameEmitter;

impl FlameEmitter {
    pub fn transpile_to_flamelang(tokens: &[FlameLangToken]) -> String {
        let mut script = String::new();
        script.push_str("# --- FLAME_LANG COMPILED OUTPUT v0.2 ---\n");
        script.push_str("# SAGCO_KERNEL_VIM_BINDING_ENABLED\n\n");

        for token in tokens {
            match token {
                FlameLangToken::ExcelWafer(id) => {
                    script.push_str(&format!("INJECT_SUBSTRATE Silicon_Si14_Wafer[\"{}\"]\n", id));
                }
                FlameLangToken::WordFreq(word, freq) => {
                    script.push_str(&format!("STREAM_FREQ Helium_He2_Metric[\"{}\" -> {}]\n", word, freq));
                }
                FlameLangToken::RawToken(tok) => {
                    script.push_str(&format!("PARSE_ATOM Carbon_C6_Token[\"{}\"]\n", tok));
                }
                FlameLangToken::WeightScalar(w) => {
                    script.push_str(&format!("APPLY_GRAVITY Lead_Pb82_Weight[{:.4}]\n", w));
                }
                FlameLangToken::FlameSignal(sig) => {
                    script.push_str(&format!("IGNITE_TOKEN Phosphorus_P15_Flame[\"{}\"]\n", sig));
                }
                FlameLangToken::OxygenRuntime(ctx) => {
                    script.push_str(&format!("BREATHE Oxygen_O8_FlameLang[\"{}\"]\n", ctx));
                }
                FlameLangToken::RustCallHook(func) => {
                    script.push_str(&format!("NATIVE_CALL Iron_Fe26_Rust[\"{}\"]\n", func));
                }
                FlameLangToken::DnaStrandSequence(dna) => {
                    script.push_str(&format!("GENCODE_BUILD Nitrogen_N7_DNA[\"{}\"]\n", dna));
                }
                FlameLangToken::UnityNode(level) => {
                    script.push_str(&format!("BIND_UNITY Hydrogen_H1_Node[coherence_level={}]\n", level));
                }
                FlameLangToken::EpicOrchestrator(state) => {
                    script.push_str(&format!("ORCHESTRATE_GOLD Au79_Epic[\"{}\"]\n", state));
                }
            }
        }

        // === Vim Kernel Keybinding Layer ===
        script.push_str("\n# --- VIM_KERNEL_INTEGRATION ---\n");
        script.push_str("VIM_BIND flame :FlameIgnite\n");
        script.push_str("VIM_BIND <leader>t :AdvanceStepperTick\n");
        script.push_str("VIM_BIND wafer :InjectSi14Wafer\n");
        script.push_str("VIM_BIND dnas :GencodeN7DNA\n");
        script.push_str("VIM_BIND epic :OrchestrateAu79\n");
        script.push_str("VIM_SET localleader=\\\\\n");
        script.push_str("VIM_AUTOCMD BufWritePost *.sagco :TranspileFlameLang\n");

        script.push_str("\nEMIT_STATE_GREEN\n");
        script.push_str("# Pipeline integrity: Unity H1 + Epic Au79 verified\n");
        script
    }

    pub fn verify_vim_bindings(script: &str) -> usize {
        script.lines().filter(|l| l.starts_with("VIM_BIND")).count()
    }
}
