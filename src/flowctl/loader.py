from pathlib import Path
import yaml
from .models import WorkflowDef


def load_workflow(path: str | Path) -> WorkflowDef:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Workflow file not found: {path}")
    raw = yaml.safe_load(p.read_text())
    if raw is None:
        raise ValueError(f"Workflow file is empty: {path}")
    if "transitions" in raw:
        for t in raw["transitions"]:
            if "from" in t:
                t["from_"] = t.pop("from")
    return WorkflowDef.model_validate(raw)


def validate_workflow(wf: WorkflowDef) -> list[str]:
    errors: list[str] = []
    for t in wf.transitions:
        if t.from_ not in wf.nodes and t.from_ != "__start__":
            errors.append(f"Transition from '{t.from_}' references unknown node")
        if t.to not in wf.nodes and t.to != "__end__":
            errors.append(f"Transition to '{t.to}' references unknown node")
    has_start = any(t.from_ == "__start__" for t in wf.transitions)
    if not has_start:
        errors.append("No __start__ transition found")
    has_end = any(t.to == "__end__" for t in wf.transitions)
    if not has_end:
        errors.append("No __end__ transition found (workflow may loop forever)")
    return errors