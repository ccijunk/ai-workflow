# SDET Test: Multiple Outputs

## Purpose

Verify multiple outputs are injected in order.

## Expected Output

The processed prompt should contain:

```
## Output

- design_md: Write to test-results/design.md
- test_md: Write to test-results/test.md
- report_md: Write to test-results/report.md
```

## Verification Checklist

- [ ] All three outputs appear
- [ ] Order matches definition
- [ ] Each has correct format