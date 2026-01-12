#!/bin/bash
# Comprehensive Phase 11 Integration Test

echo "=========================================="
echo "Phase 11 Integration Test Suite"
echo "=========================================="
echo ""

PASSED=0
FAILED=0

# Test 1: YAML Validation
echo "[Test 1] YAML Configuration Validation"
python3 -c "import yaml; yaml.safe_load(open('configs/thought_log.yaml'))" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ PASSED: thought_log.yaml is valid"
    PASSED=$((PASSED + 1))
else
    echo "  ✗ FAILED: thought_log.yaml validation failed"
    FAILED=$((FAILED + 1))
fi
echo ""

# Test 2: JSON Configuration Validation
echo "[Test 2] JSON Configuration Validation"
python3 -c "import json; json.load(open('configs/cube_mappings.json')); json.load(open('configs/oop_hierarchy.json'))" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ PASSED: JSON configs are valid"
    PASSED=$((PASSED + 1))
else
    echo "  ✗ FAILED: JSON validation failed"
    FAILED=$((FAILED + 1))
fi
echo ""

# Test 3: Thought-Log Overlay Module
echo "[Test 3] Thought-Log Overlay Module"
cd src/register_memory
python3 -c "from thought_log_overlay import ThoughtLogOverlay; t = ThoughtLogOverlay(); print('Module loaded')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ PASSED: Thought-log overlay module loads"
    PASSED=$((PASSED + 1))
else
    echo "  ✗ FAILED: Module import failed"
    FAILED=$((FAILED + 1))
fi
cd ../..
echo ""

# Test 4: Reference Parity Checker Module
echo "[Test 4] Reference Parity Checker Module"
cd src/entanglement_core
python3 -c "from reference_parity_checker import ReferenceParityChecker; c = ReferenceParityChecker(); print('Module loaded')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ PASSED: Reference parity checker module loads"
    PASSED=$((PASSED + 1))
else
    echo "  ✗ FAILED: Module import failed"
    FAILED=$((FAILED + 1))
fi
cd ../..
echo ""

# Test 5: Bloom Wave Cores Module
echo "[Test 5] Bloom Wave Cores Module"
cd src/alu
python3 -c "from bloom_wave_cores import BloomWaveCores; b = BloomWaveCores(); print('Module loaded')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ PASSED: Bloom wave cores module loads"
    PASSED=$((PASSED + 1))
else
    echo "  ✗ FAILED: Module import failed"
    FAILED=$((FAILED + 1))
fi
cd ../..
echo ""

# Test 6: Cognitive Cube Spec Module
echo "[Test 6] Cognitive Cube Spec Module"
cd src/cube_simulator
python3 -c "from cognitive_cube_spec import CognitiveCubeSpec; c = CognitiveCubeSpec(); print('Module loaded')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ PASSED: Cognitive cube spec module loads"
    PASSED=$((PASSED + 1))
else
    echo "  ✗ FAILED: Module import failed"
    FAILED=$((FAILED + 1))
fi
cd ../..
echo ""

# Test 7: Type Promotion Cube Integration
echo "[Test 7] Type Promotion Cube Integration"
cd src/cube_simulator
timeout 10 python3 type_promotion_cube.py > /tmp/test_output.txt 2>&1
if [ $? -eq 0 ] && grep -q "Phase 11 demonstration complete" /tmp/test_output.txt; then
    echo "  ✓ PASSED: Integration demo runs successfully"
    PASSED=$((PASSED + 1))
else
    echo "  ✗ FAILED: Integration demo failed"
    FAILED=$((FAILED + 1))
fi
cd ../..
echo ""

# Test 8: CLI Journey Sequencer
echo "[Test 8] CLI Journey Sequencer"
cd src/cube_simulator
timeout 10 python3 cli_journey_sequencer.py --all --quiet > /tmp/test_sequencer.txt 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ PASSED: Build sequencer completes all phases"
    PASSED=$((PASSED + 1))
else
    echo "  ✗ FAILED: Build sequencer failed"
    FAILED=$((FAILED + 1))
fi
cd ../..
echo ""

# Summary
echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "Total:  $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✓ All tests passed!"
    exit 0
else
    echo "✗ Some tests failed"
    exit 1
fi
