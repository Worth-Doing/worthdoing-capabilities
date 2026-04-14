"""Shared test fixtures for WorthDoing Capabilities."""
import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_contract_data():
    return {
        "name": "test.capability",
        "version": "0.1.0",
        "description": "A test capability",
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
            "properties": {
                "result": {"type": "string"}
            },
        },
        "execution": {
            "executor": "python",
            "function": "tests.fixtures.sample_handler.execute",
        },
        "auth": {"type": "none"},
        "cache": {"enabled": False},
        "retry": {"max_attempts": 1, "backoff": "none"},
        "timeout": {"seconds": 10},
    }
