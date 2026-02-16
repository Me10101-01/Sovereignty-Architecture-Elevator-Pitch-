/**
 * TypePromotionCube.java
 * 
 * An executable proof-of-concept demonstrating Java's numeric type promotion rules.
 * 
 * This program explores the type promotion hierarchy:
 * byte → short → int → long → float → double
 * 
 * References:
 * - Java Language Specification (JLS) §5.6 — Numeric Promotions
 * - SEI CERT Oracle Coding Standard for Java — NUM52-J
 * 
 * Key Concepts Demonstrated:
 * 1. Widening conversions (safe, implicit)
 * 2. Narrowing conversions (require explicit cast)
 * 3. Binary numeric promotion rules
 * 4. Precision loss edge cases (int → float)
 * 5. Mixed-type arithmetic operations
 * 
 * @author Dom
 * @version 1.0
 */
public class TypePromotionCube {

    /**
     * Represents a step in the type promotion hierarchy.
     */
    record PromotionStep(String fromType, String toType, String category, String safety) {}

    /**
     * Demonstrates the complete type promotion hierarchy as a directed graph.
     */
    static class PromotionHierarchy {
        private static final PromotionStep[] HIERARCHY = {
            new PromotionStep("byte", "short", "widening", "safe"),
            new PromotionStep("short", "int", "widening", "safe"),
            new PromotionStep("int", "long", "widening", "safe"),
            new PromotionStep("long", "float", "widening", "precision-loss-possible"),
            new PromotionStep("float", "double", "widening", "safe"),
            new PromotionStep("char", "int", "widening", "safe")
        };

        static void displayHierarchy() {
            System.out.println("╔════════════════════════════════════════════════════════════╗");
            System.out.println("║        Java Numeric Type Promotion Hierarchy               ║");
            System.out.println("╠════════════════════════════════════════════════════════════╣");
            System.out.println("║  byte → short → int → long → float → double               ║");
            System.out.println("║                                                            ║");
            System.out.println("║  Widening (→): Implicit, safe                             ║");
            System.out.println("║  Narrowing (←): Explicit cast required                     ║");
            System.out.println("╚════════════════════════════════════════════════════════════╝");
            System.out.println();

            for (PromotionStep step : HIERARCHY) {
                System.out.printf("  %s → %s [%s] (%s)%n",
                    step.fromType(), step.toType(), step.category(), step.safety());
            }
            System.out.println();
        }
    }

    /**
     * Demonstrates widening conversions (implicit, safe).
     */
    static class WideningConversions {
        static void demonstrate() {
            System.out.println("╔════════════════════════════════════════════════════════════╗");
            System.out.println("║              Widening Conversions (Safe)                   ║");
            System.out.println("╚════════════════════════════════════════════════════════════╝");
            
            // byte → short → int → long → float → double
            byte b = 42;
            short s = b;        // byte → short (implicit)
            int i = s;          // short → int (implicit)
            long l = i;         // int → long (implicit)
            float f = l;        // long → float (implicit, but see precision loss below)
            double d = f;       // float → double (implicit)

            System.out.printf("  byte:   %d%n", b);
            System.out.printf("  short:  %d%n", s);
            System.out.printf("  int:    %d%n", i);
            System.out.printf("  long:   %d%n", l);
            System.out.printf("  float:  %.1f%n", f);
            System.out.printf("  double: %.1f%n", d);
            System.out.println();
        }
    }

    /**
     * Demonstrates narrowing conversions (explicit cast required).
     */
    static class NarrowingConversions {
        static void demonstrate() {
            System.out.println("╔════════════════════════════════════════════════════════════╗");
            System.out.println("║         Narrowing Conversions (Explicit Cast)              ║");
            System.out.println("╚════════════════════════════════════════════════════════════╝");
            
            double d = 123.456;
            float f = (float) d;    // double → float (explicit)
            long l = (long) f;      // float → long (explicit, truncates decimal)
            int i = (int) l;        // long → int (explicit)
            short s = (short) i;    // int → short (explicit)
            byte b = (byte) s;      // short → byte (explicit)

            System.out.printf("  double: %.3f%n", d);
            System.out.printf("  float:  %.3f%n", f);
            System.out.printf("  long:   %d%n", l);
            System.out.printf("  int:    %d%n", i);
            System.out.printf("  short:  %d%n", s);
            System.out.printf("  byte:   %d%n", b);
            System.out.println();
        }
    }

    /**
     * Demonstrates precision loss during int → float conversion.
     * This is the edge case discovered in SEI CERT NUM52-J.
     * 
     * int has 32 bits of precision.
     * float has 24 bits of mantissa (23 explicit + 1 implicit).
     * Therefore, large int values lose precision when converted to float.
     */
    static class PrecisionLossEdgeCase {
        static void demonstrate() {
            System.out.println("╔════════════════════════════════════════════════════════════╗");
            System.out.println("║           Precision Loss: int → float (IEEE 754)          ║");
            System.out.println("╠════════════════════════════════════════════════════════════╣");
            System.out.println("║  float mantissa: 23 bits (+ 1 implicit)                    ║");
            System.out.println("║  int precision: 32 bits                                    ║");
            System.out.println("║  Result: Large ints lose precision when widened to float  ║");
            System.out.println("╚════════════════════════════════════════════════════════════╝");

            // Case 1: Small values (no precision loss)
            int smallInt = 42;
            float smallFloat = smallInt;
            int backToInt = (int) smallFloat;
            
            System.out.println("\nSmall value (no precision loss):");
            System.out.printf("  Original int:    %d%n", smallInt);
            System.out.printf("  As float:        %.1f%n", smallFloat);
            System.out.printf("  Back to int:     %d%n", backToInt);
            System.out.printf("  Preserved:       %s%n", smallInt == backToInt ? "✓" : "✗");

            // Case 2: Large values (precision loss occurs)
            int largeInt = 16777217;  // 2^24 + 1 (exceeds float mantissa precision)
            float largeFloat = largeInt;
            int backToIntLarge = (int) largeFloat;
            
            System.out.println("\nLarge value (precision loss):");
            System.out.printf("  Original int:    %d%n", largeInt);
            System.out.printf("  As float:        %.0f%n", largeFloat);
            System.out.printf("  Back to int:     %d%n", backToIntLarge);
            System.out.printf("  Preserved:       %s%n", largeInt == backToIntLarge ? "✓" : "✗");
            System.out.printf("  Bits lost:       %d%n", largeInt - backToIntLarge);
            System.out.println();
        }
    }

    /**
     * Demonstrates binary numeric promotion in mixed-type arithmetic.
     * JLS §5.6.2: "If either operand is of type double, the other is converted to double."
     */
    static class BinaryNumericPromotion {
        static void demonstrate() {
            System.out.println("╔════════════════════════════════════════════════════════════╗");
            System.out.println("║         Binary Numeric Promotion (JLS §5.6.2)              ║");
            System.out.println("╠════════════════════════════════════════════════════════════╣");
            System.out.println("║  Rules:                                                    ║");
            System.out.println("║  1. If either operand is double → both become double       ║");
            System.out.println("║  2. Else if either is float → both become float            ║");
            System.out.println("║  3. Else if either is long → both become long              ║");
            System.out.println("║  4. Else → both become int                                 ║");
            System.out.println("╚════════════════════════════════════════════════════════════╝");
            
            byte b = 10;
            short s = 20;
            int i = 30;
            long l = 40L;
            float f = 50.0f;
            double d = 60.0;

            // byte + short → int (both promoted to int)
            var result1 = b + s;
            System.out.printf("\nbyte + short → int:%n");
            System.out.printf("  %d + %d = %d (type: int)%n", b, s, result1);

            // int + long → long
            var result2 = i + l;
            System.out.printf("\nint + long → long:%n");
            System.out.printf("  %d + %d = %d (type: long)%n", i, l, result2);

            // long + float → float
            var result3 = l + f;
            System.out.printf("\nlong + float → float:%n");
            System.out.printf("  %d + %.1f = %.1f (type: float)%n", l, f, result3);

            // float + double → double
            var result4 = f + d;
            System.out.printf("\nfloat + double → double:%n");
            System.out.printf("  %.1f + %.1f = %.1f (type: double)%n", f, d, result4);

            // Complex expression: byte + int + float + double → double
            var result5 = b + i + f + d;
            System.out.printf("\nbyte + int + float + double → double:%n");
            System.out.printf("  %d + %d + %.1f + %.1f = %.1f (type: double)%n", 
                b, i, f, d, result5);
            System.out.println();
        }
    }

    /**
     * Demonstrates the "CLI Learning Journey" metaphor mapping.
     * This is the unique cognitive framework mentioned in the document.
     */
    static class CLILearningMetaphor {
        static void demonstrate() {
            System.out.println("╔════════════════════════════════════════════════════════════╗");
            System.out.println("║          The CLI Learning Journey Metaphor                 ║");
            System.out.println("╠════════════════════════════════════════════════════════════╣");
            System.out.println("║  Type System    ←→    CLI/DevOps Concept                   ║");
            System.out.println("╠════════════════════════════════════════════════════════════╣");
            System.out.println("║  byte           ←→    E212 errors (learning limits)        ║");
            System.out.println("║  short → int    ←→    absolute paths (widening context)    ║");
            System.out.println("║  int → long     ←→    shell scripts (automation scaling)   ║");
            System.out.println("║  long → float   ←→    containers (abstraction layer)       ║");
            System.out.println("║  float → double ←→    orchestration (full precision)       ║");
            System.out.println("╚════════════════════════════════════════════════════════════╝");
            System.out.println();
            
            System.out.println("Conceptual Mapping:");
            System.out.println("  • Widening = Safe forward movement in learning");
            System.out.println("  • Narrowing = Deliberate downscoping (explicit choice)");
            System.out.println("  • Precision loss = Inevitable tradeoffs in abstraction");
            System.out.println("  • Type safety = Operational safety through understanding");
            System.out.println();
        }
    }

    /**
     * Demonstrates the Rubik's Cube algebra analogy.
     * Clockwise = widening (safe), Counter-clockwise = narrowing (explicit).
     */
    static class RubiksCubeAnalogy {
        static void demonstrate() {
            System.out.println("╔════════════════════════════════════════════════════════════╗");
            System.out.println("║            Rubik's Cube Move Algebra Analogy               ║");
            System.out.println("╠════════════════════════════════════════════════════════════╣");
            System.out.println("║  Clockwise (R)          → Widening (implicit, safe)        ║");
            System.out.println("║  Counter-clockwise (R') → Narrowing (explicit cast)        ║");
            System.out.println("║  Commutator [R, U]      → Composition of promotions        ║");
            System.out.println("╚════════════════════════════════════════════════════════════╝");
            System.out.println();
            
            System.out.println("Algebraic Properties:");
            System.out.println("  • Widening is transitive: byte→int→double is valid");
            System.out.println("  • Narrowing requires explicit 'moves': (byte)(int)x");
            System.out.println("  • Some paths are irreversible (precision loss)");
            System.out.println("  • Identity: type→type is always safe (no-op)");
            System.out.println();
        }
    }

    /**
     * Main method orchestrating all demonstrations.
     */
    public static void main(String[] args) {
        System.out.println();
        System.out.println("════════════════════════════════════════════════════════════════");
        System.out.println("         TYPEPROMOTION CUBE: Java Type Promotion Explorer      ");
        System.out.println("════════════════════════════════════════════════════════════════");
        System.out.println("  An executable proof-of-concept demonstrating numeric type     ");
        System.out.println("  promotion rules from first principles.                        ");
        System.out.println("════════════════════════════════════════════════════════════════");
        System.out.println();

        // Display the hierarchy
        PromotionHierarchy.displayHierarchy();

        // Demonstrate widening conversions
        WideningConversions.demonstrate();

        // Demonstrate narrowing conversions
        NarrowingConversions.demonstrate();

        // Demonstrate precision loss edge case
        PrecisionLossEdgeCase.demonstrate();

        // Demonstrate binary numeric promotion
        BinaryNumericPromotion.demonstrate();

        // Display conceptual metaphors
        CLILearningMetaphor.demonstrate();
        RubiksCubeAnalogy.demonstrate();

        // Summary
        System.out.println("╔════════════════════════════════════════════════════════════╗");
        System.out.println("║                     Key Takeaways                          ║");
        System.out.println("╠════════════════════════════════════════════════════════════╣");
        System.out.println("║  1. Widening conversions are implicit and generally safe   ║");
        System.out.println("║  2. Narrowing conversions require explicit casts           ║");
        System.out.println("║  3. int→float can lose precision (IEEE 754 limitation)     ║");
        System.out.println("║  4. Binary operations promote to the 'wider' type          ║");
        System.out.println("║  5. Understanding types = understanding constraints         ║");
        System.out.println("╚════════════════════════════════════════════════════════════╝");
        System.out.println();

        System.out.println("References:");
        System.out.println("  • JLS §5.6 — Numeric Promotions");
        System.out.println("    https://docs.oracle.com/javase/specs/jls/se25/html/jls-5.html");
        System.out.println("  • SEI CERT NUM52-J — Numeric promotion behavior");
        System.out.println("    https://wiki.sei.cmu.edu/confluence/display/java/NUM52-J");
        System.out.println("  • IEEE 754 Floating-Point Standard");
        System.out.println();

        System.out.println("════════════════════════════════════════════════════════════════");
        System.out.println("  \"I don't know if that's useful or unhinged. Probably both.\"  ");
        System.out.println("                                                    — Dom         ");
        System.out.println("════════════════════════════════════════════════════════════════");
        System.out.println();
    }
}
