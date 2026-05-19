# SDET Test: Both Input and Output

## Purpose

Verify both Input and Output sections are injected together.

## Expected Output

The processed prompt should contain:

```
## Input

- requirement: Read from test-artifacts/requirement.md
- architecture: Read from test-artifacts/architecture.md

## Output

- design_md: Write to test-results/design.md
- impl_md: Write to test-results/impl.md
```

## Original Content

This tests both sections injected together.

## Verification Checklist

- [ ] Input section appears first
- [ ] Output section appears after Input
- [ ] Original content after both sections
- [ ] Order: Input → Output → Original