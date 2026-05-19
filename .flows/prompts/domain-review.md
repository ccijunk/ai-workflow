# Human — Domain Review Gate

## Task
Review `clarify.md` for:

**Domain model quality:**
- Contradictory business rules (rules that cannot both be true)
- Incomplete lifecycle coverage (missing phases)
- Non-orthogonal domain entities (overlapping responsibility)
- Missing bounded context interfaces (undeclared cross-context dependencies)

**Review criteria:**
1. Each business rule independently testable
2. Lifecycle table has all four rows
3. Domain entities have clear, non-overlapping scope
4. Bounded contexts declared with interfaces

## Outputs
Write two files:

**domain-review.md** — Your review notes documenting:
- Issues found (if any)
- What passed review
- Specific feedback for BA

**verdict.txt** — First line must be exactly:
- `APPROVED` — domain model is sound, proceed to architect
- `BLOCKED` — issues require BA revision

## Reject Reason
If BLOCKED, also use CLI flag:
```bash
flowctl run --resume --reject --reject-reason "<specific issues>"
```

This writes `reject-reason.txt` for BA to read on retry.