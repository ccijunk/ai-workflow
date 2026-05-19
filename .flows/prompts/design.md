# Architect — Design Architecture

## Role
Read your role prompt and learned heuristics from `memory/architect.md`.

## Task
Given the clarified domain model, produce `design.md` with:

**DDD structure:** Table: name | type (aggregate/entity/value object/domain service) | responsibility | bounded context

**System architecture:** Layer structure (domain/application/infrastructure/interface). ASCII diagram acceptable. Major components and relationships.

**Technology choices:** Table: concern | choice | justification | rejected alternative

**Integration points:** External systems, APIs, event buses, queues. "None" is valid but must be stated.

**Trade-offs made:** Explicit list: what was sacrificed and why. At least one entry required.

**Open questions for test-arch and developer:** Unknowns to resolve downstream.

## Feedback (if retry)
If `testability-review.md` and `reject-reason.txt` are provided, address the testability issues raised. Ensure all three criteria pass: observable outputs, declared interfaces, injectable side-effects.