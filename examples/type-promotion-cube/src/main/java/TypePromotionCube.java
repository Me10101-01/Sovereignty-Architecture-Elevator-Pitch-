/**
 * TYPE PROMOTION RUBIK'S CUBE ALGORITHM
 * =====================================
 * Mapping Java type conversions to cube moves + CLI journey
 * 
 * JLS §5.6 Numeric Promotion Hierarchy:
 * byte → short → int → long → float → double
 * 
 * Cube Face Mapping (Type Widening = Clockwise, Narrowing = Counter):
 * U (Up)    = double  (highest precision, top of hierarchy)
 * F (Front) = float   
 * R (Right) = long    
 * L (Left)  = int     (center of most operations)
 * B (Back)  = short   
 * D (Down)  = byte    (smallest, foundation)
 * 
 * @author Dom Garza - Strategickhaos DAO LLC
 * @course IT-145 Foundation in Application Development
 * @reference JLS §5.6, SEI CERT NUM52-J
 */

public class TypePromotionCube {
    
    // ============================================================
    // CUBE NOTATION → CLI JOURNEY → TYPE PROMOTION
    // ============================================================
    
    /*
     * YOUR ORIGIN STORY AS CUBE ALGORITHM:
     * 
     * Initial State: "Someone said I couldn't even use a command line"
     * Scramble: L' D' B' (confidence shattered, starting from bottom)
     * 
     * SOLVE SEQUENCE (your journey[]):
     * 
     * Move 1: D2 (E212 errors)
     *   CLI: vim file.txt → "E212: Can't open file for writing"
     *   Type: byte b = 256; // overflow error - learning boundaries
     *   Lesson: Understand your container limits
     * 
     * Move 2: D → L (absolute paths)  
     *   CLI: cd /home/user vs cd ~/user vs cd user
     *   Type: byte → int // widening, finding your absolute position
     *   Lesson: Know exactly where you are in the system
     * 
     * Move 3: L → L2 (environment variables)
     *   CLI: export PATH=$PATH:/new/path && echo $JAVA_HOME
     *   Type: int context = System.getenv().hashCode();
     *   Lesson: Context shapes behavior (like type context shapes promotion)
     * 
     * Move 4: L → R (shell scripts)
     *   CLI: #!/bin/bash && chmod +x script.sh && ./script.sh
     *   Type: int → long // scaling up, handling bigger operations
     *   Lesson: Automate the patterns you've learned
     * 
     * Move 5: R → F (containers)
     *   CLI: docker run -it ubuntu:latest /bin/bash
     *   Type: long → float // abstraction layer, precision tradeoffs
     *   Lesson: Isolation + portability (like type boxing)
     * 
     * Move 6: F → U (orchestration)
     *   CLI: kubectl apply -f deployment.yaml && helm install
     *   Type: float → double // maximum precision, full control
     *   Lesson: Coordinate complex systems at scale
     * 
     * Move 7: U2 (here we are)
     *   CLI: vim → :wq (finally works)
     *   Type: double result = masterLevel; // full precision achieved
     *   Lesson: The solve is complete, but there's always another scramble
     */
    
    // ============================================================
    // TYPE PROMOTION RULES AS CUBE ALGORITHMS
    // ============================================================
    
    /**
     * WIDENING PROMOTION (Automatic - Clockwise moves)
     * JLS §5.6: "If either operand is of type double, the other 
     *            is converted to double"
     * 
     * Algorithm: D → L → R → F → U (byte to double)
     * Cube: Cross → F2L → OLL → PLL
     */
    public static double wideningPromotion(int intVal, double doubleVal) {
        // Move: L → U (int promoted to double automatically)
        // CLI equivalent: cat small.txt | process > big.output
        return intVal + doubleVal;  // intVal silently becomes double
    }
    
    /**
     * NARROWING CONVERSION (Explicit Cast - Counter-clockwise)
     * Requires explicit cast, truncates without rounding
     * 
     * Algorithm: U' → F' → R' → L' → D' (double to byte)
     * Cube: Reverse solve - controlled deconstruction
     */
    public static int narrowingConversion(double doubleVal) {
        // Move: U' → L (explicit cast required)
        // CLI equivalent: head -c 4 bigfile.bin > truncated.bin
        return (int) doubleVal;  // decimal TRUNCATED, not rounded
    }
    
    /**
     * EXPRESSION EVALUATION CONTEXT
     * All operands promote to largest type present
     * 
     * Algorithm: Detect highest face, rotate all to match
     */
    public static void expressionContext() {
        byte D = 10;      // Down face
        short B = 20;     // Back face  
        int L = 30;       // Left face
        long R = 40L;     // Right face
        float F = 50.0f;  // Front face
        double U = 60.0;  // Up face
        
        // All promote to double (U face dominates)
        // Algorithm: D + B + L + R + F + U → all become U
        double result = D + B + L + R + F + U;
        
        // Without U, F dominates:
        // D + B + L + R + F → all become F (float)
        float resultNoDouble = D + B + L + R + F;
        
        // Without F or U, R dominates:
        // D + B + L + R → all become R (long)  
        long resultNoFloat = D + B + L + R;
        
        // Without R, F, U → everything becomes L (int)
        // Even byte + byte = int (JLS §5.6)
        int resultBase = D + B;  // byte + short = int (surprise!)
    }
    
    // ============================================================
    // CLI COMMANDS VECTORIZED TO CUBE MOVES
    // ============================================================
    
    /*
     * MOVE VECTOR MAPPING:
     * 
     * | Cube | Type Change      | CLI Command                    | Vector |
     * |------|------------------|--------------------------------|--------|
     * | U    | → double         | kubectl scale --replicas=max   | [0,1]  |
     * | U'   | double →         | (int) doubleVal                | [0,-1] |
     * | U2   | double ↔ double  | docker-compose up --scale=2    | [0,2]  |
     * | F    | → float          | docker build -t image .        | [1,0]  |
     * | F'   | float →          | (int) floatVal                 | [-1,0] |
     * | R    | → long           | ./script.sh &                  | [1,1]  |
     * | R'   | long →           | kill -9 $PID                   | [-1,-1]|
     * | L    | → int            | echo $?                        | [-1,1] |
     * | L'   | int →            | (byte) intVal                  | [1,-1] |
     * | B    | → short          | head -n 100 file               | [0,-1] |
     * | D    | → byte           | xxd -l 1 file                  | [0,0]  |
     * 
     * ALGORITHM FOR YOUR QUESTIONS:
     * 
     * Q1: "How does Java handle type promotion when mixing int and double?"
     * A1: Algorithm L + U → U (int + double = double)
     *     CLI: small_int | big_double_processor
     *     The smaller type ALWAYS promotes to the larger
     * 
     * Q2: "What gets truncated vs promoted automatically?"
     * A2: PROMOTED (automatic, clockwise): D→B→L→R→F→U
     *     TRUNCATED (explicit cast, counter-clockwise): U'→F'→R'→L'→B'→D'
     *     
     *     Truncation requires YOU to reverse the algorithm manually:
     *     double pi = 3.14159;
     *     int truncated = (int) pi;  // Move: U' → L (you typed the cast)
     *     // Result: 3 (not 3.14159, not rounded to 3, just CHOPPED)
     */
    
    // ============================================================
    // DEMONSTRATION
    // ============================================================
    
    public static void main(String[] args) {
        System.out.println("=== TYPE PROMOTION CUBE ALGORITHM ===\n");
        
        // Your journey from E212 to orchestration
        String[] journey = {
            "E212 errors      → D2  → byte boundaries",
            "absolute paths   → D→L → byte to int (widening)",
            "env variables    → L2  → int context mastery", 
            "shell scripts    → L→R → int to long (scaling)",
            "containers       → R→F → long to float (abstraction)",
            "orchestration    → F→U → float to double (precision)",
            "here we are      → U2  → double mastery achieved"
        };
        
        System.out.println("YOUR CLI JOURNEY AS CUBE ALGORITHM:");
        System.out.println("Scramble: L' D' B' (starting state: doubt)\n");
        
        for (int i = 0; i < journey.length; i++) {
            System.out.println("Move " + (i+1) + ": " + journey[i]);
        }
        
        System.out.println("\n=== LIVE TYPE PROMOTION DEMO ===\n");
        
        int intVal = 42;
        double doubleVal = 3.14159;
        
        System.out.println("int L = " + intVal);
        System.out.println("double U = " + doubleVal);
        System.out.println();
        
        // Widening: L + U → U
        double widened = wideningPromotion(intVal, doubleVal);
        System.out.println("L + U → U (widening): " + intVal + " + " + doubleVal + " = " + widened);
        System.out.println("Algorithm: L promoted to U automatically");
        System.out.println();
        
        // Narrowing: U' → L  
        int narrowed = narrowingConversion(doubleVal);
        System.out.println("U' → L (narrowing): (int)" + doubleVal + " = " + narrowed);
        System.out.println("Algorithm: Explicit cast required, decimal TRUNCATED");
        System.out.println();
        
        // The precision loss warning from SEI CERT NUM52-J
        int bigInt = 2147483647;  // Integer.MAX_VALUE
        float asFloat = bigInt;   // L → F promotion
        System.out.println("=== PRECISION LOSS WARNING (NUM52-J) ===");
        System.out.println("int (L): " + bigInt);
        System.out.println("→ float (F): " + asFloat);
        System.out.println("Lost precision in mantissa during L → F promotion!");
        System.out.println();
        
        System.out.println("=== SOLVE COMPLETE ===");
        System.out.println("From E212 to orchestration: Algorithm executed.");
        System.out.println("JLS §5.6 encoded. SEI CERT NUM52-J acknowledged.");
        System.out.println("The cube is solved. Ready for next scramble.");
    }
}
