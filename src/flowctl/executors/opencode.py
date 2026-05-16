import subprocess
import json
from pathlib import Path
from .base import ExecutorAdapter, ExecutorInput, ExecutorResult


class OpencodeAdapter(ExecutorAdapter):
    def __init__(self, model: str = None, agent: str = None):
        self.model = model
        self.agent = agent

    def execute(self, inp: ExecutorInput) -> ExecutorResult:
        prompt_content = self._load_prompt(inp)
        
        cmd = ["opencode", "run"]
        cmd.extend(["--dir", str(inp.run_dir)])
        cmd.extend(["--format", "json"])

        if self.model:
            cmd.extend(["--model", self.model])
        if self.agent:
            cmd.extend(["--agent", self.agent])

        for skill_path in inp.skill_paths:
            skill_file = inp.run_dir / Path(skill_path).name
            if Path(skill_path).exists():
                skill_file.write_text(Path(skill_path).read_text())
            cmd.extend(["--file", str(skill_file)])

        cmd.append(prompt_content)

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(inp.run_dir),
        )

        outputs = {}
        if proc.returncode == 0:
            self._extract_and_write_outputs(proc.stdout, inp.outputs, inp.run_dir)
            for key, rel_path in inp.outputs.items():
                artifact_path = inp.run_dir / rel_path
                if artifact_path.exists():
                    outputs[key] = artifact_path.read_text()

        return ExecutorResult(
            outputs=outputs,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )

    def _load_prompt(self, inp: ExecutorInput) -> str:
        prompt_lines = []
        
        prompt_file = inp.run_dir / inp.prompt_path
        if prompt_file.exists():
            prompt_lines.append(prompt_file.read_text())
        else:
            prompt_lines.append(f"Role: {inp.role}")
            prompt_lines.append(f"Prompt file: {inp.prompt_path}")
        
        if inp.inputs:
            prompt_lines.append("\n## Available Inputs:")
            for key, path in inp.inputs.items():
                input_file = inp.run_dir / path
                if input_file.exists():
                    prompt_lines.append(f"\n### {key} ({path})")
                    prompt_lines.append(input_file.read_text())
        
        if inp.outputs:
            prompt_lines.append("\n## Expected Outputs:")
            prompt_lines.append("Create the following output files:")
            for key, path in inp.outputs.items():
                prompt_lines.append(f"  - {path} (output '{key}')")
        
        return "\n".join(prompt_lines)

    def _extract_and_write_outputs(self, stdout: str, expected_outputs: dict, run_dir: Path):
        pass