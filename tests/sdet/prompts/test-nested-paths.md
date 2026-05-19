# SDET Test: Nested Paths

## Purpose

Verify nested file paths are preserved in Input/Output sections.

## Expected Output

The processed prompt should contain:

```
## Input

- deep_input: Read from test-artifacts/docs/deep/input.md

## Output

- deep_output: Write to test-results/docs/deep/output.md
```

## Verification Checklist

- [ ] Nested input path preserved (docs/deep/)
- [ ] Nested output path preserved
- [ ] No path flattening or simplification