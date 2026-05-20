from pathlib import Path


def _parse_prefix(filename: str) -> tuple[str, str]:
    """Extract prefix and relative path from filename."""
    if filename.startswith("workflow:"):
        return "workflow", filename[len("workflow:"):]
    elif filename.startswith("repo:"):
        return "repo", filename[len("repo:"):]
    elif filename.startswith("run:"):
        return "run", filename[len("run:"):]
    else:
        return "run", filename


def _resolve_path(
    filename: str,
    run_dir: Path,
    workflow_dir: Path | None = None,
    repo_dir: Path | None = None,
) -> Path:
    """Resolve file path based on prefix."""
    prefix, rel_path = _parse_prefix(filename)
    
    if prefix == "workflow":
        base_dir = workflow_dir
    elif prefix == "repo":
        base_dir = repo_dir
    else:
        base_dir = run_dir
    
    if base_dir:
        return base_dir / rel_path
    return run_dir / rel_path


def validate_artifacts(
    outputs: dict[str, str],
    run_dir: Path,
    workflow_dir: Path | None = None,
    repo_dir: Path | None = None,
) -> list[str]:
    """Validate output artifacts exist at resolved paths."""
    errors: list[str] = []
    for key, filename in outputs.items():
        resolved_path = _resolve_path(filename, run_dir, workflow_dir, repo_dir)
        
        if not resolved_path.exists():
            errors.append(f"Output '{key}' missing: {resolved_path}")
        elif resolved_path.stat().st_size == 0:
            errors.append(f"Output '{key}' is empty: {resolved_path}")
    return errors