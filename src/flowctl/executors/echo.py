from pathlib import Path
from .base import ExecutorAdapter, ExecutorInput, ExecutorResult


class EchoAdapter(ExecutorAdapter):
    def _parse_prefix(self, filename: str) -> tuple[str, str]:
        """Extract prefix and relative path from filename."""
        if filename.startswith("workflow:"):
            return "workflow", filename[len("workflow:"):]
        elif filename.startswith("repo:"):
            return "repo", filename[len("repo:"):]
        elif filename.startswith("run:"):
            return "run", filename[len("run:"):]
        else:
            return "run", filename

    def _resolve_path(self, filename: str, inp: ExecutorInput) -> Path:
        """Resolve file path based on prefix."""
        prefix, rel_path = self._parse_prefix(filename)
        
        if prefix == "workflow":
            base_dir = inp.workflow_dir
        elif prefix == "repo":
            base_dir = inp.repo_dir
        else:
            base_dir = inp.run_dir
        
        if base_dir:
            return base_dir / rel_path
        return inp.run_dir / rel_path

    def execute(self, inp: ExecutorInput) -> ExecutorResult:
        stdout_lines = [
            f"Role: {inp.role}",
            f"Prompt Path: {inp.prompt_path}",
            "",
            "=" * 60,
            "PROCESSED PROMPT",
            "=" * 60,
            inp.prompt,
            "=" * 60,
            "",
            "=" * 60,
            "RESOLVED PATHS",
            "=" * 60,
        ]
        
        if inp.inputs:
            stdout_lines.append("Inputs:")
            for key, filename in inp.inputs.items():
                resolved = self._resolve_path(filename, inp)
                stdout_lines.append(f"  {key}: {filename} -> {resolved}")
        
        if inp.outputs:
            stdout_lines.append("Outputs:")
            for key, filename in inp.outputs.items():
                resolved = self._resolve_path(filename, inp)
                stdout_lines.append(f"  {key}: {filename} -> {resolved}")
        
        stdout_lines.append("=" * 60)
        
        outputs = {}
        for key, filename in inp.inputs.items():
            resolved = self._resolve_path(filename, inp)
            if resolved.exists():
                outputs[key] = resolved.read_text()
        
        for key, filename in inp.outputs.items():
            resolved = self._resolve_path(filename, inp)
            resolved.parent.mkdir(parents=True, exist_ok=True)
            resolved.write_text(f"echo: mock artifact for {key}")
            outputs[key] = str(resolved)
        
        return ExecutorResult(
            outputs=outputs,
            returncode=0,
            stdout="\n".join(stdout_lines),
            stderr="",
        )