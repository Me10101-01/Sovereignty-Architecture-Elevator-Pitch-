# Open Questions

Unresolved threads, edge cases to explore, and questions that need more investigation. This is where future rabbit holes begin.

---

## Java Type System

### 1. Why does Java mandate 32-bit minimum for arithmetic?

**Current Understanding:**
- Historical: 32-bit CPUs were standard when Java was designed
- Performance: Aligned with register sizes
- Safety: Reduces overflow in intermediate calculations

**Still Wondering:**
- Why didn't they align with 8/16-bit architectures of the time?
- How do embedded Java systems (Java ME) handle this?
- Would modern Java benefit from smaller minimum sizes on IoT devices?

**Next Steps:**
- [ ] Research Java ME specifications
- [ ] Look into Java's original design docs (if available)
- [ ] Compare with C's behavior on different architectures

---

### 2. Compound operators: Convenience vs. consistency?

**The Inconsistency:**
```java
byte b = 100;
b = b + 1;     // Compile error
b += 1;        // OK (implicit cast)
```

**Questions:**
- Was this intentional or an oversight?
- Why make this exception to type safety?
- Has this caused real bugs in production code?
- Do other languages (C#, Kotlin) follow this pattern?

**Hypothesis:**
- Convenience won over consistency
- Assumed programmers using `+=` know what they're doing
- May be legacy from C influence

**Next Steps:**
- [ ] Search Java bug database for compound operator issues
- [ ] Check C# and Kotlin specifications
- [ ] Look for Gosling/Java designers discussing this choice

---

### 3. Floating-point precision loss in widening

**The Gotcha:**
```java
long l = 9_876_543_210L;
float f = l;  // Widening, but loses precision!
```

**Questions:**
- Why is this considered "widening" when it loses precision?
- Should this require explicit cast?
- How often does this bite people in practice?
- Are there compiler warnings for this?

**Next Steps:**
- [ ] Check if `-Xlint` warns about int→float or long→double
- [ ] Search for real-world bugs caused by this
- [ ] Compare with Rust's approach (does it allow this?)

---

## Cross-Language Comparisons

### 4. How do other languages handle numeric promotion?

**Known:**
- **C:** More permissive, allows implicit narrowing (dangerous)
- **Python:** Dynamic typing, no compile-time promotion
- **Rust:** Explicit conversions required (no implicit promotion)

**Want to Know:**
- **Go:** How does it handle type conversions?
- **Swift:** Similar to Rust or more like Java?
- **Kotlin:** Does it improve on Java's rules?
- **TypeScript:** How does it model numeric types?

**Hypothesis:**
- Trend is toward more explicit (Rust/Swift model)
- Java is middle ground between C and modern languages

**Next Steps:**
- [ ] Create comparison table across languages
- [ ] Build equivalent of TypePromotionCube in Rust
- [ ] Document Kotlin improvements over Java

---

### 5. Unsigned types in Java

**The Mystery:**
Java has `char` (16-bit unsigned) but no other unsigned types... until Java 8 added unsigned operations for existing types.

**Questions:**
- Why no native `unsigned int` or `unsigned long`?
- How do unsigned operations in Java 8+ work?
- Is the lack of unsigned types a design flaw or intentional simplification?
- How does this compare to C's unsigned types?

**Java 8 Unsigned API:**
```java
Integer.toUnsignedString(int)
Integer.compareUnsigned(int, int)
Long.toUnsignedString(long)
```

**Next Steps:**
- [ ] Explore Java's unsigned utility methods
- [ ] Compare performance: signed vs. unsigned operations
- [ ] Research why Java originally excluded unsigned types

---

## Security Implications

### 6. Real-world exploits from numeric promotion bugs?

**Known:**
- Apache Commons Lang bug (precision loss)
- SEICERT warns about security implications

**Want to Know:**
- Are there CVEs specifically about Java numeric promotion?
- Has this led to buffer overflows in Java applications?
- What about in Android (Dalvik/ART)?

**Next Steps:**
- [ ] Search CVE database for Java numeric promotion
- [ ] Look for security advisories mentioning NUM52-J
- [ ] Check Android security bulletins

---

### 7. Can static analysis catch all promotion bugs?

**Tools Available:**
- SpotBugs, PMD, SonarQube
- Checker Framework (more sophisticated)

**Questions:**
- What's the false positive rate?
- Are there patterns that slip through?
- Can this be made part of compiler (like Rust's borrow checker)?

**Next Steps:**
- [ ] Test TypePromotionCube.java with all static analyzers
- [ ] Intentionally create buggy code to see what's caught
- [ ] Research Java compiler plugin system

---

## Performance & Optimization

### 8. Performance cost of type promotion

**Questions:**
- Does promoting byte→int have CPU cost?
- Are smaller types ever actually faster?
- When does it make sense to use byte/short?
- JIT optimizations: does HotSpot optimize this away?

**Hypothesis:**
- Modern CPUs: `int` is probably always fastest
- Memory bandwidth: smaller types matter for large arrays
- Cache locality: byte arrays pack better

**Next Steps:**
- [ ] Write microbenchmarks comparing byte[] vs int[]
- [ ] Check JIT compiler output (use `-XX:+PrintAssembly`)
- [ ] Research Java Performance book for guidance

---

### 9. BigDecimal: When is it overkill?

**Known:**
- Required for financial calculations
- Performance cost: much slower than primitives

**Questions:**
- Quantify performance difference (10x? 100x?)
- Are there middle-ground options?
- When can you safely use `double` for money?

**Next Steps:**
- [ ] Benchmark primitive vs. BigDecimal arithmetic
- [ ] Research fixed-point arithmetic as alternative
- [ ] Look into JSR 354 (Money and Currency API)

---

## Edge Cases

### 10. Character encoding and char type

**The Weirdness:**
`char` is 16-bit, but Unicode has characters beyond 16 bits (surrogate pairs).

**Questions:**
- How does `char` handle emojis and other high codepoints?
- When should you use `char` vs `int` for codepoints?
- How does this interact with promotion rules?

**Example:**
```java
char emoji = '😀';  // Does this even compile?
```

**Next Steps:**
- [ ] Test high-codepoint characters
- [ ] Understand String.codePointAt() vs charAt()
- [ ] Research UTF-16 encoding in Java

---

### 11. Strictfp: Does anyone actually use this?

**What it is:**
`strictfp` modifier for strict floating-point calculations (IEEE 754 compliance).

**Questions:**
- When does this matter in practice?
- Performance cost?
- Why isn't it the default?
- Is it deprecated/removed in modern Java?

**Next Steps:**
- [ ] Test same calculations with/without strictfp
- [ ] Check Java 21 specification for strictfp status
- [ ] Find use cases where it made a difference

---

## Meta-Research Questions

### 12. How do other people organize their learning?

**Devin's Method:**
- Seems to retain everything
- Must have a system
- Want to compare notes

**Questions:**
- Note-taking systems (Zettelkasten, etc.)?
- Spaced repetition?
- Different brain, or just different method?

**Next Steps:**
- [x] Create fan-library as my system
- [ ] Ask Devin about his approach
- [ ] See if others want to collaborate

---

### 13. Is this methodology generalizable?

**Current Application:**
Java numeric promotion → Fan library structure

**Questions:**
- Would this work for other topics (networking, algorithms, etc.)?
- Can this be a template for others with ADHD?
- Should this be documented as a "meta-methodology"?

**Next Steps:**
- [ ] Test with next research topic
- [ ] Document the methodology itself
- [ ] Share with others who might benefit

---

## Questions Raised by Devin (TBD)

*This section will be filled in after Devin responds to the bibliography/artifact share.*

---

## Resolved Questions (Moved from Above)

### ✅ Why does byte + byte return int?
**Answer:** Unary numeric promotion. Prevents overflow in intermediate calculations.  
**Source:** JLS §5.6.1  
**Date Resolved:** 2025-01-12

---

## Question Priorities

**High Priority (investigate soon):**
1. Cross-language comparison (will help with understanding Java's design choices)
2. Static analysis effectiveness (practical for catching bugs)
3. Real-world security exploits (motivation for caring about this)

**Medium Priority (when relevant):**
4. Performance benchmarks (good for portfolio, blog post material)
5. BigDecimal alternatives (practical for projects)
6. Devin's methodology (collaboration opportunity)

**Low Priority (interesting but not urgent):**
7. Strictfp details (niche use case)
8. Historical design decisions (interesting but low ROI)
9. Embedded Java ME (not relevant to current coursework)

---

## Contributing to This List

**When to add a question:**
- Encounter something that doesn't make sense
- Find a contradiction between sources
- Think "I wonder why..." while coding
- Discover an edge case not covered in docs

**Format:**
```markdown
### N. Question Title

**Current Understanding:**
[What you know so far]

**Still Wondering:**
[What you don't know]

**Next Steps:**
- [ ] Action items to investigate
```

---

**Last Updated:** 2025-01-12  
**Total Open Questions:** 13  
**Total Resolved Questions:** 1  
**Priority Focus:** Cross-language comparison, static analysis, security exploits
