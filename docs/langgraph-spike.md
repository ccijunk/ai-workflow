# LangGraph Spike Evaluation (30 min)

## Setup (5 min)

- LangGraph installed: `uv add langgraph`
- LangGraph is a low-level orchestration framework for agents with durable execution, streaming, human-in-the-loop, and persistence

## Findings

### Can LangGraph host subprocess-as-node?

**Yes.** LangGraph nodes are functions that receive state and return state updates:

```python
def subprocess_node(state):
    result = subprocess.run(["claude", "--prompt", state["prompt"]])
    return {"output": result.stdout}
```

This matches our executor-as-subprocess pattern cleanly.

### Conditional edges

LangGraph supports conditional edges via `add_conditional_edges`:

```python
graph.add_conditional_edges("node", lambda state: "next_a" if state["ok"] == "pass" else "next_b")
```

This maps to our `when: key == "value"` syntax, but requires translating YAML conditions to Python lambdas/functions.

### YAML-to-LangGraph mapping

**Impedance mismatch is significant:**

- YAML workflow → Python StateGraph compilation step required
- LangGraph uses `MessagesState` or custom TypedDict for state
- Our simple `context: dict[str, str]` would need adaptation
- Transitions defined imperatively (`add_edge`, `add_conditional_edges`) vs our declarative YAML

The mapping would require:
1. Parse YAML workflow
2. Generate StateGraph with nodes from `workflow.nodes`
3. Add edges from `workflow.transitions`
4. Compile graph

This is doable but adds complexity vs our ~100-line standalone runner.

### Overhead assessment

**What we gain with LangGraph:**
- Durable execution (resumability built-in)
- Human-in-the-loop (interrupts - could map to our `pause: true`)
- Persistence/checkpointing built-in
- LangSmith integration for debugging/tracing

**What we lose:**
- Direct control over state machine
- Simplicity (standalone runner is ~100 lines)
- Independence from LangChain ecosystem
- Clear YAML-to-execution mapping
- Lightweight `uvx` install footprint

**Dependency overhead:**
- langgraph + langchain-core + other LangChain deps
- Our current deps: click, pyyaml, pydantic (~3 packages)

## Go/No-Go Decision

**Decision:** NO-GO

**Reasoning:**

LangGraph CAN host subprocess-as-node, but the impedance mismatch between YAML-defined workflows and LangGraph's imperative graph construction adds unnecessary complexity for v1. Our standalone runner (~100 lines) already handles the state machine, conditional transitions, and artifact validation. LangGraph's benefits (durable execution, persistence) are deferred to later milestones per spec.

**If we need durable execution in v2:**
- Option A: Add checkpointing to standalone runner (serialize state to disk)
- Option B: Migrate to LangGraph then (workflow YAML format stays same, just change runtime)

**Continue with standalone runner.**