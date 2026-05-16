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
        abs_run_dir = inp.run_dir.resolve()
        cmd.extend(["--dir", str(abs_run_dir)])
        cmd.extend(["--format", "json"])

        if self.model:
            cmd.extend(["--model", self.model])
        if self.agent:
            cmd.extend(["--agent", self.agent])

        for skill_path in inp.skill_paths:
            if inp.workflow_dir:
                src_skill = inp.workflow_dir / skill_path
            else:
                src_skill = Path(skill_path)
            skill_file = inp.run_dir / Path(skill_path).name
            if src_skill.exists():
                skill_file.write_text(src_skill.read_text())
            cmd.extend(["--file", str(skill_file)])

        cmd.append(prompt_content)

        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(abs_run_dir),
        )

        outputs = {}
        session_id = None

        if proc.returncode == 0:
            session_id = self._extract_session_id(proc.stdout) or self._extract_session_id(proc.stderr)
            self._extract_and_write_outputs(proc.stdout, inp.outputs, inp.run_dir)
            for key, rel_path in inp.outputs.items():
                artifact_path = inp.run_dir / rel_path
                if artifact_path.exists():
                    outputs[key] = artifact_path.read_text()

        if session_id:
            self._delete_session(session_id)

        return ExecutorResult(
            outputs=outputs,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )

    def _extract_session_id(self, stdout: str) -> str | None:
        for line in stdout.splitlines():
            try:
                event = json.loads(line)
                if "sessionID" in event:
                    return event["sessionID"]
            except json.JSONDecodeError:
                continue
        return None

    def _delete_session(self, session_id: str):
        subprocess.run(
            ["opencode", "session", "delete", session_id],
            capture_output=True,
            text=True,
        )

    def _load_prompt(self, inp: ExecutorInput) -> str:
        prompt_lines = []
        
        if inp.workflow_dir:
            prompt_file = inp.workflow_dir / inp.prompt_path
        else:
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
                if not input_file.exists() and inp.workflow_dir:
                    input_file = inp.workflow_dir / path
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