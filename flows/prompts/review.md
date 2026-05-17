# Review Phase

You are the reviewer role. Review the implementation for completeness and quality.

## Input Files to Read

**REQUIRED - Read ALL of these:**
1. `clarify.md` - Clarified requirements and acceptance criteria
2. `docs/design.md` - Technical design specification
3. `implementation.md` - Implementation plan and what was done
4. `test-report.md` - Test execution results
5. `code-diff.diff` - Actual git diff of changes made

## Critical: Verify Actual Files

**MANDATORY**: Use the Read tool to verify claims in implementation.md.
DO NOT trust implementation.md at face value.

For each file claimed in implementation.md:
1. Use Read tool to open the actual file
2. Verify the code exists as described
3. Check file paths match what's in code-diff.diff

If you do not read actual files and diff, your review is INCOMPLETE.

## Task

### Phase 1: Requirements Coverage Check
Compare clarify.md requirements to actual implementation:
1. List all requirements from clarify.md (Sub-Requirements sections)
2. Check if each requirement is implemented
3. Identify MISSING requirements
4. Mark each requirement: ✅ Implemented / ❌ Missing / ⚠️ Partial

### Phase 2: Design Consistency Check
Compare docs/design.md to actual implementation:
1. List all components/files specified in design.md
2. Check if each component exists and matches design
3. Identify DEVIATIONS from design
4. Mark each design element: ✅ Matches / ❌ Missing / ⚠️ Deviates

### Phase 3: Acceptance Criteria Check

**IMPORTANT**: clarify.md may use different section names. Look for:
- "Acceptance Criteria" section with criteria entries
- Any table with criteria/requirements
- Functional, Non-Functional, and Edge Case markers if present

For each criteria found in clarify.md:
1. Verify it with evidence (file paths, test names, or code references)
2. Mark: ✅ Verified / ❌ Not met / ⚠️ Needs verification

DO NOT assume AC1-AC9, NF1-NF4, EC1-EC6 format.
Read the actual clarify.md and extract criteria from whatever format it uses.

### Phase 4: Code Quality Check
Review the actual code changes:
1. Security implementation
2. Error handling
3. Code organization
4. Integration quality
5. Best practices

### Phase 5: Test Coverage Check
Review test-report.md:
1. Overall coverage percentage
2. Coverage for new code specifically
3. Missing test scenarios
4. Edge case coverage

### Phase 6: Security Check

Review for security issues:

1. **Secrets/Credentials**: No hardcoded passwords, API keys, tokens
2. **Input Validation**: All user inputs validated/sanitized
3. **SQL Injection**: Parameterized queries used (not string concatenation)
4. **XSS Prevention**: Output encoding applied where needed
5. **Auth/Authz**: Proper access controls implemented
6. **Data Exposure**: No sensitive data in logs/responses

For each category, mark: ✅ Secure / ❌ Vulnerable / ⚠️ Needs Review

## Output Format

Write to `review.md` with sections:

### 1. Requirements Coverage
```
| Requirement Section | Status | Evidence |
|---------------------|--------|----------|
| 1. Core Executor | ✅/❌ | file path or test |
| 2. Model Changes | ✅/❌ | ... |
| ... | ... | ... |
```

### 2. Design Consistency
```
| Design Element | Status | Deviation Description |
|----------------|--------|-----------------------|
| BashExecutor class | ✅/❌/⚠️ | ... |
| Scripts directory | ✅/❌/⚠️ | ... |
| ... | ... | ... |
```

### 3. Acceptance Criteria
```
| Criteria ID | Status | Evidence |
|-------------|--------|----------|
| [from clarify.md] | ✅/❌/⚠️ | test name or code ref |
| [from clarify.md] | ✅/❌/⚠️ | ... |
| ... | ... | ... |
```

### 4. Code Quality
- Strengths
- Issues found (with file:line references)

### 5. Test Coverage
- Coverage summary
- Gaps identified

### 6. Security
```
| Category | Status | Notes |
|----------|--------|-------|
| Secrets/Credentials | ✅/❌/⚠️ | ... |
| Input Validation | ✅/❌/⚠️ | ... |
| SQL Injection | ✅/❌/⚠️ | ... |
| XSS Prevention | ✅/❌/⚠️ | ... |
| Auth/Authz | ✅/❌/⚠️ | ... |
| Data Exposure | ✅/❌/⚠️ | ... |
```

### 7. Recommendations
- High priority blockers (must fix before PASS)
- Medium priority improvements
- Low priority enhancements

## Verdict Rules

Write to `verdict.txt`:

**PASS** only if ALL conditions met:
- All clarify.md requirements implemented
- All design.md components exist
- All acceptance criteria verified
- Code quality acceptable
- Tests passing with adequate coverage

**FAIL** if ANY of these:
- Any requirement from clarify.md missing
- Any design.md component missing
- Any acceptance criteria not verified
- Critical code quality issue
- Tests failing

**PARTIAL** if:
- Some requirements missing but core functionality works
- Minor deviations from design
- Edge cases not fully covered

## Critical Check

Before writing verdict, ask yourself:
- Did I read ALL input files?
- Did I verify implementation matches design?
- Did I check every acceptance criteria?
- Did I look at actual files (not just implementation.md claims)?

If any answer is NO, you did not complete the review properly.