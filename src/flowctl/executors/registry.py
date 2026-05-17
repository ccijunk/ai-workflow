from typing import Callable
from .base import ExecutorAdapter
from .echo import EchoAdapter
from .opencode import OpencodeAdapter
from .bash import BashExecutor


class ExecutorRegistry:
    def __init__(self):
        self._factories: dict[str, Callable[..., ExecutorAdapter]] = {}

    def register(self, name: str, factory: Callable[..., ExecutorAdapter]) -> None:
        self._factories[name] = factory

    def get(self, executor_name: str, **kwargs) -> ExecutorAdapter:
        if executor_name not in self._factories:
            available = ', '.join(self.list_available())
            raise ValueError(f"Unknown executor: '{executor_name}'. Available: {available}")
        return self._factories[executor_name](**kwargs)

    def list_available(self) -> list[str]:
        return sorted(self._factories.keys())


def create_default_registry() -> ExecutorRegistry:
    registry = ExecutorRegistry()
    registry.register("echo", lambda **kw: EchoAdapter())
    registry.register("opencode", lambda model=None, agent=None, **kw: OpencodeAdapter(model=model, agent=agent))
    registry.register("bash", lambda script_path=None, timeout_seconds=60, **kw: BashExecutor(script_path=script_path or "", timeout_seconds=timeout_seconds))
    return registry