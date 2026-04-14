"""Capability registry for discovering and managing WorthDoing capabilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from worthdoing_capabilities.contracts.models import CapabilityContract


class CapabilityRegistry:
    """Registry for managing and querying capability contracts.

    Provides methods to register, look up, search, and discover capabilities
    from YAML contract files.
    """

    def __init__(self) -> None:
        self._capabilities: dict[str, CapabilityContract] = {}

    def register(self, contract: CapabilityContract) -> None:
        """Register a capability contract.

        Args:
            contract: The validated CapabilityContract to register.
        """
        self._capabilities[contract.name] = contract

    def get(self, name: str) -> CapabilityContract:
        """Retrieve a capability contract by name.

        Args:
            name: The capability name.

        Returns:
            The registered CapabilityContract.

        Raises:
            KeyError: If no capability with the given name is registered.
        """
        if name not in self._capabilities:
            available = ", ".join(sorted(self._capabilities.keys())) or "(none)"
            raise KeyError(
                f"Capability '{name}' not found. Available capabilities: {available}"
            )
        return self._capabilities[name]

    def list_all(self) -> list[CapabilityContract]:
        """Return all registered capability contracts.

        Returns:
            A list of all CapabilityContract instances, sorted by name.
        """
        return sorted(self._capabilities.values(), key=lambda c: c.name)

    def list_by_category(self, category: str) -> list[CapabilityContract]:
        """Return all capabilities in a given category.

        Args:
            category: The category to filter by (case-insensitive).

        Returns:
            A list of matching CapabilityContract instances.
        """
        cat_lower = category.lower()
        return [
            c for c in self._capabilities.values()
            if c.category.lower() == cat_lower
        ]

    def filter_by_tag(self, tag: str) -> list[CapabilityContract]:
        """Return all capabilities that have a specific tag.

        Args:
            tag: The tag to filter by (case-insensitive).

        Returns:
            A list of matching CapabilityContract instances.
        """
        tag_lower = tag.lower()
        return [
            c for c in self._capabilities.values()
            if any(t.lower() == tag_lower for t in c.tags)
        ]

    def search(self, query: str) -> list[CapabilityContract]:
        """Search capabilities by matching query against name, description, and tags.

        Performs a case-insensitive substring match.

        Args:
            query: The search query string.

        Returns:
            A list of matching CapabilityContract instances.
        """
        q = query.lower()
        results: list[CapabilityContract] = []
        for c in self._capabilities.values():
            if (
                q in c.name.lower()
                or q in c.description.lower()
                or any(q in t.lower() for t in c.tags)
            ):
                results.append(c)
        return sorted(results, key=lambda c: c.name)

    def has(self, name: str) -> bool:
        """Check if a capability is registered.

        Args:
            name: The capability name.

        Returns:
            True if the capability exists, False otherwise.
        """
        return name in self._capabilities

    def count(self) -> int:
        """Return the number of registered capabilities."""
        return len(self._capabilities)

    def categories(self) -> list[str]:
        """Return a sorted list of unique categories across all capabilities."""
        return sorted({c.category for c in self._capabilities.values()})

    def tags(self) -> list[str]:
        """Return a sorted list of unique tags across all capabilities."""
        all_tags: set[str] = set()
        for c in self._capabilities.values():
            all_tags.update(c.tags)
        return sorted(all_tags)

    def load_from_directory(self, base_dir: Path) -> int:
        """Discover and load all capability.yaml files from a directory tree.

        Args:
            base_dir: Root directory to search recursively.

        Returns:
            The number of capabilities loaded.

        Raises:
            FileNotFoundError: If the directory does not exist.
        """
        if not base_dir.exists():
            raise FileNotFoundError(f"Directory not found: {base_dir}")
        if not base_dir.is_dir():
            raise ValueError(f"Path is not a directory: {base_dir}")

        count = 0
        for yaml_path in sorted(base_dir.rglob("capability.yaml")):
            contract = CapabilityContract.from_yaml(yaml_path)
            self.register(contract)
            count += 1

        return count

    def load_builtin(self) -> int:
        """Load built-in capabilities from the package's own capabilities/ directory.

        Returns:
            The number of built-in capabilities loaded. Returns 0 if no
            capability files are found (e.g. capabilities not yet defined).
        """
        capabilities_dir = Path(__file__).resolve().parent.parent / "capabilities"
        if not capabilities_dir.exists():
            return 0
        return self.load_from_directory(capabilities_dir)
