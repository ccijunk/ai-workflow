from pathlib import Path


def validate_artifacts(outputs: dict[str, str], run_dir: Path) -> list[str]:
    errors: list[str] = []
    for key, path_str in outputs.items():
        p = Path(path_str)
        if not p.is_absolute():
            p = run_dir / p
        if not p.exists():
            errors.append(f"Output '{key}' missing: {p}")
        elif p.stat().st_size == 0:
            errors.append(f"Output '{key}' is empty: {p}")
    return errors