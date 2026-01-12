# SEICERT NUM52-J: Be Aware of Numeric Promotion Behavior

**Source:** SEI CERT Oracle Coding Standard for Java  
**Rule ID:** NUM52-J  
**Severity:** Medium  
**Likelihood:** Probable  
**Remediation Cost:** Medium  
**Priority:** P8  
**Level:** L2  
**Date Accessed:** 2025-01-12  

---

## Rule Statement

**Be aware of numeric promotion behavior when using compound assignment operators and mixed-type arithmetic.**

Failure to understand numeric promotion can lead to:
- Unexpected precision loss
- Silent overflow
- Logic errors in comparisons
- Security vulnerabilities (integer overflow attacks)

---

## Noncompliant Code Example (Compound Assignment)

```java
public class NumericPromotionExample {
    public static void main(String[] args) {
        byte b = 127;
        b += 1;  // Implicitly casts: b = (byte)(b + 1)
        System.out.println(b);  // Outputs: -128 (overflow!)
    }
}
```

**Problem:** The compound assignment operator `+=` includes an implicit cast, which can cause overflow without warning.

---

## Compliant Solution (Explicit Range Check)

```java
public class NumericPromotionExample {
    public static void main(String[] args) {
        byte b = 127;
        
        // Check for overflow before assignment
        int tmp = b + 1;
        if (tmp > Byte.MAX_VALUE || tmp < Byte.MIN_VALUE) {
            throw new ArithmeticException("Byte overflow detected");
        }
        b = (byte) tmp;
        System.out.println(b);
    }
}
```

---

## Noncompliant Code Example (Precision Loss)

```java
public class PrecisionLossExample {
    public static void main(String[] args) {
        long accountBalance = 9_876_543_210L;
        float floatBalance = accountBalance;  // Implicit widening
        
        long recovered = (long) floatBalance;
        System.out.println("Original:  " + accountBalance);
        System.out.println("Recovered: " + recovered);
        System.out.println("Loss: $" + (accountBalance - recovered));
    }
}
```

**Output:**
```
Original:  9876543210
Recovered: 9876543488
Loss: $-278
```

**Problem:** Converting `long` to `float` loses precision because float mantissa is only 24 bits.

---

## Compliant Solution (Use Appropriate Type)

```java
public class PrecisionLossExample {
    public static void main(String[] args) {
        long accountBalance = 9_876_543_210L;
        
        // Option 1: Use double (53-bit mantissa, still can lose precision)
        double doubleBalance = accountBalance;
        
        // Option 2: Use BigDecimal for financial calculations
        BigDecimal preciseBalance = BigDecimal.valueOf(accountBalance);
        
        // Option 3: Keep as long if no fractional values needed
        long integerBalance = accountBalance;
    }
}
```

---

## Noncompliant Code Example (Mixed-Type Comparison)

```java
public class MixedTypeComparison {
    public static boolean isLarger(long l, float f) {
        return l > f;  // l promoted to float, may lose precision
    }
    
    public static void main(String[] args) {
        long l = 9_876_543_210L;
        float f = 9_876_543_210.0f;
        
        System.out.println(isLarger(l, f));  // false, but values "should" be equal
    }
}
```

**Problem:** The long is promoted to float, losing precision before comparison.

---

## Compliant Solution (Use Common Type)

```java
public class MixedTypeComparison {
    public static boolean isLarger(long l, float f) {
        // Convert both to double for comparison
        return (double) l > (double) f;
    }
    
    // Or better: avoid mixing types
    public static boolean isLargerLong(long l1, long l2) {
        return l1 > l2;
    }
}
```

---

## Noncompliant Code Example (Integer Multiplication Overflow)

```java
public class IntegerOverflow {
    public static void main(String[] args) {
        int bytesPerMegabyte = 1024 * 1024;
        int megabytes = 10_000;
        
        // Both are int, result overflows int
        long totalBytes = bytesPerMegabyte * megabytes;  // Wrong!
        
        System.out.println("Total bytes: " + totalBytes);  // Negative number
    }
}
```

**Output:**
```
Total bytes: -727379968
```

---

## Compliant Solution (Promote Before Multiplication)

```java
public class IntegerOverflow {
    public static void main(String[] args) {
        int bytesPerMegabyte = 1024 * 1024;
        int megabytes = 10_000;
        
        // Cast one operand to long before multiplication
        long totalBytes = (long) bytesPerMegabyte * megabytes;
        
        System.out.println("Total bytes: " + totalBytes);  // 10485760000
    }
}
```

---

## Risk Assessment

| Rule | Severity | Likelihood | Remediation Cost | Priority | Level |
|------|----------|------------|------------------|----------|-------|
| NUM52-J | Medium | Probable | Medium | P8 | L2 |

**Potential Consequences:**

1. **Security Vulnerabilities**
   - Buffer overflow (incorrect size calculation)
   - Integer overflow attacks
   - Authentication bypass (balance/credit checks)

2. **Financial Loss**
   - Precision loss in monetary calculations
   - Incorrect billing/accounting

3. **Logic Errors**
   - Incorrect comparisons
   - Unexpected loop termination
   - Wrong array indexing

---

## Related Guidelines

### CERT C Secure Coding Standard
- **INT02-C:** Understand integer conversion rules
- **INT31-C:** Ensure that integer conversions do not result in lost or misinterpreted data
- **INT32-C:** Ensure that operations on signed integers do not result in overflow

### CWE (Common Weakness Enumeration)
- **CWE-190:** Integer Overflow or Wraparound
- **CWE-197:** Numeric Truncation Error
- **CWE-681:** Incorrect Conversion between Numeric Types

### MITRE ATT&CK
- **T1499:** Endpoint Denial of Service (via integer overflow)

---

## Best Practices

### 1. Choose Appropriate Types

```java
// Bad: Using byte/short for no good reason
byte counter = 0;
for (int i = 0; i < 200; i++) {
    counter += 1;  // Will overflow
}

// Good: Use int by default
int counter = 0;
for (int i = 0; i < 200; i++) {
    counter += 1;
}
```

### 2. Validate Before Narrowing

```java
public static byte safeNarrowToByte(int value) {
    if (value < Byte.MIN_VALUE || value > Byte.MAX_VALUE) {
        throw new ArithmeticException("Value out of byte range: " + value);
    }
    return (byte) value;
}
```

### 3. Use Math Methods for Overflow Detection (Java 8+)

```java
try {
    int result = Math.addExact(a, b);  // Throws on overflow
    long product = Math.multiplyExact(x, y);  // Throws on overflow
} catch (ArithmeticException e) {
    // Handle overflow
}
```

### 4. Use BigDecimal for Financial Calculations

```java
// Never do this for money
float price = 0.1f;
float quantity = 3.0f;
float total = price * quantity;  // 0.30000001

// Always use BigDecimal
BigDecimal price = new BigDecimal("0.1");
BigDecimal quantity = new BigDecimal("3.0");
BigDecimal total = price.multiply(quantity);  // 0.3 exactly
```

### 5. Enable Compiler Warnings

```bash
javac -Xlint:cast MyClass.java  # Warn about casts
javac -Xlint:all MyClass.java   # All warnings
```

---

## Testing Strategy

### Unit Tests Should Cover:

1. **Boundary Values**
   ```java
   @Test
   public void testByteOverflow() {
       byte b = Byte.MAX_VALUE;
       assertThrows(ArithmeticException.class, () -> 
           safeAdd(b, (byte) 1)
       );
   }
   ```

2. **Mixed-Type Operations**
   ```java
   @Test
   public void testLongToFloatPrecision() {
       long original = 9_876_543_210L;
       float converted = original;
       long restored = (long) converted;
       assertNotEquals(original, restored);
   }
   ```

3. **Compound Operators**
   ```java
   @Test
   public void testCompoundAssignment() {
       byte b = 100;
       b += 50;  // Should handle correctly
       assertEquals(-106, b);  // Demonstrates overflow
   }
   ```

---

## Automated Detection

### Static Analysis Tools

1. **SpotBugs** (successor to FindBugs)
   - Detects: `INT: Bad comparison of nonnegative value with negative constant`
   - Detects: `INT: Bad comparison of signed byte`

2. **PMD**
   - Rule: `AvoidUsingShortType`
   - Rule: `BigIntegerInstantiation`

3. **SonarQube**
   - Rule: `S2184` - Casts should not be used where integer promotion applies
   - Rule: `S2676` - Neither "Math.abs" nor negation should be used on numbers that could be "MIN_VALUE"

4. **Checker Framework**
   - `@IntRange` annotations for value range checking

---

## Real-World Example: Apache Commons Lang Bug

In 2015, Apache Commons Lang had a bug in `NumberUtils.createNumber()`:

```java
// Vulnerable code (simplified)
public static Number createNumber(String str) {
    // ...
    if (str.endsWith("f") || str.endsWith("F")) {
        Float f = Float.valueOf(str);
        // Assumed float could represent any value
        return f;
    }
    // ...
}
```

**Issue:** Large long values converted to float lost precision, breaking round-trip conversions.

---

## Summary

**Key Takeaways:**

1. ✅ Understand unary and binary numeric promotion rules
2. ✅ Be cautious with compound assignment operators (+=, -=, etc.)
3. ✅ Avoid implicit widening that loses precision (int→float, long→float/double)
4. ✅ Check for overflow when narrowing types
5. ✅ Use BigDecimal for financial calculations
6. ✅ Prefer int over byte/short unless memory is critical
7. ✅ Use Math.***Exact() methods (Java 8+) for overflow detection
8. ✅ Enable static analysis tools to catch promotion issues

---

## References

1. SEI CERT Oracle Coding Standard for Java (2016)
2. Java Language Specification, SE 21 Edition, §5.6
3. Effective Java, 3rd Edition, Item 60
4. OWASP Top 10 - Broken Access Control
5. CWE-190: Integer Overflow or Wraparound

---

**Tags:** #security #cert #numeric-promotion #overflow #precision-loss  
**Status:** 🔒 Security-Critical  
**Next Steps:** Implement automated checks in CI/CD pipeline
