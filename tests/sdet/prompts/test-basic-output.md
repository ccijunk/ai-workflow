# SDET Test: Basic Output Injection

## Purpose

Verify single output section is injected correctly.

## Expected Output

The processed prompt should contain:

```
## Output

- output2: Write to test-results/basic-output-result.md
```

## Original Content

This prompt tests output injection without inputs.

## Verification Checklist

- [ ] Output section appears
- [ ] Format is correct: `- key: Write to path`
- [ ] Original content preserved