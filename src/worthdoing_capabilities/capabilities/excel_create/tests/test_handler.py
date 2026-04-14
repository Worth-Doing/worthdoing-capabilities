"""Tests for the excel_create capability handler."""

import pytest
from pathlib import Path

from worthdoing_capabilities.capabilities.excel_create.handler import execute


@pytest.mark.asyncio
async def test_execute_creates_xlsx(tmp_path):
    output_file = tmp_path / "test_output.xlsx"

    input_data = {
        "output_path": str(output_file),
        "sheets": [
            {
                "name": "Sales",
                "headers": ["Product", "Quantity", "Price"],
                "rows": [
                    ["Widget A", 10, 29.99],
                    ["Widget B", 25, 14.50],
                ],
            },
            {
                "name": "Summary",
                "headers": ["Metric", "Value"],
                "rows": [
                    ["Total Products", 2],
                ],
            },
        ],
    }

    result = await execute(input_data)

    assert output_file.exists()
    assert result["path"] == str(output_file)
    assert result["sheets_count"] == 2
    assert result["total_rows"] == 3


@pytest.mark.asyncio
async def test_execute_creates_xlsx_with_column_widths(tmp_path):
    output_file = tmp_path / "widths.xlsx"

    input_data = {
        "output_path": str(output_file),
        "sheets": [
            {
                "name": "Data",
                "headers": ["Name", "Value"],
                "rows": [["Alpha", 100]],
                "column_widths": [20, 15],
            }
        ],
    }

    result = await execute(input_data)

    assert output_file.exists()
    assert result["sheets_count"] == 1
    assert result["total_rows"] == 1


@pytest.mark.asyncio
async def test_execute_creates_nested_directory(tmp_path):
    output_file = tmp_path / "sub" / "dir" / "output.xlsx"

    input_data = {
        "output_path": str(output_file),
        "sheets": [
            {
                "name": "Sheet1",
                "headers": ["A"],
                "rows": [["value"]],
            }
        ],
    }

    result = await execute(input_data)

    assert output_file.exists()
    assert result["sheets_count"] == 1
