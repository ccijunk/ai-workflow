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


def run_workflow(
    workflow: WorkflowDef,
    run_dir: Path,
    adapter: ExecutorAdapter | None = None,
    dry_run: bool = False,
) -> dict[str, str]:
    adapter = adapter or EchoAdapter()
    context: dict[str, str] = {}
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

        inp = ExecutorInput(
            role=node_def.role,
            prompt_path=node_def.prompt,
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
    }
    for key, path_str in node_def.outputs.items():
        artifact_path = inp.run_dir / path_str
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        mock_val = mock_values.get(key, f"mock: {key}")
        artifact_path.write_text(mock_val)
        outputs[key] = mock_val
    return ExecutorResult(outputs=outputs, returncode=0, stdout="[dry-run]", stderr="")