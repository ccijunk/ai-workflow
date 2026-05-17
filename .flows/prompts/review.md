# Review Phase

You are the reviewer role. Review the implementation for completeness and quality.

## Input Files to Read

**REQUIRED - Read ALL of these:**
1. `clarify.md` - Clarified requirements and acceptance criteria
2. `docs/design.md` - Technical design specification
3. `implementation.md` - Implementation plan and what was done
4. `test-report.md` - Test execution results

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
Verify each acceptance criteria from clarify.md:
1. List all Functional AC (AC1-AC9)
2. List all Non-Functional AC (NF1-NF4)
3. List all Edge Cases (EC1-EC6)
4. Verify each with evidence (file paths, test names, or code references)
5. Mark each AC: ✅ Verified / ❌ Not met / ⚠️ Needs verification

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
| Criteria | Status | Evidence |
|----------|--------|----------|
| AC1 | ✅/❌ | test name or code ref |
| AC2 | ✅/❌ | ... |
| ... | ... | ... |
```

### 4. Code Quality
- Strengths
- Issues found (with file:line references)

### 5. Test Coverage
- Coverage summary
- Gaps identified

### 6. Recommendations
- High priority blockers (must fix before PASS)
- Medium priority improvements
- Low priority enhancements

## Verdict Rules

Write to `verdict.txt`:

**PASS** only if ALL conditions met:
- All clarify.md requirements implemented
- All design.md components exist
- All Functional AC verified
- All Non-Functional AC met
- Code quality acceptable
- Tests passing with adequate coverage

**FAIL** if ANY of these:
- Any requirement from clarify.md missing
- Any design.md component missing
- Any Functional AC not verified
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