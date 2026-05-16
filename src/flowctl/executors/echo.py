from pathlib import Path
from .base import ExecutorAdapter, ExecutorInput, ExecutorResult


class EchoAdapter(ExecutorAdapter):
    def execute(self, inp: ExecutorInput) -> ExecutorResult:
        stdout_lines = [f"Role: {inp.role}", f"Prompt: {inp.prompt_path}"]
        outputs = {}
        for key, path_str in inp.inputs.items():
            p = Path(path_str)
            if p.exists():
                outputs[key] = p.read_text()
        for key, path_str in inp.outputs.items():
            artifact_path = inp.run_dir / path_str
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(f"echo: mock artifact for {key}")
            outputs[key] = str(artifact_path)
        return ExecutorResult(
            outputs=outputs,
            returncode=0,
            stdout="\n".join(stdout_lines),
            stderr="",
        )