import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ExecutorInput:
    role: str
    prompt_path: str
    skill_paths: list[str]
    inputs: dict[str, str]
    outputs: dict[str, str]
    run_dir: Path


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