// SAGCO-Core — bare-metal instruction lexer + parser + VM
// Instruction set: read | wave | pulse | seal | spawn | fork | connect
// License: SSL-1.0 — Strategickhaos DAO LLC

pub mod lexer;
pub mod parser;
pub mod vm;
pub mod crypto;
pub mod cloud_io;

pub use lexer::{Lexer, Token};
pub use parser::{Command, Parser};
pub use vm::{SagcoVm, VmAntibody, VmResult};
pub use crypto::{sha256_hex, seal_file, seal_bytes, verify_seal, SealLedger};

/// Run a SAGCO bytecode stream through the full Lex → Parse → Execute pipeline.
pub fn run_stream(stream: &str) -> SagcoVm {
    let lexer  = Lexer::new(stream);
    let mut parser = Parser::new(lexer);
    let mut vm = SagcoVm::new();

    let cmds: Vec<Command> = parser.parse_program()
        .into_iter()
        .filter_map(|r| r.ok())
        .collect();

    for cmd in &cmds {
        let result = vm.execute(cmd);
        println!("{}", result.message);
        if result.antibody != VmAntibody::PassImmunity {
            println!("  ANTIBODY={}", result.antibody.as_str());
        }
    }

    vm
}
