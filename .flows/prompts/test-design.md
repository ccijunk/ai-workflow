# Test-Architect — Design Test Strategy

## Role
Read your role prompt and learned heuristics from `memory/test-arch.md`.

## Task
Given the design and clarify, produce `test-design.md` with:

**Test strategy:** Unit/integration/E2E scope and ownership. Developer owns unit tests (TDD). Test-developer owns integration + E2E.

**Feature test cases:** Table: ID | scenario | precondition | action | expected outcome | owner (developer/test-developer)

**Regression suite:** Table: ID | repo-relative file path | runner command | trigger

**Edge cases and failure scenarios:** Boundary conditions not in feature test cases.

**Test tooling:** Frameworks and runners. Version-pinned.

## Testability verification
Confirm design passes all three criteria:
1. Every aggregate has at least one observable output (state or event)
2. No direct cross-context dependency without declared interface
3. Every external side-effect is injectable or replaceable