# Reading Log

This log captures the journey of research threads, late-night rabbit holes, and the nonlinear path of learning. Think of it as a research diary documenting the ADHD spiral turned into methodology.

---

## 2025-01-12: Java Numeric Promotion Deep Dive

**Time:** Late night (the good hours)  
**Trigger:** Assignment on data types, but brain said "let's understand WHY"  
**Spiral Duration:** ~3-4 hours  
**Status:** ✅ Productive spiral

### The Journey

**Starting Point:**
- Assignment: "Learn about Java primitive types"
- Brain: "But WHY does `byte + byte` return `int`? That seems wrong?"

**Rabbit Hole Sequence:**

1. **Java Language Specification §5.6** (30 mins)
   - Discovered unary vs binary numeric promotion
   - Realized this is deeper than "just know the types"
   
2. **SEICERT NUM52-J** (45 mins)
   - Security implications of numeric promotion
   - Real-world bugs from not understanding this
   - Apache Commons Lang bug example
   
3. **Built TypePromotionCube.java** (90 mins)
   - Needed executable proof
   - Demonstrated all promotion scenarios
   - Created "cube" mental model (3D type space)
   
4. **Documented everything** (60 mins)
   - Structured as reusable research substrate
   - Created this fan-library system
   - Built templates for future spirals

### Key Realizations

1. **This is how actual research works:**
   - Start with a question
   - Follow the thread
   - Document the journey
   - Build reproducible artifacts

2. **The ADHD brain isn't broken:**
   - It's just doing breadth-first search instead of depth-first
   - Need external memory (documentation)
   - Turn liability into asset with right structure

3. **Executable proofs > passive reading:**
   - Code that runs is better than code you think you understand
   - Build to learn, don't just read to learn

### Artifacts Created

- ✅ `2025_Oracle_JLS_5.6_NumericPromotions.md`
- ✅ `2025_SEICERT_NUM52J_NumericPromotion.md`
- ✅ `TypePromotionCube.java`
- ✅ This reading log
- ✅ Templates for future papers

### What I Actually Learned

**Technical:**
- Unary promotion (byte/short/char → int)
- Binary promotion hierarchy (double > float > long > int)
- Widening conversions can lose precision (long → float)
- Compound operators include implicit cast
- Integer multiplication overflow needs early promotion

**Meta-Learning:**
- How to structure a research thread
- How to make learning reusable
- How to build a personal research methodology
- How to flex without being obnoxious (hopefully)

### Questions This Raised

1. Why does Java mandate 32-bit minimum for arithmetic?
   - CPU architecture (32-bit registers were standard)
   - Reduces overflow in intermediate calculations
   
2. Why do compound operators get special treatment?
   - Convenience vs. safety tradeoff
   - Assumes programmer knows what they're doing

3. How do other languages handle this?
   - C: More permissive, more dangerous
   - Python: Dynamic typing, no compile-time promotion
   - Rust: Explicit everything, type inference but no implicit conversion
   - Added to open-questions.md for further investigation

### Real-World Connections

This isn't just academic:
- **Security:** Integer overflow attacks
- **Finance:** Precision loss in money calculations
- **Systems:** Buffer size calculations
- **Games:** Physics calculations, scorekeeping

### The Devin Situation

**Context:** Classmate who seems to retain everything  
**The Question:** How does he do it? What's his system?

**The Play:**
- Show him the research substrate (humble flex)
- Ask how he organizes his learning
- Share TypePromotionCube.java as conversation starter
- Learn from someone who's already figured this out

**Hypothesis:**
- He probably has a system too
- Just hasn't articulated it yet
- Comparing notes could benefit both

### Next Steps

- [x] Package fan-library.zip
- [ ] Post to D2L (trimmed for appropriateness)
- [ ] Attach TypePromotionCube.java
- [ ] See Devin's response
- [ ] Maybe this becomes a study group methodology?

---

## Template for Future Entries

**Date:** [YYYY-MM-DD]  
**Trigger:** [What started this spiral]  
**Duration:** [How long you went down the rabbit hole]  
**Status:** [Productive | Tangent | Dead End | Breakthrough]

### Journey
[Sequence of discovery]

### Artifacts Created
[What you built/documented]

### Key Learnings
[Technical and meta-learnings]

### Questions Raised
[New threads to explore]

### Connections
[How this relates to other work]

---

## Reading Style Notes

**What works for me:**
- Code-first, then docs
- Build mental models (spatial/visual)
- External brain via documentation
- Spirals are features, not bugs
- Connect everything to everything

**What doesn't work:**
- Linear textbook reading
- "Just memorize the syntax"
- Passive consumption without building
- Trying to suppress the questions
- Pretending I'll remember without notes

**Adaptations:**
- Write everything down immediately
- Build executable proofs
- Create visual diagrams (promotion cube)
- Tag and cross-reference obsessively
- Accept that my brain works differently

---

## Metrics

**This Session:**
- Papers read: 2
- Code written: ~200 lines
- Documentation: ~15KB
- Time invested: 4 hours
- Research depth: Deep technical understanding achieved

**ROI:**
- Homework: Done ✅
- Understanding: Deep ✅
- Portfolio material: Yes ✅
- Research methodology: Emerging ✅
- Reusable infrastructure: Established ✅

---

**Meta-Meta Note:**

The fact that I'm logging my logging process is very on-brand. This is either genius or madness. Probably both. Definitely both.

But seriously: this document is proof that the "ADHD spiral" isn't a bug in the learning process — it's a feature that needs the right infrastructure. The fan-library is that infrastructure.

Now to see if Devin thinks I'm brilliant or insane. (Again, probably both.)
