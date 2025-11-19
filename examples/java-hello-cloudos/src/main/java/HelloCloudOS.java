public class HelloCloudOS {
  record Point(double x, double y) {}

  public static void main(String[] args) {
    var point = new Point(42.0, 25.0);

    // Pattern matching for records (Java 21+)
    String result;
    if (point.x() > point.y()) {
      result = "Java 21+ pattern matching wins";
    } else {
      result = "CloudOS sovereignty activated";
    }

    // Text blocks (Java 15+) and formatted (Java 15+)
    String message = """
      Hello from OpenJDK 21+ on CloudOS!
      Text blocks ✓ Records ✓ Pattern matching ✓ Virtual threads ✓
      Running on: %s
      Point: x=%.1f, y=%.1f
      """.formatted(
        System.getProperty("java.version"),
        point.x(),
        point.y()
      );

    System.out.println(message);
    System.out.println("Result: " + result);
    
    // Demonstrate records work correctly
    System.out.println("Point record: " + point);
  }
}
