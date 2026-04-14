"""Tests for the file_read capability handler."""

import pytest
import tempfile
from pathlib import Path

from worthdoing_capabilities.capabilities.file_read.handler import execute


@pytest.mark.asyncio
async def test_execute_reads_existing_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("hello world")
        f.flush()
        path = f.name

    result = await execute({"path": path})
    assert result["exists"] is True
    assert result["content"] == "hello world"
    assert result["size"] > 0
    assert result["encoding"] == "utf-8"

    Path(path).unlink()


@pytest.mark.asyncio
async def test_execute_handles_missing_file():
    result = await execute({"path": "/nonexistent/path/to/file.txt"})
    assert result["exists"] is False
    assert result["content"] == ""
    assert result["size"] == 0
