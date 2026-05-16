from pathlib import Path
from .models import WorkflowDef
from .executors import ExecutorAdapter, EchoAdapter
from .executors.base import ExecutorInput, ExecutorResult
from .artifact_validator import validate_artifacts

MAX_ITERATIONS = 100


def get_next_transitions(workflow: WorkflowDef, current: str, context: dict) -> list[str]:
    candidates = [t for t in workflow.transitions if t.from_ == current]
    if not candidates:
        return []
    results = []
    for t in candidates:
        if t.when:
            key, _, val = t.when.partition(" == ")
            key = key.strip()
            expected = val.strip().strip('"\'')
            actual = context.get(key)
            if actual == expected:
                results.append(t.to)
            continue
        results.append(t.to)
    return results


def _resolve_prompt(workflow: WorkflowDef, node_def, node_name: str) -> str:
    """
    Resolve prompt for a node in the following order:
    1. Node's explicit prompt
    2. Role binding prompt (if binding exists for this node)
    3. Role's default prompt
    4. Error if no prompt found
    """
    if node_def.prompt:
        return node_def.prompt

    if workflow.roles and node_def.role in workflow.roles:
        role_config = workflow.roles[node_def.role]
        if role_config.bindings and node_name in role_config.bindings:
            binding = role_config.bindings[node_name]
            if binding.prompt:
                return binding.prompt
        if role_config.default_prompt:
            return role_config.default_prompt

    raise RuntimeError(
        f"No prompt found for node '{node_name}' with role '{node_def.role}'. "
        f"Specify a prompt on the node, add a role binding, or set a default_prompt on the role."
    )


def run_workflow(
    workflow: WorkflowDef,
    run_dir: Path,
    adapter: ExecutorAdapter | None = None,
    dry_run: bool = False,
    initial_context: dict[str, str] | None = None,
) -> dict[str, str]:
    adapter = adapter or EchoAdapter()
    context: dict[str, str] = initial_context or {}
    current = "__start__"
    iterations = 0

    while current != "__end__":
        iterations += 1
        if iterations > MAX_ITERATIONS:
            raise RuntimeError(f"Workflow exceeded {MAX_ITERATIONS} iterations - possible cycle")

        next_nodes = get_next_transitions(workflow, current, context)
        if not next_nodes:
            raise RuntimeError(f"No valid transitions from '{current}'")

        next_node = next_nodes[0]
        # v1 limitation: only first transition used; multiple branches not supported

        if next_node == "__end__":
            break

        node_def = workflow.nodes.get(next_node)
        if not node_def:
            raise RuntimeError(f"Node '{next_node}' not found in workflow definition")

        prompt_path = _resolve_prompt(workflow, node_def, next_node)

        inp = ExecutorInput(
            role=node_def.role,
            prompt_path=prompt_path,
            skill_paths=node_def.skills,
            inputs=node_def.inputs,
            outputs=node_def.outputs,
            run_dir=run_dir,
        )

        if dry_run:
            result = _mock_execution(inp, node_def)
        else:
            result = adapter.execute(inp)

        errors = validate_artifacts(node_def.outputs, run_dir)
        if errors and not dry_run:
            raise RuntimeError(f"Artifact validation failed: {'; '.join(errors)}")

        if result.outputs:
            context.update(result.outputs)

        current = next_node

    return context


def _mock_execution(inp: ExecutorInput, node_def) -> ExecutorResult:
    outputs = {}
    mock_values = {
        "pass": "yes",
        "verdict": "PASS",
        "ok": "pass",
        "clarify_approved": "yes",
        "design_approved": "yes",
        "requirement": "mock requirement: add role binding config, add role prompt",
        "pr_url": "https://github.com/ccijunk/ai-workflow/pull/1",
    }
    for key, path_str in node_def.outputs.items():
        artifact_path = inp.run_dir / path_str
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        mock_val = mock_values.get(key, f"mock: {key}")
        artifact_path.write_text(mock_val)
        outputs[key] = mock_val
    return ExecutorResult(outputs=outputs, returncode=0, stdout="[dry-run]", stderr="")