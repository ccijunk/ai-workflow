from pathlib import Path
from .models import WorkflowDef
from .executors import ExecutorAdapter, EchoAdapter
from .executors.base import ExecutorInput, ExecutorResult
from .artifact_validator import validate_artifacts
from .logger import WorkflowLogger
from .state import save_state, load_state, has_state, clear_state

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
            if actual and actual.strip().split('\n')[0] == expected:
                results.append(t.to)
            continue
        results.append(t.to)
    return results


def run_workflow(
    workflow: WorkflowDef,
    run_dir: Path,
    adapter: ExecutorAdapter | None = None,
    dry_run: bool = False,
    initial_context: dict[str, str] | None = None,
    workflow_dir: Path | None = None,
    log_level: str = "INFO",
    log_format: str = "json",
    resume: bool = False,
) -> dict[str, str]:
    adapter = adapter or EchoAdapter()
    context: dict[str, str] = initial_context or {}
    current = "__start__"
    iterations = 0
    
    run_id = run_dir.name
    logger = WorkflowLogger(run_id, run_dir, log_level, log_format)
    logger.log_workflow_start(workflow=str(workflow_dir) if workflow_dir else "unknown", executor=adapter.__class__.__name__, initial_context=initial_context)

    if resume and has_state(run_dir):
        state = load_state(run_dir)
        if state:
            current = state.current_node
            context = state.context
            iterations = state.iterations

    run_dir.mkdir(parents=True, exist_ok=True)

    while current != "__end__":
        iterations += 1
        if iterations > MAX_ITERATIONS:
            raise RuntimeError(f"Workflow exceeded {MAX_ITERATIONS} iterations - possible cycle")

        next_nodes = get_next_transitions(workflow, current, context)
        if not next_nodes:
            logger.log_error(RuntimeError(f"No valid transitions from '{current}'"))
            raise RuntimeError(f"No valid transitions from '{current}'")

        next_node = next_nodes[0]

        for i, candidate in enumerate([t for t in workflow.transitions if t.from_ == current]):
            logger.log_transition(current, candidate.to, candidate.when, matched=(i == 0))

        if next_node == "__end__":
            break

        node_def = workflow.nodes.get(next_node)
        if not node_def:
            logger.log_error(RuntimeError(f"Node '{next_node}' not found"))
            raise RuntimeError(f"Node '{next_node}' not found in workflow definition")

        inp = ExecutorInput(
            role=node_def.role,
            prompt_path=node_def.prompt,
            skill_paths=node_def.skills,
            inputs=node_def.inputs,
            outputs=node_def.outputs,
            run_dir=run_dir,
            workflow_dir=workflow_dir,
        )

        logger.log_node_start(next_node, node_def.role, node_def.prompt, node_def.skills, node_def.inputs)

        if dry_run:
            result = _mock_execution(inp, node_def)
        else:
            result = adapter.execute(inp)

        errors = validate_artifacts(node_def.outputs, run_dir)
        logger.log_validation(next_node, errors)
        
        if errors and not dry_run:
            logger.log_node_failure(next_node, RuntimeError(f"Artifact validation failed: {'; '.join(errors)}"))
            raise RuntimeError(f"Artifact validation failed: {'; '.join(errors)}")

        logger.log_node_end(next_node, "completed", result.outputs)

        if result.outputs:
            context.update(result.outputs)

        current = next_node
        
        if not dry_run:
            save_state(run_dir, current, context, iterations)

    clear_state(run_dir)

    logger.log_workflow_end("completed")
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