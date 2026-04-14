"""Tests for the CapabilityRegistry."""

import pytest

from worthdoing_capabilities.contracts.models import CapabilityContract
from worthdoing_capabilities.registry.registry import CapabilityRegistry


def _make_contract(
    name: str = "test.cap",
    category: str = "testing",
    tags: list[str] | None = None,
    description: str = "A test capability for registry tests",
) -> CapabilityContract:
    """Helper to create a minimal CapabilityContract for testing."""
    return CapabilityContract.model_validate(
        {
            "name": name,
            "version": "0.1.0",
            "description": description,
            "category": category,
            "tags": tags or ["test"],
            "input": {
                "type": "object",
                "properties": {"q": {"type": "string"}},
                "required": ["q"],
            },
            "output": {
                "type": "object",
                "properties": {"r": {"type": "string"}},
            },
            "execution": {"executor": "python", "function": "some.module.func"},
        }
    )


class TestRegistryBasics:
    """Test basic register/get/list operations."""

    def test_register_and_retrieve(self):
        registry = CapabilityRegistry()
        contract = _make_contract("my.cap")

        registry.register(contract)
        result = registry.get("my.cap")

        assert result.name == "my.cap"

    def test_list_all_returns_registered_capabilities(self):
        registry = CapabilityRegistry()
        registry.register(_make_contract("cap.one"))
        registry.register(_make_contract("cap.two"))
        registry.register(_make_contract("cap.three"))

        all_caps = registry.list_all()

        assert len(all_caps) == 3
        names = {c.name for c in all_caps}
        assert names == {"cap.one", "cap.two", "cap.three"}

    def test_count_method(self):
        registry = CapabilityRegistry()
        assert registry.count() == 0

        registry.register(_make_contract("cap.a"))
        assert registry.count() == 1

        registry.register(_make_contract("cap.b"))
        assert registry.count() == 2

    def test_has_returns_true_for_registered(self):
        registry = CapabilityRegistry()
        registry.register(_make_contract("exists.cap"))

        assert registry.has("exists.cap") is True

    def test_has_returns_false_for_unregistered(self):
        registry = CapabilityRegistry()

        assert registry.has("nope.cap") is False

    def test_get_unknown_capability_raises_key_error(self):
        registry = CapabilityRegistry()

        with pytest.raises(KeyError, match="not found"):
            registry.get("does.not.exist")

    def test_duplicate_registration_overwrites(self):
        registry = CapabilityRegistry()
        v1 = _make_contract("dup.cap", description="Version one description for dup")
        v2 = _make_contract("dup.cap", description="Version two description for dup")

        registry.register(v1)
        registry.register(v2)

        assert registry.count() == 1
        result = registry.get("dup.cap")
        assert result.description == "Version two description for dup"


class TestRegistryFiltering:
    """Test filtering capabilities by category, tag, and search."""

    def test_list_by_category(self):
        registry = CapabilityRegistry()
        registry.register(_make_contract("io.read", category="io"))
        registry.register(_make_contract("io.write", category="io"))
        registry.register(_make_contract("net.fetch", category="network"))

        io_caps = registry.list_by_category("io")

        assert len(io_caps) == 2
        assert all(c.category == "io" for c in io_caps)

    def test_list_by_category_case_insensitive(self):
        registry = CapabilityRegistry()
        registry.register(_make_contract("cap.one", category="Network"))

        results = registry.list_by_category("network")

        assert len(results) == 1

    def test_filter_by_tag(self):
        registry = CapabilityRegistry()
        registry.register(_make_contract("a", tags=["alpha", "beta"]))
        registry.register(_make_contract("b", tags=["beta", "gamma"]))
        registry.register(_make_contract("c", tags=["gamma"]))

        beta_caps = registry.filter_by_tag("beta")

        assert len(beta_caps) == 2
        names = {c.name for c in beta_caps}
        assert names == {"a", "b"}

    def test_search_by_query(self):
        registry = CapabilityRegistry()
        registry.register(
            _make_contract("file.read", description="Reads files from local disk")
        )
        registry.register(
            _make_contract("url.fetch", description="Fetches URLs from web")
        )

        matched = registry.search("files")

        assert len(matched) == 1
        assert matched[0].name == "file.read"

    def test_search_matches_name(self):
        registry = CapabilityRegistry()
        registry.register(_make_contract("web.search", description="Search the web"))
        registry.register(_make_contract("file.read", description="Read a file"))

        matched = registry.search("web")

        assert len(matched) == 1
        assert matched[0].name == "web.search"

    def test_search_matches_tags(self):
        registry = CapabilityRegistry()
        registry.register(_make_contract("cap.a", tags=["network", "http"]))
        registry.register(_make_contract("cap.b", tags=["filesystem"]))

        matched = registry.search("http")

        assert len(matched) == 1
        assert matched[0].name == "cap.a"

    def test_search_no_results(self):
        registry = CapabilityRegistry()
        registry.register(_make_contract("cap.a"))

        matched = registry.search("nonexistent_xyz")

        assert matched == []
