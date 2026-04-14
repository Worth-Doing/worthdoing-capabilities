"""Tests for the shell capability."""

import pytest

from worthdoing_capabilities.capabilities.shell.handler import execute


@pytest.mark.asyncio
async def test_execute_echo():
    result = await execute({"command": "echo hello"})
    assert result["stdout"] == "hello"
    assert result["returncode"] == 0


@pytest.mark.asyncio
async def test_execute_returns_stderr_on_error():
    result = await execute({"command": "ls /nonexistent_path_12345"})
    assert result["returncode"] != 0
    assert len(result["stderr"]) > 0
