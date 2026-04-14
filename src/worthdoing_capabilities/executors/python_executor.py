"""Python executor for WorthDoing internal capabilities."""

from __future__ import annotations

import asyncio
import importlib
import inspect
from typing import Any

from worthdoing_capabilities.executors.base import BaseExecutor


class PythonExecutor(BaseExecutor):
    """Executor that dynamically imports and calls Python functions.

    The capability configuration must contain a ``function`` field with a
    dotted import path, e.g.
    ``worthdoing_capabilities.capabilities.file_read.handler.execute``.
    The final segment is the callable name; the preceding segments form
    the module path.
    """

    @property
    def executor_type(self) -> str:
        return "python"

    async def execute(
        self, config: dict, input_data: dict, auth_headers: dict
    ) -> dict:
        """Execute a Python function identified by a dotted import path.

        Supports both synchronous and asynchronous callables. Synchronous
        functions are executed via ``asyncio.to_thread`` to avoid blocking
        the event loop.

        Args:
            config: Execution configuration with a ``function`` key.
            input_data: Validated input data passed to the function.
            auth_headers: Authentication headers (unused for Python execution
                but accepted for interface consistency).

        Returns:
            The dict returned by the target function.

        Raises:
            ValueError: If the ``function`` path is missing or malformed.
            ImportError: If the module cannot be imported.
            AttributeError: If the function does not exist in the module.
            RuntimeError: If the function does not return a dict.
        """
        dotted_path: str | None = config.get("function")
        if not dotted_path:
            raise ValueError(
                "PythonExecutor requires a 'function' field in the execution config."
            )

        # Split into module path and callable name
        parts = dotted_path.rsplit(".", 1)
        if len(parts) != 2:
            raise ValueError(
                f"Invalid function path '{dotted_path}': expected 'module.callable' format."
            )

        module_path, func_name = parts

        try:
            module = importlib.import_module(module_path)
        except ImportError as exc:
            raise ImportError(
                f"Could not import module '{module_path}': {exc}"
            ) from exc

        func = getattr(module, func_name, None)
        if func is None:
            raise AttributeError(
                f"Module '{module_path}' has no attribute '{func_name}'."
            )

        if not callable(func):
            raise TypeError(
                f"'{dotted_path}' is not callable."
            )

        # Call the function -- handle both sync and async
        if inspect.iscoroutinefunction(func):
            result = await func(input_data)
        else:
            result = await asyncio.to_thread(func, input_data)

        if not isinstance(result, dict):
            raise RuntimeError(
                f"Function '{dotted_path}' must return a dict, "
                f"got '{type(result).__name__}'."
            )

        return result
