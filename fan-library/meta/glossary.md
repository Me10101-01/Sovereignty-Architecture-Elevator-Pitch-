# Glossary

A living dictionary of terms that matter in this research journey. Not textbook definitions — practical understanding from actually working with these concepts.

---

## Java Type System

### Primitive Types
The eight basic data types built into Java. Unlike objects, these are stored directly in memory (stack), not on the heap.

**The Eight:**
- **Integer types:** `byte` (8-bit), `short` (16-bit), `int` (32-bit), `long` (64-bit)
- **Floating-point types:** `float` (32-bit), `double` (64-bit)
- **Character:** `char` (16-bit unsigned)
- **Boolean:** `boolean` (true/false, implementation-specific size)

**Why it matters:** Understanding these is fundamental to understanding promotion rules and memory efficiency.

### Numeric Promotion
The automatic conversion of operands to a common type before evaluation. Java's way of making different-sized numbers work together.

**Two kinds:**
1. **Unary:** Single operand promoted (e.g., `-byte` → `int`)
2. **Binary:** Two operands promoted to common type (e.g., `int + long` → `long + long`)

**Analogy:** Like converting inches and feet to a common unit before adding them.

### Widening Conversion
Converting a smaller type to a larger type. Generally "safe" (doesn't lose magnitude), but can lose precision.

**Safe path:**
```
byte → short → int → long → float → double
char → int → long → float → double
```

**Gotcha:** `int` → `float` and `long` → `double` can lose precision even though they're "widening."

### Narrowing Conversion
Converting a larger type to a smaller type. Requires explicit cast because it can lose data.

**Example:**
```java
int big = 1000;
byte small = (byte) big;  // Explicit cast required, value wraps around
```

**Why explicit:** Forces programmer to acknowledge potential data loss.

### Type Promotion Cube (My Term)
Mental model I created: visualizing type promotion as 3D space with axes for size, precision, and signedness.

**Axes:**
- **Size:** byte → short → int → long
- **Precision:** integral → float → double
- **Signedness:** signed vs unsigned (char vs byte/short)

**Why useful:** Makes it easier to reason about complex promotion scenarios.

---

## Java Language Specification (JLS)

### JLS §5.6
The section of the Java Language Specification that defines numeric promotion rules.

**Key subsections:**
- §5.6.1: Unary Numeric Promotion
- §5.6.2: Binary Numeric Promotion

**Fun fact:** Reading specs is dense but authoritative. Worth referencing.

---

## Security & Correctness

### Integer Overflow
When an arithmetic operation produces a value outside the range of the result type. In Java, integer overflow wraps around (no exception thrown).

**Example:**
```java
byte b = 127;
b += 1;  // Results in -128, not 128
```

**Why dangerous:** Can lead to security vulnerabilities, especially in size calculations for buffers.

### Precision Loss
When converting between types loses exact value representation. Common in integer → float conversions.

**Example:**
```java
int big = 123456789;
float f = big;  // Precision lost
int back = (int) f;  // 123456792 (not original!)
```

**Why it matters:** Critical in financial calculations, scientific computing.

### SEICERT
SEI CERT Oracle Coding Standard for Java — a set of secure coding guidelines.

**NUM52-J:** "Be aware of numeric promotion behavior" — the rule this research is all about.

---

## Research Methodology

### Fan Library
This repository structure. A "fan" because it expands outward from a central question into many related threads.

**Structure:**
- `/papers` — Research papers and specifications
- `/artifacts` — Executable code that proves concepts
- `/meta` — Templates, logs, glossaries (this file)

**Purpose:** External memory for an ADHD brain. Research substrate for continued learning.

### Executable Proof
Code that demonstrates a concept by running. Better than just reading about something.

**Example:** `TypePromotionCube.java` proves numeric promotion rules by showing output.

**Philosophy:** "Show, don't tell" applied to learning.

### Research Substrate
A structured foundation for ongoing research. Not just notes — a system.

**Components:**
- Templates for intake
- Logging system
- Cross-references
- Executable artifacts

**Goal:** Turn one-off learning into accumulating knowledge.

### ADHD Spiral (Reframed)
What others call "getting distracted" — reframed as breadth-first search in the knowledge graph.

**Old view:** "I can't focus on the assignment"  
**New view:** "I'm exploring the conceptual space around the assignment"

**Key insight:** Not a bug, it's a feature that needs the right infrastructure (this library).

---

## Language Comparison

### Implicit Conversion
When a language automatically converts between types without explicit instruction.

**Java:** Allows widening (byte → int) but not narrowing (int → byte)  
**C:** More permissive, allows more implicit narrowing (dangerous)  
**Python:** Dynamic typing, no compile-time conversions  
**Rust:** Almost no implicit conversions, type inference but explicit conversion required

### Type Safety
How strictly a language enforces type rules.

**Spectrum:**
- **Strict:** Rust, Haskell (almost no implicit anything)
- **Moderate:** Java, C# (some implicit conversions)
- **Loose:** C, JavaScript (lots of implicit conversions)

---

## Patterns & Anti-Patterns

### Compound Assignment Operator
Operators like `+=`, `-=`, `*=` that combine operation and assignment.

**Secret:** They include an implicit cast!

```java
byte b = 100;
b = b + 1;     // Compile error (int cannot be assigned to byte)
b += 1;        // OK! Equivalent to: b = (byte)(b + 1)
```

**Why confusing:** Inconsistent with regular assignment rules.

### Math.***Exact() Methods
Java 8+ methods that throw exceptions on overflow instead of wrapping.

**Available:**
- `Math.addExact(int, int)`
- `Math.subtractExact(int, int)`
- `Math.multiplyExact(int, int)`
- `Math.incrementExact(int)`
- etc.

**Usage:** When overflow is a bug, not expected behavior.

---

## Memory & Performance

### Stack vs Heap
**Stack:** Where primitive types and references are stored. Fast, automatic cleanup.  
**Heap:** Where objects are stored. Slower, garbage collected.

**Why primitives exist:** Performance. `int` is much faster than `Integer`.

### Register Size
CPU registers are typically 32-bit or 64-bit. Java's choice to promote everything to at least `int` (32-bit) aligns with this.

**Historical context:** When Java was designed, 32-bit CPUs were dominant.

---

## Terms to Add (Future)

- [ ] Mantissa (in floating-point representation)
- [ ] Two's complement (integer representation)
- [ ] IEEE 754 (floating-point standard)
- [ ] Type erasure (generics)
- [ ] Boxing/Unboxing (primitive ↔ wrapper classes)

---

## Personal Notation

### Symbols I Use in Notes

- `→` : "promotes to" or "converts to"
- `↔` : "can convert bidirectionally"
- `⚠️` : Warning/gotcha
- `✅` : Verified/tested
- `❌` : Won't compile or is incorrect
- `🤔` : Need to investigate further
- `💡` : Aha moment

---

## Cross-References

**Related Papers:**
- [2025_Oracle_JLS_5.6_NumericPromotions.md](../papers/java-spec/2025_Oracle_JLS_5.6_NumericPromotions.md)
- [2025_SEICERT_NUM52J_NumericPromotion.md](../papers/java-spec/2025_SEICERT_NUM52J_NumericPromotion.md)

**Related Artifacts:**
- [TypePromotionCube.java](../artifacts/experiments/TypePromotionCube.java)

**Related Questions:**
- [open-questions.md](./open-questions.md)

---

**Last Updated:** 2025-01-12  
**Status:** Living document  
**Growth:** Started with ~10 terms, will expand as research continues
