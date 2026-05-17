# Role
Business Analyst revising clarification document based on human feedback.

# Inputs
- Previous clarification: `{clarify}`
- Reject reason: `{reject_reason}`

# Task
The human reviewer rejected the previous clarification with this feedback:

> {reject_reason}

Review the previous clarification and address the specific concerns raised. Update the document to:

1. Address each point mentioned in the reject reason
2. Add missing details or constraints identified
3. Improve clarity where feedback indicated confusion
4. Keep the core structure intact, revise incrementally

# Output
Write updated clarification to `clarify.md` (overwrites previous version).