"""Integration tests for CapabilityRuntime.

These tests verify end-to-end behaviour of the runtime engine.
The runtime module (runtime.engine) may not be implemented yet;
tests are skipped gracefully in that case.
"""

import pytest

try:
    from worthdoing_capabilities.runtime.engine import CapabilityRuntime

    _RUNTIME_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    _RUNTIME_AVAILABLE = False

skip_no_runtime = pytest.mark.skipif(
    not _RUNTIME_AVAILABLE,
    reason="CapabilityRuntime not yet implemented (runtime.engine missing)",
)


@skip_no_runtime
class TestRuntimeInitialization:
    """Test that the runtime initializes correctly."""

    def test_runtime_creates_successfully(self):
        runtime = CapabilityRuntime()

        assert runtime is not None
        assert runtime.registry is not None
        assert runtime.cache is not None
        assert runtime.log is not None

    def test_runtime_without_auto_discover(self):
        runtime = CapabilityRuntime(auto_discover=False)

        assert runtime.registry.count() == 0


@skip_no_runtime
class TestRuntimeCapabilities:
    """Test listing and inspecting capabilities through the runtime."""

    def test_list_capabilities_returns_list(self):
        runtime = CapabilityRuntime()
        caps = runtime.list_capabilities()

        assert isinstance(caps, list)

    def test_list_capabilities_entries_are_dicts(self):
        runtime = CapabilityRuntime(auto_discover=False)
        from worthdoing_capabilities.contracts.models import CapabilityContract

        contract = CapabilityContract.model_validate(
            {
                "name": "test.cap",
                "version": "0.1.0",
                "description": "A test capability for integration testing",
                "category": "testing",
                "tags": ["test"],
                "input": {
                    "type": "object",
                    "properties": {"q": {"type": "string"}},
                    "required": ["q"],
                },
                "output": {
                    "type": "object",
                    "properties": {"r": {"type": "string"}},
                },
                "execution": {
                    "executor": "python",
                    "function": "tests.fixtures.sample_handler.execute",
                },
            }
        )
        runtime.register_capability(contract)

        caps = runtime.list_capabilities()
        assert len(caps) == 1
        assert caps[0]["name"] == "test.cap"
        assert "version" in caps[0]
        assert "description" in caps[0]

    def test_inspect_returns_full_contract_dict(self):
        runtime = CapabilityRuntime(auto_discover=False)
        from worthdoing_capabilities.contracts.models import CapabilityContract

        contract = CapabilityContract.model_validate(
            {
                "name": "test.inspect",
                "version": "0.1.0",
                "description": "A capability for inspect testing",
                "category": "testing",
                "tags": ["test"],
                "input": {
                    "type": "object",
                    "properties": {"q": {"type": "string"}},
                    "required": ["q"],
                },
                "output": {
                    "type": "object",
                    "properties": {"r": {"type": "string"}},
                },
                "execution": {
                    "executor": "python",
                    "function": "tests.fixtures.sample_handler.execute",
                },
            }
        )
        runtime.register_capability(contract)

        detail = runtime.inspect("test.inspect")

        assert isinstance(detail, dict)
        assert detail["name"] == "test.inspect"
        assert "execution" in detail
        assert "input" in detail
        assert "output" in detail


@skip_no_runtime
class TestRuntimeExecution:
    """Test running capabilities through the runtime."""

    @pytest.mark.asyncio
    async def test_execute_python_capability(self):
        runtime = CapabilityRuntime(auto_discover=False)
        from worthdoing_capabilities.contracts.models import CapabilityContract

        contract = CapabilityContract.model_validate(
            {
                "name": "test.exec",
                "version": "0.1.0",
                "description": "A capability for execution testing",
                "category": "testing",
                "tags": ["test"],
                "input": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Test input"}
                    },
                    "required": ["query"],
                },
                "output": {
                    "type": "object",
                    "properties": {"result": {"type": "string"}},
                },
                "execution": {
                    "executor": "python",
                    "function": "tests.fixtures.sample_handler.execute",
                },
            }
        )
        runtime.register_capability(contract)

        result = await runtime.run_async("test.exec", {"query": "hello"})

        assert result is not None
        assert result["result"] == "processed: hello"


@skip_no_runtime
class TestRuntimeCache:
    """Test that caching works end-to-end through the runtime."""

    def test_cache_stats_available(self):
        runtime = CapabilityRuntime(auto_discover=False)

        stats = runtime.cache_stats()

        assert "hits" in stats
        assert "misses" in stats
        assert "size" in stats

    @pytest.mark.asyncio
    async def test_cache_hit_on_second_call(self):
        runtime = CapabilityRuntime(auto_discover=False)
        from worthdoing_capabilities.contracts.models import CapabilityContract

        contract = CapabilityContract.model_validate(
            {
                "name": "test.cached",
                "version": "0.1.0",
                "description": "A cached capability for testing",
                "category": "testing",
                "tags": ["test"],
                "input": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    },
                    "required": ["query"],
                },
                "output": {
                    "type": "object",
                    "properties": {"result": {"type": "string"}},
                },
                "execution": {
                    "executor": "python",
                    "function": "tests.fixtures.sample_handler.execute",
                },
                "cache": {"enabled": True, "ttl_seconds": 300},
            }
        )
        runtime.register_capability(contract)

        # First call -- cache miss
        result1 = await runtime.run_async("test.cached", {"query": "cached"})
        # Second call -- should be cache hit
        result2 = await runtime.run_async("test.cached", {"query": "cached"})

        assert result1 == result2

        stats = runtime.cache_stats()
        assert stats["hits"] >= 1


@skip_no_runtime
class TestRuntimeExecutionRecord:
    """Test that execution records are created after runs."""

    @pytest.mark.asyncio
    async def test_execution_record_created_after_run(self):
        runtime = CapabilityRuntime(auto_discover=False)
        from worthdoing_capabilities.contracts.models import CapabilityContract

        contract = CapabilityContract.model_validate(
            {
                "name": "test.logged",
                "version": "0.1.0",
                "description": "A capability for logging testing",
                "category": "testing",
                "tags": ["test"],
                "input": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    },
                    "required": ["query"],
                },
                "output": {
                    "type": "object",
                    "properties": {"result": {"type": "string"}},
                },
                "execution": {
                    "executor": "python",
                    "function": "tests.fixtures.sample_handler.execute",
                },
            }
        )
        runtime.register_capability(contract)

        await runtime.run_async("test.logged", {"query": "log-me"})

        history = runtime.execution_history()
        assert len(history) == 1
        assert history[0]["capability_name"] == "test.logged"
        assert history[0]["status"] == "success"
