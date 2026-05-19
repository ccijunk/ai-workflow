#!/bin/bash
# SDET Dry-Run Test Script
# Purpose: Run dry-run tests and verify prompt processing output

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
SDET_DIR="$SCRIPT_DIR"
WORKFLOW_DIR="$SDET_DIR"
RUN_ID="sdet-test-$(date +%Y%m%d-%H%M%S)"
RESULTS_DIR="$SDET_DIR/runs/$RUN_ID"

echo "========================================"
echo "SDET Dry-Run Test Suite"
echo "========================================"
echo ""
echo "Project Dir:  $PROJECT_DIR"
echo "SDET Dir:     $SDET_DIR"
echo "Workflow Dir: $WORKFLOW_DIR"
echo "Run ID:       $RUN_ID"
echo "Results Dir:  $RESULTS_DIR"
echo ""

# Create test artifacts
create_test_artifacts() {
    echo "Creating test artifacts..."
    mkdir -p "$SDET_DIR/test-artifacts/docs/deep"
    
    # Basic inputs
    echo "# Test Requirement" > "$SDET_DIR/test-artifacts/requirement.md"
    echo "# Test Architecture" > "$SDET_DIR/test-artifacts/architecture.md"
    echo "# Test Design" > "$SDET_DIR/test-artifacts/design.md"
    
    # Multiple inputs
    echo "# Input A" > "$SDET_DIR/test-artifacts/input-a.md"
    echo "# Input B" > "$SDET_DIR/test-artifacts/input-b.md"
    echo "# Input C" > "$SDET_DIR/test-artifacts/input-c.md"
    
    # Nested paths
    echo "# Deep Input" > "$SDET_DIR/test-artifacts/docs/deep/input.md"
    
    # Script input (for bash executor test)
    echo "# Script Input" > "$SDET_DIR/test-artifacts/script-input.md"
    
    # Section removal test
    echo "# New Input" > "$SDET_DIR/test-artifacts/new-input.md"
    
    echo "Test artifacts created in: $SDET_DIR/test-artifacts"
}

# Run dry-run and capture output
run_dry_run() {
    echo ""
    echo "Running dry-run..."
    echo ""
    
    cd "$PROJECT_DIR"
    uv run flowctl run \
        --dry-run \
        --workflow-dir "$WORKFLOW_DIR" \
        --run-id "$RUN_ID" \
        "$WORKFLOW_DIR/workflows/sdet-dry-run-test.yaml" 2>&1 | tee "$RESULTS_DIR/dry-run-output.txt"
    
    echo ""
    echo "Dry-run output saved to: $RESULTS_DIR/dry-run-output.txt"
}

# Verify test results
verify_results() {
    echo ""
    echo "========================================"
    echo "Verifying Test Results"
    echo "========================================"
    echo ""
    
    OUTPUT="$RESULTS_DIR/dry-run-output.txt"
    
    PASS=0
    FAIL=0
    
    # Test 1: Basic Input
    echo "Test 1: Basic Input Injection"
    if grep -q "requirement: Read from test-artifacts/requirement.md" "$OUTPUT"; then
        echo "  ✓ PASS: Input section injected"
        ((PASS++))
    else
        echo "  ✗ FAIL: Input section not found"
        ((FAIL++))
    fi
    
    # Test 2: Basic Output
    echo "Test 2: Basic Output Injection"
    if grep -q "output2: Write to test-results/basic-output-result.md" "$OUTPUT"; then
        echo "  ✓ PASS: Output section injected"
        ((PASS++))
    else
        echo "  ✗ FAIL: Output section not found"
        ((FAIL++))
    fi
    
    # Test 3: Multiple Inputs
    echo "Test 3: Multiple Inputs"
    if grep -q "input_a: Read from test-artifacts/input-a.md" "$OUTPUT" && \
       grep -q "input_b: Read from test-artifacts/input-b.md" "$OUTPUT" && \
       grep -q "input_c: Read from test-artifacts/input-c.md" "$OUTPUT"; then
        echo "  ✓ PASS: All inputs injected"
        ((PASS++))
    else
        echo "  ✗ FAIL: Not all inputs found"
        ((FAIL++))
    fi
    
    # Test 4: Multiple Outputs
    echo "Test 4: Multiple Outputs"
    if grep -q "design_md: Write to test-results/design.md" "$OUTPUT" && \
       grep -q "test_md: Write to test-results/test.md" "$OUTPUT" && \
       grep -q "report_md: Write to test-results/report.md" "$OUTPUT"; then
        echo "  ✓ PASS: All outputs injected"
        ((PASS++))
    else
        echo "  ✗ FAIL: Not all outputs found"
        ((FAIL++))
    fi
    
    # Test 5: Both I/O
    echo "Test 5: Both Input and Output"
    if grep -q "## Input" "$OUTPUT" && grep -q "## Output" "$OUTPUT"; then
        echo "  ✓ PASS: Both sections present"
        ((PASS++))
    else
        echo "  ✗ FAIL: Missing sections"
        ((FAIL++))
    fi
    
    # Test 6: Section Removal
    echo "Test 6: Section Removal"
    # Check that the new injected content is present
    if grep -q "new_input: Read from test-artifacts/new-input.md" "$OUTPUT"; then
        echo "  ✓ PASS: New Input section injected"
        ((PASS++))
    else
        echo "  ✗ FAIL: New Input section not found"
        ((FAIL++))
    fi
    
    # Test 7: Nested Paths
    echo "Test 7: Nested Paths"
    if grep -q "test-artifacts/docs/deep/input.md" "$OUTPUT"; then
        echo "  ✓ PASS: Nested path preserved"
        ((PASS++))
    else
        echo "  ✗ FAIL: Nested path not preserved"
        ((FAIL++))
    fi
    
    # Test 8: Bash Executor Skip (should NOT have processed prompt)
    echo "Test 8: Bash Executor Skip"
    if grep -q "test_bash_skip" "$OUTPUT" || grep -q "script-output.md" "$OUTPUT"; then
        echo "  ✓ PASS: Bash node executed"
        ((PASS++))
    else
        echo "  ✗ FAIL: Bash node not found in output"
        ((FAIL++))
    fi
    
    # Test 9: Empty I/O (should NOT have Input/Output sections for that node)
    echo "Test 9: Empty Inputs/Outputs"
    if grep -q "test_empty_io" "$OUTPUT"; then
        echo "  ✓ PASS: Empty I/O node processed"
        ((PASS++))
    else
        echo "  ✗ FAIL: Empty I/O node not found"
        ((FAIL++))
    fi
    
    # Test 10: Complex Integration
    echo "Test 10: Complex Integration"
    if grep -q "Important architectural constraints" "$OUTPUT" && \
       grep -q "Analyze all inputs" "$OUTPUT"; then
        echo "  ✓ PASS: Original content preserved"
        ((PASS++))
    else
        echo "  ✗ FAIL: Original content lost"
        ((FAIL++))
    fi
    
    echo ""
    echo "========================================"
    echo "Test Summary"
    echo "========================================"
    echo "Passed: $PASS"
    echo "Failed: $FAIL"
    echo "Run ID: $RUN_ID"
    echo "Output: $RESULTS_DIR/dry-run-output.txt"
    echo ""
    
    if [ $FAIL -eq 0 ]; then
        echo "✓ All SDET dry-run tests passed!"
        return 0
    else
        echo "✗ Some tests failed. Check output at: $RESULTS_DIR/dry-run-output.txt"
        return 1
    fi
}

# Main
main() {
    mkdir -p "$RESULTS_DIR"
    
    create_test_artifacts
    run_dry_run
    verify_results
}

main "$@"