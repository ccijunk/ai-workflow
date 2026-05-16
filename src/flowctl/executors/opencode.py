import subprocess
import json
from pathlib import Path
from .base import ExecutorAdapter, ExecutorInput, ExecutorResult


class OpencodeAdapter(ExecutorAdapter):
    def __init__(self, model: str = None, agent: str = None):
        self.model = model
        self.agent = agent

    def execute(self, inp: ExecutorInput) -> ExecutorResult:
        cmd = ["opencode", "run"]
        cmd.extend(["--dir", str(inp.run_dir)])
        cmd.extend(["--format", "json"])

        if self.model:
            cmd.extend(["--model", self.model])
        if self.agent:
            cmd.extend(["--agent", self.agent])

        for skill_path in inp.skill_paths:
            cmd.extend(["--file", str(skill_path)])

        prompt = self._build_prompt(inp)
        cmd.append(prompt)

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(inp.run_dir),
        )

        outputs = {}
        if proc.returncode == 0:
            outputs = self._parse_outputs(proc.stdout, inp.outputs)

        return ExecutorResult(
            outputs=outputs,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )

    def _build_prompt(self, inp: ExecutorInput) -> str:
        prompt_lines = [f"Role: {inp.role}"]
        prompt_lines.append(f"Prompt file: {inp.prompt_path}")
        if inp.inputs:
            prompt_lines.append("Inputs available:")
            for key, path in inp.inputs.items():
                prompt_lines.append(f"  - {key}: {path}")
        prompt_lines.append(f"Expected outputs: {list(inp.outputs.keys())}")
        return "\n".join(prompt_lines)

    def _parse_outputs(self, stdout: str, expected_outputs: dict) -> dict:
        outputs = {}
        for line in stdout.splitlines():
            try:
                event = json.loads(line)
                if event.get("type") == "assistant_message":
                    content = event.get("content", "")
                    for key in expected_outputs:
                        if key in outputs:
                            continue
                        path = expected_outputs[key]
                        artifact_path = Path(path)
                        if not artifact_path.is_absolute():
                            pass
                        if artifact_path.exists():
                            outputs[key] = artifact_path.read_text()
            except json.JSONDecodeError:
                continue
        return outputs