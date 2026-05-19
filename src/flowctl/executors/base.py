import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from flowctl.models import Node


@dataclass
class ExecutorInput:
    role: str
    prompt_path: str
    skill_paths: list[str]
    inputs: dict[str, str]
    outputs: dict[str, str]
    run_dir: Path
    workflow_dir: Optional[Path] = None
    node: Optional[Node] = None


@dataclass
class ExecutorResult:
    outputs: dict[str, str]
    returncode: int
    stdout: str
    stderr: str


class ExecutorAdapter(ABC):
    @abstractmethod
    def execute(self, inp: ExecutorInput) -> ExecutorResult:
        ...