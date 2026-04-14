"""Tests for the latex_create capability handler."""

import pytest
from pathlib import Path

from worthdoing_capabilities.capabilities.latex_create.handler import execute


@pytest.mark.asyncio
async def test_execute_creates_tex_file(tmp_path):
    output_file = tmp_path / "test_doc.tex"

    input_data = {
        "output_path": str(output_file),
        "title": "Test Paper",
        "author": "Test Author",
        "content": [
            {"type": "section", "text": "Introduction"},
            {"type": "text", "text": "This is the introduction."},
            {"type": "equation", "text": "E = mc^2", "label": "eq:einstein"},
            {"type": "itemize", "items": ["First item", "Second item"]},
        ],
    }

    result = await execute(input_data)

    assert output_file.exists()
    assert result["path"] == str(output_file)
    assert result["blocks_count"] == 4
    assert result["has_bibliography"] is False
    assert "amsmath" in result["packages_used"]

    content = output_file.read_text()
    assert "\\documentclass{article}" in content
    assert "\\begin{document}" in content
    assert "\\end{document}" in content
    assert "\\section{Introduction}" in content
    assert "E = mc^2" in content


@pytest.mark.asyncio
async def test_execute_with_bibliography(tmp_path):
    output_file = tmp_path / "bib_doc.tex"

    input_data = {
        "output_path": str(output_file),
        "title": "Research Paper",
        "content": [
            {"type": "section", "text": "Related Work"},
            {"type": "text", "text": "See the references."},
        ],
        "bibliography": [
            {
                "key": "knuth1984",
                "type": "book",
                "title": "The TeXbook",
                "author": "Donald Knuth",
                "year": "1984",
                "publisher": "Addison-Wesley",
            }
        ],
    }

    result = await execute(input_data)

    assert output_file.exists()
    assert result["has_bibliography"] is True

    content = output_file.read_text()
    assert "\\begin{thebibliography}" in content
    assert "knuth1984" in content


@pytest.mark.asyncio
async def test_execute_with_table_and_code(tmp_path):
    output_file = tmp_path / "table_code.tex"

    input_data = {
        "output_path": str(output_file),
        "content": [
            {
                "type": "table",
                "headers": ["Method", "Accuracy"],
                "rows": [["SVM", "92%"], ["RF", "89%"]],
                "caption": "Results",
                "label": "tab:results",
            },
            {
                "type": "code",
                "language": "Python",
                "text": "print('hello')",
            },
            {
                "type": "figure_placeholder",
                "caption": "Architecture diagram",
                "label": "fig:arch",
            },
        ],
    }

    result = await execute(input_data)

    assert output_file.exists()
    assert result["blocks_count"] == 3

    content = output_file.read_text()
    assert "\\begin{tabular}" in content
    assert "\\toprule" in content
    assert "\\begin{lstlisting}" in content
    assert "\\begin{figure}" in content


@pytest.mark.asyncio
async def test_execute_escapes_special_chars(tmp_path):
    output_file = tmp_path / "escape.tex"

    input_data = {
        "output_path": str(output_file),
        "content": [
            {"type": "text", "text": "Price is 100$ & tax is 5%"},
        ],
    }

    result = await execute(input_data)

    content = output_file.read_text()
    assert "100\\$" in content
    assert "\\&" in content
    assert "5\\%" in content


@pytest.mark.asyncio
async def test_execute_custom_document_class(tmp_path):
    output_file = tmp_path / "report.tex"

    input_data = {
        "output_path": str(output_file),
        "document_class": "report",
        "packages": ["tikz"],
        "content": [
            {"type": "section", "text": "Chapter One"},
        ],
    }

    result = await execute(input_data)

    content = output_file.read_text()
    assert "\\documentclass{report}" in content
    assert "\\usepackage{tikz}" in content
    assert "tikz" in result["packages_used"]
