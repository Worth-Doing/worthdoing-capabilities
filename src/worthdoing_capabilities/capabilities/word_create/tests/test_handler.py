"""Tests for the word_create capability handler."""

import pytest
from pathlib import Path

from worthdoing_capabilities.capabilities.word_create.handler import execute


@pytest.mark.asyncio
async def test_execute_creates_docx(tmp_path):
    output_file = tmp_path / "test_doc.docx"

    input_data = {
        "output_path": str(output_file),
        "title": "Test Report",
        "content": [
            {"type": "heading", "level": 1, "text": "Introduction"},
            {"type": "paragraph", "text": "This is a test paragraph."},
            {"type": "list", "items": ["Item one", "Item two", "Item three"]},
            {
                "type": "table",
                "headers": ["Name", "Score"],
                "rows": [
                    ["Alice", 95],
                    ["Bob", 87],
                ],
            },
        ],
    }

    result = await execute(input_data)

    assert output_file.exists()
    assert result["path"] == str(output_file)
    assert result["blocks_count"] == 4
    assert result["page_estimate"] >= 1


@pytest.mark.asyncio
async def test_execute_creates_docx_without_title(tmp_path):
    output_file = tmp_path / "no_title.docx"

    input_data = {
        "output_path": str(output_file),
        "content": [
            {"type": "paragraph", "text": "Just a paragraph."},
        ],
    }

    result = await execute(input_data)

    assert output_file.exists()
    assert result["blocks_count"] == 1


@pytest.mark.asyncio
async def test_execute_bold_paragraph(tmp_path):
    output_file = tmp_path / "bold.docx"

    input_data = {
        "output_path": str(output_file),
        "content": [
            {"type": "paragraph", "text": "Bold text here", "bold": True},
        ],
    }

    result = await execute(input_data)

    assert output_file.exists()
    assert result["blocks_count"] == 1
