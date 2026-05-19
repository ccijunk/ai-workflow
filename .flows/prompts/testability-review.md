# Human — Testability Review Gate

## Task
Review `design.md` for testability:

**Testability criteria (all three must pass):**
1. Every aggregate has at least one observable output (state or event)
2. No direct cross-bounded-context dependency without declared interface
3. Every external side-effect (network, file, DB write) is injectable or replaceable

**Review checklist:**
- Check DDD structure table for observable outputs per aggregate
- Check system architecture for cross-context dependencies
- Check integration points for injectable/replaceable side-effects

## Outputs
Write two files:

**testability-review.md** — Your review notes documenting:

**Criteria evaluation table:**
| Criterion | Status (pass/fail) | Evidence or gap |

**Issues:** Numbered list of failing criteria with location in design.md

**verdict.txt** — First line must be exactly:
- `APPROVED` — design is testable, proceed to test_arch
- `BLOCKED` — testability issues require architect revision

## Reject Reason
If BLOCKED, also use CLI flag:
```bash
flowctl run --resume --reject --reject-reason "<specific testability issues>"
```