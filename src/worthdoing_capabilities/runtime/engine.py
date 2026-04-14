"""WorthDoing AI -- Capability Runtime Engine."""

from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Any, Optional

from worthdoing_capabilities.contracts.models import CapabilityContract
from worthdoing_capabilities.registry.registry import CapabilityRegistry
from worthdoing_capabilities.executors.registry import (
    ExecutorRegistry,
    create_default_registry,
)
from worthdoing_capabilities.validation.validator import validate_input, validate_output
from worthdoing_capabilities.auth.resolver import resolve_auth
from worthdoing_capabilities.cache.store import CacheStore
from worthdoing_capabilities.memory.record import ExecutionRecord, ExecutionLog


class CapabilityRuntime:
    """WorthDoing AI -- Capability Runtime Engine.

    Orchestrates capability discovery, validation, execution, caching,
    and logging. Serves as the primary entry point for running capabilities.
    """

    def __init__(self, *, auto_discover: bool = True) -> None:
        self.registry = CapabilityRegistry()
        self.cache = CacheStore()
        self.log = ExecutionLog()
        self._executor_registry: ExecutorRegistry = create_default_registry(runtime=self)

        if auto_discover:
            self.registry.load_builtin()

    # --------------------------------------------------------------------- #
    # Query methods
    # --------------------------------------------------------------------- #

    def list_capabilities(self) -> list[dict]:
        """List all registered capabilities with summary info.

        Returns:
            A list of dicts with name, version, description, category, and tags.
        """
        return [
            {
                "name": c.name,
                "version": c.version,
                "description": c.description,
                "category": c.category,
                "tags": c.tags,
            }
            for c in self.registry.list_all()
        ]

    def inspect(self, name: str) -> dict:
        """Get full details of a capability.

        Args:
            name: The capability name.

        Returns:
            The full contract as a dict.
        """
        contract = self.registry.get(name)
        return contract.model_dump()

    # --------------------------------------------------------------------- #
    # Execution
    # --------------------------------------------------------------------- #

    def run(self, name: str, input_data: dict, *, bypass_cache: bool = False) -> dict:
        """Execute a capability synchronously.

        Convenience wrapper around :meth:`run_async` for non-async contexts.

        Args:
            name: The capability name to execute.
            input_data: Input data for the capability.
            bypass_cache: If True, skip cache lookup and storage.

        Returns:
            The validated output dict from the capability.
        """
        return asyncio.run(
            self.run_async(name, input_data, bypass_cache=bypass_cache)
        )

    async def run_async(
        self,
        name: str,
        input_data: dict,
        *,
        bypass_cache: bool = False,
    ) -> dict:
        """Execute a capability asynchronously.

        Performs full validation, caching, auth resolution, execution with
        retry/timeout, output validation, and logging.

        Args:
            name: The capability name to execute.
            input_data: Input data for the capability.
            bypass_cache: If True, skip cache lookup and storage.

        Returns:
            The validated output dict from the capability.

        Raises:
            KeyError: If the capability is not registered.
            ValueError: If input or output validation fails.
            RuntimeError: If execution fails after all retry attempts.
        """
        contract = self.registry.get(name)

        # Validate input
        validated_input = validate_input(contract, input_data)

        # Check cache
        cache_key: str | None = None
        cache_status = "disabled"

        if contract.cache.enabled and not bypass_cache:
            cache_key = self.cache.generate_key(name, validated_input)
            cached = self.cache.get(cache_key)
            if cached.hit:
                record = ExecutionRecord(
                    capability_name=name,
                    version=contract.version,
                    input_data=validated_input,
                    output_data=cached.value,
                    status="cache_hit",
                    duration_ms=0.0,
                    cache_status="hit",
                )
                self.log.add(record)
                return cached.value
            cache_status = "miss"
        elif bypass_cache:
            cache_status = "bypass"

        # Resolve auth
        auth_headers = resolve_auth(contract.auth)

        # Get executor
        executor = self._executor_registry.get(contract.execution.executor)

        # Execute with timeout and retry
        start = time.perf_counter()
        last_error: str | None = None
        attempts = contract.retry.max_attempts

        for attempt in range(attempts):
            try:
                result = await asyncio.wait_for(
                    executor.execute(
                        contract.execution.model_dump(),
                        validated_input,
                        auth_headers,
                    ),
                    timeout=contract.timeout.seconds,
                )
                duration_ms = (time.perf_counter() - start) * 1000

                # Validate output
                validated_output = validate_output(contract, result)

                # Cache result
                if contract.cache.enabled and not bypass_cache and cache_key is not None:
                    self.cache.set(cache_key, validated_output, contract.cache.ttl_seconds)

                # Record execution
                record = ExecutionRecord(
                    capability_name=name,
                    version=contract.version,
                    input_data=validated_input,
                    output_data=validated_output,
                    status="success",
                    duration_ms=duration_ms,
                    cache_status=cache_status,
                )
                self.log.add(record)

                return validated_output

            except asyncio.TimeoutError:
                last_error = (
                    f"Capability '{name}' timed out after {contract.timeout.seconds}s"
                )
            except Exception as exc:
                last_error = str(exc)

            # Backoff before retry (unless this was the last attempt)
            if attempt < attempts - 1:
                if contract.retry.backoff == "exponential":
                    await asyncio.sleep(2 ** attempt * 0.5)
                elif contract.retry.backoff == "linear":
                    await asyncio.sleep((attempt + 1) * 0.5)

        # All attempts failed
        duration_ms = (time.perf_counter() - start) * 1000
        status = "timeout" if "timed out" in (last_error or "") else "error"

        record = ExecutionRecord(
            capability_name=name,
            version=contract.version,
            input_data=validated_input,
            output_data=None,
            status=status,
            duration_ms=duration_ms,
            cache_status=cache_status,
            error=last_error,
        )
        self.log.add(record)

        raise RuntimeError(f"Capability '{name}' failed: {last_error}")

    # --------------------------------------------------------------------- #
    # Registration and loading
    # --------------------------------------------------------------------- #

    def register_capability(self, contract: CapabilityContract) -> None:
        """Manually register a capability.

        Args:
            contract: The validated CapabilityContract to register.
        """
        self.registry.register(contract)

    def load_capabilities(self, directory: Path) -> int:
        """Load capabilities from a directory.

        Args:
            directory: Path to a directory containing capability.yaml files.

        Returns:
            The number of capabilities loaded.
        """
        return self.registry.load_from_directory(directory)

    # --------------------------------------------------------------------- #
    # Observability
    # --------------------------------------------------------------------- #

    def execution_history(self, **kwargs: Any) -> list[dict]:
        """Query execution history.

        Accepts the same keyword arguments as ``ExecutionLog.query``.

        Returns:
            A list of execution record dicts.
        """
        records = self.log.query(**kwargs)
        return [r.model_dump() for r in records]

    def cache_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            A dict with hit count, miss count, size, and hit rate.
        """
        return self.cache.stats()
