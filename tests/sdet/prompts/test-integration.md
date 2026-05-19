# SDET Test: Complex Integration

## Purpose

Full integration test with multiple inputs, outputs, and nested content.

## Notes

Important architectural constraints:
- Must follow project structure
- Must include tests

## Task

1. Analyze all inputs
2. Create implementation
3. Write tests
4. Document decisions

## Expected Output

Processed prompt should contain:

```
## Input

- requirement: Read from test-artifacts/requirement.md
- architecture: Read from test-artifacts/architecture.md
- design: Read from test-artifacts/design.md

## Output

- impl_md: Write to test-results/impl.md
- test_md: Write to test-results/test.md
- docs_md: Write to test-results/docs.md

# SDET Test: Complex Integration

## Notes
...
## Task
...
```

## Verification Checklist

- [ ] Three inputs injected in order
- [ ] Three outputs injected in order
- [ ] Notes section preserved
- [ ] Task section preserved
- [ ] All content present