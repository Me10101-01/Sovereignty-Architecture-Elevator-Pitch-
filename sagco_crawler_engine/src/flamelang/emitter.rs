use crate::flamelang::token::FlameLangToken;

pub struct FlameEmitter;

impl FlameEmitter {
    pub fn transpile_to_flamelang(tokens: &[FlameLangToken]) -> String {
        let mut script = String::new();
        script.push_str("# --- FLAME_LANG COMPILED OUTPUT ---\n");
        script.push_str("# SAGCO-0023 STEPPER_CRAWLER_TICKS_ENGINE\n");
        script.push_str("# Periodic Table → FlameLang bridge\n\n");

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
                FlameLangToken::UnityNode(id) => {
                    script.push_str(&format!("BIND_COSMOS Hydrogen_H1_Unity[{}]\n", id));
                }
                FlameLangToken::EpicOrchestrator(name) => {
                    script.push_str(&format!("ORCHESTRATE Gold_Au79_Epic[\"{}\"]\n", name));
                }
            }
        }

        script.push_str("\nEMIT_STATE_GREEN\n");
        script
    }
}
