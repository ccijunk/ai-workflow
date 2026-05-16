from pydantic import BaseModel, Field
from typing import Optional


class FlowctlConfig(BaseModel):
    preferred_executor: str = "echo"
    framework_version: str = "0.1.0"


class RoleBinding(BaseModel):
    prompt: str


class RoleConfig(BaseModel):
    name: str
    model: str
    description: Optional[str] = None
    default_prompt: Optional[str] = None
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
    prompt: str
    skills: list[str] = []
    inputs: dict[str, str] = {}
    outputs: dict[str, str] = {}
    executor: Optional[str] = None


class WorkflowDef(BaseModel):
    version: str = "1"
    nodes: dict[str, Node]
    transitions: list[Transition]
    roles: Optional[dict[str, RoleConfig]] = None