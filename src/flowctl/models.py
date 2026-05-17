from pydantic import BaseModel, Field, model_validator
from typing import Optional


class FlowctlConfig(BaseModel):
    preferred_executor: str = "echo"
    framework_version: str = "0.1.0"
    run_dir: str = ".flows/runs"
    workflow_dir: str = ".flows"


class RoleBinding(BaseModel):
    prompt: str


class RoleConfig(BaseModel):
    name: str
    model: str
    description: Optional[str] = None
    default_prompt: Optional[str] = None
    executor: Optional[str] = None
    bindings: dict[str, RoleBinding] = Field(default_factory=dict)


class Transition(BaseModel):
    model_config = {"populate_by_name": True}
    from_: str = Field(alias="from")
    to: str
    when: Optional[str] = None
    pause: bool = False
    auto: Optional[str] = None


class Node(BaseModel):
    role: str
    prompt: Optional[str] = None
    skills: list[str] = []
    inputs: dict[str, str] = {}
    outputs: dict[str, str] = {}
    executor: Optional[str] = None
    command: Optional[str] = None
    timeout_seconds: Optional[int] = 60

    @model_validator(mode='after')
    def validate_fields(self) -> 'Node':
        if self.executor == 'bash':
            if not self.command:
                raise ValueError(
                    f"Node with executor='bash' must have 'command' field. "
                    f"Specify a script path like 'scripts/fetch-issue.sh'"
                )
        else:
            if self.command:
                raise ValueError(
                    f"'command' field is only allowed when executor='bash'. "
                    f"Current executor: {self.executor or 'none'}"
                )
            if not self.prompt:
                raise ValueError(
                    f"Node without executor='bash' must have 'prompt' field."
                )
        if self.timeout_seconds is not None and self.timeout_seconds <= 0:
            raise ValueError(f"timeout_seconds must be positive: {self.timeout_seconds}")
        return self


class WorkflowDef(BaseModel):
    version: str = "1"
    nodes: dict[str, Node]
    transitions: list[Transition]
    roles: Optional[dict[str, RoleConfig]] = None