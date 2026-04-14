"""Abstract base executor for WorthDoing capability contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseExecutor(ABC):
    """Base class for all capability executors."""

    @abstractmethod
    async def execute(
        self, config: dict, input_data: dict, auth_headers: dict
    ) -> dict:
        """Execute a capability and return the result.

        Args:
            config: The execution configuration from the capability contract.
            input_data: Validated input data for the capability.
            auth_headers: Resolved authentication headers.

        Returns:
            A dict containing the execution result.
        """
        ...

    @property
    @abstractmethod
    def executor_type(self) -> str:
        """Return the executor type identifier."""
        ...
