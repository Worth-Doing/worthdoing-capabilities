"""Executor registry for WorthDoing capability contracts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from worthdoing_capabilities.executors.base import BaseExecutor
from worthdoing_capabilities.executors.http_executor import HttpExecutor
from worthdoing_capabilities.executors.python_executor import PythonExecutor
from worthdoing_capabilities.executors.shell_executor import ShellExecutor
from worthdoing_capabilities.executors.workflow_executor import WorkflowExecutor

if TYPE_CHECKING:
    from worthdoing_capabilities.runtime.engine import CapabilityRuntime


class ExecutorRegistry:
    """Registry mapping executor type identifiers to executor instances."""

    def __init__(self) -> None:
        self._executors: dict[str, BaseExecutor] = {}

    def register(self, executor: BaseExecutor) -> None:
        """Register an executor instance by its type identifier.

        Args:
            executor: The executor to register.
        """
        self._executors[executor.executor_type] = executor

    def get(self, executor_type: str) -> BaseExecutor:
        """Retrieve a registered executor by type.

        Args:
            executor_type: The executor type identifier.

        Returns:
            The registered BaseExecutor instance.

        Raises:
            KeyError: If no executor is registered for the given type.
        """
        if executor_type not in self._executors:
            raise KeyError(f"No executor registered for type: {executor_type}")
        return self._executors[executor_type]

    def available_types(self) -> list[str]:
        """Return a list of all registered executor type identifiers."""
        return list(self._executors.keys())


def create_default_registry(runtime: CapabilityRuntime | None = None) -> ExecutorRegistry:
    """Create an ExecutorRegistry pre-loaded with the built-in executors.

    Args:
        runtime: Optional CapabilityRuntime reference needed by the
            WorkflowExecutor. If ``None``, the workflow executor is not
            registered.

    Returns:
        A fully populated ExecutorRegistry.
    """
    registry = ExecutorRegistry()
    registry.register(HttpExecutor())
    registry.register(PythonExecutor())
    registry.register(ShellExecutor())
    if runtime:
        registry.register(WorkflowExecutor(runtime))
    return registry
