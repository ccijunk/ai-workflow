# BA — Clarify Domain Model

## Role
Read your role prompt and learned heuristics from `memory/ba.md`.

## Task
Given the issue and requirement, produce `clarify.md` with:

**Problem statement:** One paragraph in business terms describing what the software must do.

**Domain entities:** Table with columns: entity name | brief definition | key attributes

**Business rules:** Numbered list. Each rule must be independently statable. Flag contradictions explicitly.

**Lifecycle coverage:** Table with columns: Phase | Key events | Rules that apply | Exit condition
- All four rows required: Create, Operate, Edge case, Terminate

**Bounded contexts:** Domain partitions and their interfaces. "N/A — single context" is valid.

**Acceptance criteria:** Given/When/Then format. One criterion per lifecycle phase.

**Open questions:** Unresolved business questions for architect to evaluate.

## Feedback (if retry)
If `domain-review.md` and `reject-reason.txt` are provided, address the specific issues raised. Re-evaluate your domain model against the feedback.