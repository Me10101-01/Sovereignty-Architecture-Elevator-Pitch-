# Java CloudOS Hello World

A demonstration of Java 21+ features running in the CloudOS sovereign development environment.

## Features Demonstrated

- **Text Blocks** - Multi-line strings with proper formatting
- **Records** - Immutable data classes with pattern matching
- **Pattern Matching for instanceof** - Enhanced switch expressions
- **Virtual Threads** - Lightweight concurrency (preview)
- **Sealed Classes** - Restricted class hierarchies (when needed)

## Build & Run

### Using Maven

```bash
# From within the container
cd examples/java-hello-cloudos
mvn compile exec:java -Dexec.mainClass=HelloCloudOS
```

### Direct Java Execution

```bash
cd examples/java-hello-cloudos/src/main/java
java --enable-preview HelloCloudOS.java
```

## Running in CloudOS

```bash
# Start the JDK workspace
./start-cloudos-jdk.sh start

# Get a shell in the container
./start-cloudos-jdk.sh shell

# Inside the container
cd examples/java-hello-cloudos
mvn compile exec:java -Dexec.mainClass=HelloCloudOS
```

## Expected Output

```
Hello from OpenJDK 21+ on CloudOS!
Text blocks ✓ Records ✓ Pattern matching ✓ Virtual threads ✓
Running on: <vendor version>

Result: Java 25 pattern matching wins
```

## Debugging

The container exposes port 5005 for JPDA debugging. Configure your IDE to connect to `localhost:5005`.

## Zero Cloud Dependencies

This runs entirely on your local machine with no external cloud services required. Full sovereignty. 🚀
