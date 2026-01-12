# Reply to Devin — The Rabbit Hole Bibliography

-----

## The Honest Preamble

Hi Devin,

Your explanation clicked, so naturally I did what I always do — fell down a 3AM rabbit hole trying to understand *why* it works that way instead of just accepting it.

Fair warning: I have no memorization. Seriously. My brain is all RAM, no hard drive. If I don’t build a mental machine for something, it evaporates. So I compensate by connecting everything to everything else until it sticks.

I genuinely don’t know how actual QA engineers like yourself keep all this indexed in your head. Do you just… remember things? Is there a trick? Because I have to externalize everything into systems or it’s gone.

Anyway, here’s where the type promotion question took me:

-----

## Primary Sources (The Formal Stuff)

**Java Language Specification (JLS) §5.6 — Numeric Promotions**

- Oracle Corporation
- https://docs.oracle.com/javase/specs/jls/se25/html/jls-5.html
- *The canonical source. “If either operand is of type double, the other is converted to double.”*

**SEI CERT Oracle Coding Standard for Java — NUM52-J**

- Carnegie Mellon University, Software Engineering Institute
- https://wiki.sei.cmu.edu/confluence/display/java/NUM52-J.+Be+aware+of+numeric+promotion+behavior
- *This is where I found the precision loss edge case: int→float can lose bits in the mantissa even during widening. That felt important.*

-----

## Secondary Sources (The YouTube Spiral)

**Lucidchart — UML Class Diagram Tutorial** (10:16)

- *Required viewing from Module 2 resources. Helped visualize class relationships.*

**Java Tutorial 9 — UML to Code** (12:11, first 6:26)

- *Also from Module 2. Translating diagrams to actual Java.*

**Caleb Curry — Object-Oriented Programming with Java**

- O’Reilly / Pearson LiveLessons
- *Guy explains access modifiers like he’s telling a story. My brain liked that.*

**thenewboston — Java Beginner Programming Tutorials**

- YouTube playlist
- *Old but gold. Short videos, no fluff.*

**freeCodeCamp — Object-Oriented Programming in Java (Beginner’s Guide)**

- https://www.freecodecamp.org/news/object-oriented-programming-concepts-java/
- *Written tutorial that let me read at my own pace instead of pausing videos every 3 seconds.*

-----

## Tertiary Sources (The “Why Does This Work” Tangents)

**W3Schools — Java OOP**

- https://www.w3schools.com/java/java_oop.asp
- *Quick reference. DRY principle explanation stuck with me.*

**GeeksforGeeks — Java OOP Concepts**

- https://www.geeksforgeeks.org/java/object-oriented-programming-oops-concept-in-java/
- *The compile-time vs runtime polymorphism distinction finally made sense here.*

**IEEE 754 Floating-Point Standard**

- *Didn’t read the whole spec (I’m not insane), but skimmed enough to understand why float mantissa is 23 bits and why that matters for int→float precision loss.*

-----

## The Weird Part (Where My Brain Went)

After understanding the promotion hierarchy:

```
byte → short → int → long → float → double
```

I started seeing it as a directed graph. Then as a lattice. Then I thought about Rubik’s cube move algebra (clockwise = widening/safe, counter-clockwise = narrowing/explicit cast required).

Then I mapped my own CLI learning journey onto it:

- E212 errors → byte boundaries (learning limits)
- absolute paths → widening context (knowing where you are)
- shell scripts → int to long (automation scaling)
- containers → abstraction layer (like boxing)
- orchestration → full precision control

…and then I wrote 200 lines of Java that compiles and runs and demonstrates all of this.

I don’t know if that’s useful or unhinged. Probably both.

-----

## The Actual Question

How do you retain all this?

Like, you’re a senior QA engineer. You’ve presumably seen thousands of edge cases, promotion rules, casting gotchas, API quirks. Is it just pattern recognition from repetition? Do you have a reference system? Or does it eventually just… live in your head?

Because right now I’m building external scaffolding for everything (notes, diagrams, executable proofs, weird metaphors) and I’m curious if that ever consolidates into something more portable.

Appreciate any insight. And thanks for the clear explanation — it gave me something solid to build from.

— Dom

-----

## Attached

- `TypePromotionCube.java` — The executable proof-of-concept
- JLS §5.6 reference
- SEI CERT NUM52-J precision loss documentation

-----

*P.S. — I formatted my intro post in JSON because I genuinely think in structured data. Not trying to be clever, just… that’s how it came out.*