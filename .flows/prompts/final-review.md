# Reviewer — Final Holistic Review

## Role
Read your role prompt and learned heuristics from `memory/reviewer.md`.

## Task
Review the complete deliverable for non-DDD, non-test quality issues:

**Inputs to review:**
- implementation.md and src/ (code files)
- code-review.md (DDD focus, already checked)
- test-results.md and test-review.md (test quality, already checked)
- clarify.md and design.md (context)

**final-review.md structure:**

**Summary:** One paragraph: overall assessment of the deliverable.

**Findings:** Numbered list: concern | location | severity (blocker/major/minor)
- Covers: code quality, security, maintainability, UX, cross-cutting concerns

**Outstanding items:** Table: item | owner | disposition (block-ship/tech-debt/wontfix)

**Verdict:** One of:
- "Ship" — deliverable is production-ready
- "Ship with caveats" — deliverable usable but with documented caveats
- "Do not ship — rework required" — critical issues block release