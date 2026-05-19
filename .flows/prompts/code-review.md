# Human — Code Review Gate (DDD Focus)

## Task
Review implementation for DDD adherence:

**DDD review criteria:**
- Bounded context integrity (no domain logic leakage across boundaries)
- Aggregate invariant enforcement (aggregates protect their consistency)
- Domain logic placement (domain layer, not infrastructure)

**Review focus:**
- Check `implementation.md` Code structure for layer boundaries
- Check src/ files for domain logic placement
- Compare against design.md DDD structure

**NOT your focus:**
- General code quality (final_review handles)
- Test coverage (test_arch_test_review handles)
- Security issues (final_review handles)

## Outputs
Write two files:

**code-review.md** — Your review notes documenting:

**DDD adherence assessment:** One paragraph: bounded context integrity, aggregate invariant enforcement, domain logic placement.

**Findings:** Numbered list: location (file:line) | issue | severity (blocker/major/minor)
- Scope: DDD violations only

**verdict.txt** — First line must be exactly:
- `APPROVED` — implementation preserves DDD integrity
- `BLOCKED` — DDD violations require developer revision

## Reject Reason
If BLOCKED, also use CLI flag:
```bash
flowctl run --resume --reject --reject-reason "<specific DDD violations>"
```