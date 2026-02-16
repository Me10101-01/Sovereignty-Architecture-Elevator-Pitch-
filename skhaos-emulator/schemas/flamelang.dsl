/**
 * FlameLang DSL - Bio-Physics Pattern Compiler
 * 
 * Domain-Specific Language for compiling bio UDAP patterns to executable code
 * Syntax: FLAME <pattern> WITH <constraints> EMIT <target>
 */

grammar FlameLang;

// Entry point
program: statement+ EOF;

statement
    : flame_compile
    | bio_pattern
    | physics_constraint
    ;

// FLAME compilation directive
flame_compile
    : 'FLAME' pattern 'WITH' constraints 'EMIT' target ';'
    ;

// Bio patterns
pattern
    : zipf_pattern
    | dolphin_pattern
    | hybrid_pattern
    ;

zipf_pattern
    : 'ZIPF' '(' unit_list ')' 'RANKED' 'BY' alpha=NUMBER
    ;

dolphin_pattern
    : 'DOLPHIN' '(' comm_type ')' 'AT' freq=NUMBER 'HZ'
    ;

hybrid_pattern
    : 'HYBRID' '(' pattern ',' pattern ')'
    ;

comm_type
    : 'WHISTLE'
    | 'CLICK'
    | 'DIALECT'
    ;

// Physics constraints
constraints
    : constraint ('AND' constraint)*
    ;

constraint
    : physics_law
    | frequency_constraint
    | energy_constraint
    ;

physics_law
    : 'ENTROPY' direction
    | 'UNCERTAINTY' '<=' threshold=NUMBER
    | 'CONSERVATION' 'BALANCED'
    | 'RELATIVITY' spacetime
    ;

direction
    : 'INCREASES'
    | 'MINIMIZED'
    ;

frequency_constraint
    : 'FREQUENCY' 'IN' range
    ;

energy_constraint
    : 'ENERGY' 'CONSERVED'
    ;

// Targets
target
    : 'RUST' rust_module
    | 'MSMC' state_machine
    | 'UDAP' uri_pattern
    ;

rust_module
    : 'MODULE' ID
    ;

state_machine
    : 'STATE' ID
    ;

uri_pattern
    : STRING
    ;

// Supporting rules
unit_list
    : STRING (',' STRING)*
    ;

range
    : '[' NUMBER ',' NUMBER ']'
    ;

spacetime
    : '(' NUMBER ',' NUMBER ',' NUMBER ',' NUMBER ')'
    ;

// Lexer rules
ID: [a-zA-Z_][a-zA-Z0-9_]*;
NUMBER: [0-9]+ ('.' [0-9]+)?;
STRING: '"' (~["\r\n])* '"';
WS: [ \t\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;

// Example programs:
//
// FLAME ZIPF("moan", "cry", "grumble") RANKED BY 1.0
//   WITH ENTROPY INCREASES AND FREQUENCY IN [20, 4000]
//   EMIT RUST MODULE bio_zipf;
//
// FLAME DOLPHIN(WHISTLE) AT 10000 HZ
//   WITH UNCERTAINTY <= 5.27e-35 AND ENERGY CONSERVED
//   EMIT UDAP "skhaos://bio/dolphin/whistle?signature=true&hz=10000";
//
// FLAME HYBRID(ZIPF("a", "b", "a"), DOLPHIN(CLICK) AT 150000 HZ)
//   WITH ENTROPY INCREASES AND CONSERVATION BALANCED
//   EMIT MSMC STATE rondo_cycle;
