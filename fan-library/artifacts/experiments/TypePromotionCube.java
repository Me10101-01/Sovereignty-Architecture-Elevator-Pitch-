/**
 * TypePromotionCube.java
 * 
 * Executable proof demonstrating Java numeric type promotion behavior
 * across multiple dimensions: unary, binary, and widening conversions.
 * 
 * This artifact demonstrates:
 * 1. Unary numeric promotion (JLS §5.6.1)
 * 2. Binary numeric promotion (JLS §5.6.2)
 * 3. Widening primitive conversions (JLS §5.1.2)
 * 4. Potential precision loss and overflow scenarios
 * 
 * Relates to: SEICERT NUM52-J (Numeric Promotion)
 * Author: Research substrate for Java fundamentals exploration
 * Date: 2025
 */

public class TypePromotionCube {
    
    /**
     * Demonstrates unary numeric promotion: smaller types promoted to int
     */
    public static void demonstrateUnaryPromotion() {
        System.out.println("=== UNARY NUMERIC PROMOTION ===");
        
        byte b = 10;
        short s = 20;
        char c = 'A'; // ASCII value 65
        
        // All these operations promote to int
        System.out.println("byte negation type: " + getType(-b));
        System.out.println("short bitwise NOT type: " + getType(~s));
        System.out.println("char bitwise NOT type: " + getType(~c));
        
        // Demonstration: assignment requires explicit cast
        // byte result = -b; // Would not compile!
        byte result = (byte) -b;
        System.out.println("byte -10 becomes: " + result);
        System.out.println();
    }
    
    /**
     * Demonstrates binary numeric promotion: operands promoted to common type
     */
    public static void demonstrateBinaryPromotion() {
        System.out.println("=== BINARY NUMERIC PROMOTION ===");
        
        byte b = 10;
        short s = 20;
        int i = 30;
        long l = 40L;
        float f = 50.0f;
        double d = 60.0;
        
        // Byte + Short = int
        System.out.println("byte + short type: " + getType(b + s));
        System.out.println("byte + short value: " + (b + s));
        
        // Int + Long = long
        System.out.println("int + long type: " + getType(i + l));
        System.out.println("int + long value: " + (i + l));
        
        // Long + Float = float
        System.out.println("long + float type: " + getType(l + f));
        System.out.println("long + float value: " + (l + f));
        
        // Float + Double = double
        System.out.println("float + double type: " + getType(f + d));
        System.out.println("float + double value: " + (f + d));
        System.out.println();
    }
    
    /**
     * Demonstrates widening conversions and potential precision loss
     */
    public static void demonstrateWideningConversions() {
        System.out.println("=== WIDENING CONVERSIONS & PRECISION ===");
        
        // Safe widening: no loss
        int smallInt = 42;
        long widerLong = smallInt;
        System.out.println("int 42 -> long: " + widerLong + " (no loss)");
        
        // Potentially lossy widening: int to float
        int largeInt = 123456789;
        float floatVersion = largeInt;
        int backToInt = (int) floatVersion;
        System.out.println("int " + largeInt + " -> float -> int: " + backToInt);
        System.out.println("Precision lost: " + (largeInt != backToInt));
        
        // Potentially lossy widening: long to float
        long largeLong = 9876543210L;
        float floatFromLong = largeLong;
        long backToLong = (long) floatFromLong;
        System.out.println("long " + largeLong + " -> float -> long: " + backToLong);
        System.out.println("Precision lost: " + (largeLong != backToLong));
        
        // Potentially lossy widening: long to double
        long veryLargeLong = 9007199254740993L; // 2^53 + 1
        double doubleVersion = veryLargeLong;
        long backFromDouble = (long) doubleVersion;
        System.out.println("long " + veryLargeLong + " -> double -> long: " + backFromDouble);
        System.out.println("Precision lost: " + (veryLargeLong != backFromDouble));
        System.out.println();
    }
    
    /**
     * Demonstrates overflow scenarios in type promotion
     */
    public static void demonstrateOverflow() {
        System.out.println("=== OVERFLOW SCENARIOS ===");
        
        // Byte overflow during promotion
        byte maxByte = 127;
        byte minByte = -128;
        
        // Addition promotes to int, no overflow in int
        int byteSum = maxByte + minByte;
        System.out.println("byte max + byte min = " + byteSum + " (promoted to int)");
        
        // But assignment back to byte can overflow
        byte overflowResult = (byte) (maxByte + 1);
        System.out.println("byte 127 + 1 = " + overflowResult + " (overflow!)");
        
        // Integer multiplication overflow
        int large1 = 100000;
        int large2 = 100000;
        int product = large1 * large2; // Overflows!
        long correctProduct = (long) large1 * large2; // Cast one operand first
        System.out.println("int 100000 * 100000 = " + product + " (overflow!)");
        System.out.println("(long) 100000 * 100000 = " + correctProduct + " (correct)");
        System.out.println();
    }
    
    /**
     * Demonstrates the promotion cube concept: dimensions of type interaction
     */
    public static void demonstratePromotionCube() {
        System.out.println("=== TYPE PROMOTION CUBE ===");
        System.out.println("Visualizing 3D type promotion space:");
        System.out.println();
        
        // Axis 1: Size (byte -> short -> int -> long)
        System.out.println("Size Axis (integral):");
        System.out.println("  byte(8) -> short(16) -> int(32) -> long(64)");
        
        // Axis 2: Precision (integral -> float -> double)
        System.out.println("Precision Axis:");
        System.out.println("  integral -> float(32) -> double(64)");
        
        // Axis 3: Signedness (char unsigned vs byte signed)
        System.out.println("Signedness Axis:");
        System.out.println("  char(unsigned 16) vs short(signed 16)");
        System.out.println();
        
        // Corner case examples
        byte b = 100;
        char c = 100;
        
        // Both promote to int, but different representations
        System.out.println("Signed byte 100: " + b);
        System.out.println("Unsigned char 100: " + (int) c);
        
        byte negByte = -1;
        char charFromByte = (char) negByte; // 65535 (0xFFFF)
        System.out.println("Byte -1 as char: " + (int) charFromByte);
        System.out.println();
    }
    
    /**
     * Helper method to determine the runtime type of a numeric expression
     * Note: Due to type erasure, this uses method overloading
     */
    private static String getType(int value) { return "int"; }
    private static String getType(long value) { return "long"; }
    private static String getType(float value) { return "float"; }
    private static String getType(double value) { return "double"; }
    
    /**
     * Main entry point: runs all demonstrations
     */
    public static void main(String[] args) {
        System.out.println("╔══════════════════════════════════════════════════════════╗");
        System.out.println("║       TYPE PROMOTION CUBE - EXECUTABLE PROOF             ║");
        System.out.println("║   Demonstrating Java Numeric Promotion Behavior (JLS)   ║");
        System.out.println("╚══════════════════════════════════════════════════════════╝");
        System.out.println();
        
        demonstrateUnaryPromotion();
        demonstrateBinaryPromotion();
        demonstrateWideningConversions();
        demonstrateOverflow();
        demonstratePromotionCube();
        
        System.out.println("╔══════════════════════════════════════════════════════════╗");
        System.out.println("║              DEMONSTRATION COMPLETE                       ║");
        System.out.println("║  All numeric promotion behaviors have been exhibited.     ║");
        System.out.println("╚══════════════════════════════════════════════════════════╝");
    }
}
