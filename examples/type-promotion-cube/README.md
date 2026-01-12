# Type Promotion Cube Algorithm

A creative educational Java program that maps Java's type promotion hierarchy to Rubik's Cube algorithms and a developer's CLI journey from beginner to mastery.

## Concept

This program demonstrates Java's numeric type promotion (JLS §5.6) using an innovative metaphor:
- **Rubik's Cube faces** represent different numeric types
- **Cube rotations** represent type conversions
- **A personal journey** from command line struggles to orchestration mastery

## Type Hierarchy ↔ Cube Mapping

```
U (Up)    = double  (highest precision, top of hierarchy)
F (Front) = float   
R (Right) = long    
L (Left)  = int     (center of most operations)
B (Back)  = short   
D (Down)  = byte    (smallest, foundation)
```

## Key Concepts Demonstrated

1. **Widening Promotion** (Automatic)
   - `byte → short → int → long → float → double`
   - Represented as clockwise cube rotations
   - No data loss (except int→float precision)

2. **Narrowing Conversion** (Explicit Cast)
   - `double → float → long → int → short → byte`
   - Represented as counter-clockwise rotations
   - Requires explicit cast, truncates values

3. **Expression Context**
   - All operands promote to largest type present
   - Demo of SEI CERT NUM52-J precision loss warning

## Building and Running

### Prerequisites
- Java 17 or higher
- Maven 3.6+

### Compile
```bash
cd examples/type-promotion-cube
mvn clean compile
```

### Run
```bash
mvn exec:java
```

Or compile and run directly:
```bash
javac src/main/java/TypePromotionCube.java
java -cp src/main/java TypePromotionCube
```

## Expected Output

The program outputs:
1. A CLI journey narrative from E212 errors to orchestration
2. Live type promotion demonstrations
3. Precision loss warnings (NUM52-J compliance)

## Educational Value

This program is designed for IT-145 Foundation in Application Development and demonstrates:
- Understanding of Java type system (JLS §5.6)
- Awareness of security concerns (SEI CERT NUM52-J)
- Creative problem-solving and conceptual mapping
- Clear code documentation practices

## Author

Dom Garza - Strategickhaos DAO LLC

## References

- Java Language Specification (JLS) §5.6 - Numeric Promotion
- SEI CERT Oracle Coding Standard for Java - NUM52-J
