# SDET Test: Multiple Inputs

## Purpose

Verify multiple inputs are injected in order.

## Expected Output

The processed prompt should contain:

```
## Input

- input_a: Read from test-artifacts/input-a.md
- input_b: Read from test-artifacts/input-b.md
- input_c: Read from test-artifacts/input-c.md
```

## Verification Checklist

- [ ] All three inputs appear
- [ ] Order matches definition (a, b, c)
- [ ] Each has correct format