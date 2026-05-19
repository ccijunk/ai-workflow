# SDET Test: Basic Input Injection

## Purpose

Verify single input section is injected correctly.

## Expected Output

The processed prompt should contain:

```
## Input

- requirement: Read from test-artifacts/requirement.md
```

## Original Content

This is the original prompt content that should be preserved after Input section injection.

## Verification Checklist

- [ ] Input section appears at top
- [ ] Format is correct: `- key: Read from path`
- [ ] Original content preserved
- [ ] No duplicate sections