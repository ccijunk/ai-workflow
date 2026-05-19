# SDET Test: Section Removal

## Purpose

Verify old manual Input/Output sections are removed and replaced.

## Input

THIS IS OLD MANUAL INPUT - SHOULD BE REMOVED.
This content must not appear in processed prompt.

## Output

THIS IS OLD MANUAL OUTPUT - SHOULD BE REMOVED.
This content must not appear in processed prompt.

## Original Content

This section should be preserved.

## Expected Output

Processed prompt should NOT contain:
- "THIS IS OLD MANUAL INPUT"
- "SHOULD BE REMOVED"

Processed prompt SHOULD contain:
- "## Input" with new_input from definition
- "## Output" with new_output from definition
- "This section should be preserved"

## Verification Checklist

- [ ] Old Input section completely removed
- [ ] Old Output section completely removed
- [ ] New Input section injected
- [ ] New Output section injected
- [ ] Other sections preserved