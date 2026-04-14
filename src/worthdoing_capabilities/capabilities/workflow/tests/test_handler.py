"""Tests for the workflow capability contract."""

import pytest
from pathlib import Path

from worthdoing_capabilities.contracts.loader import load_contract


def test_workflow_contract_loads():
    """Verify the workflow capability.yaml loads and validates."""
    yaml_path = Path(__file__).resolve().parent.parent / "capability.yaml"
    contract = load_contract(yaml_path)
    assert contract.name == "workflow.simple_chain"
    assert contract.execution.executor == "workflow"
    assert contract.execution.steps is not None
    assert len(contract.execution.steps) == 2


def test_workflow_steps_reference_valid_capabilities():
    """Verify workflow steps reference known capability names."""
    yaml_path = Path(__file__).resolve().parent.parent / "capability.yaml"
    contract = load_contract(yaml_path)
    step_names = [s["capability"] for s in contract.execution.steps]
    assert "url_fetch" in step_names
    assert "file.read" in step_names
