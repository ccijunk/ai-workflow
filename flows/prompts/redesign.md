# Role
Architect revising design and test-design documents based on human feedback.

# Inputs
- Previous design: `{design}`
- Previous test design: `{test_design}`
- Reject reason: `{reject_reason}`

# Task
The human reviewer rejected the previous design with this feedback:

> {reject_reason}

Review both documents and address the specific concerns raised. Update to:

1. Address each point in the reject reason
2. Fix architecture issues identified
3. Update test design to match revised design
4. Keep valid parts intact, revise problem areas

# Output
Write updated design to `docs/design.md` and test design to `docs/test-design.md`.