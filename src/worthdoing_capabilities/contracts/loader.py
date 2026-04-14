"""Contract loading utilities for discovering and validating capability contracts."""

from __future__ import annotations

from pathlib import Path

from worthdoing_capabilities.contracts.models import CapabilityContract


def load_contract(path: Path) -> CapabilityContract:
    """Load and validate a single capability contract from a YAML file.

    Args:
        path: Path to the capability YAML file.

    Returns:
        A validated CapabilityContract instance.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file content is not a valid contract.
    """
    return CapabilityContract.from_yaml(path)


def load_contracts_from_directory(base_dir: Path) -> list[CapabilityContract]:
    """Discover and load all capability contracts from a directory tree.

    Recursively searches for files named ``capability.yaml`` under the
    given base directory and loads each one as a CapabilityContract.

    Args:
        base_dir: Root directory to search for capability.yaml files.

    Returns:
        A list of validated CapabilityContract instances.

    Raises:
        FileNotFoundError: If the base directory does not exist.
    """
    if not base_dir.exists():
        raise FileNotFoundError(f"Directory not found: {base_dir}")

    if not base_dir.is_dir():
        raise ValueError(f"Path is not a directory: {base_dir}")

    contracts: list[CapabilityContract] = []
    for yaml_path in sorted(base_dir.rglob("capability.yaml")):
        contract = CapabilityContract.from_yaml(yaml_path)
        contracts.append(contract)

    return contracts
