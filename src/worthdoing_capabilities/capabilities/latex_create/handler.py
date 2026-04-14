"""LaTeX document creation capability handler."""
from pathlib import Path
import re


def _escape_latex(text: str) -> str:
    """Escape special LaTeX characters in text content."""
    # Order matters: backslash first, then others
    replacements = [
        ("\\", "\\textbackslash{}"),
        ("&", "\\&"),
        ("%", "\\%"),
        ("$", "\\$"),
        ("#", "\\#"),
        ("_", "\\_"),
        ("{", "\\{"),
        ("}", "\\}"),
        ("~", "\\textasciitilde{}"),
        ("^", "\\textasciicircum{}"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


async def execute(input_data: dict) -> dict:
    output_path = Path(input_data["output_path"])
    content_blocks = input_data["content"]
    document_class = input_data.get("document_class", "article")
    title = input_data.get("title")
    author = input_data.get("author")
    date = input_data.get("date")
    extra_packages = input_data.get("packages", [])
    bibliography = input_data.get("bibliography", [])

    lines: list[str] = []

    # Document class
    lines.append(f"\\documentclass{{{document_class}}}")
    lines.append("")

    # Default packages
    default_packages = [
        ("inputenc", "utf8"),
        ("fontenc", "T1"),
        ("amsmath", None),
        ("amssymb", None),
        ("geometry", "margin=1in"),
        ("hyperref", None),
        ("graphicx", None),
        ("booktabs", None),
        ("listings", None),
        ("xcolor", None),
    ]

    packages_used = []
    for pkg, opts in default_packages:
        if opts:
            lines.append(f"\\usepackage[{opts}]{{{pkg}}}")
        else:
            lines.append(f"\\usepackage{{{pkg}}}")
        packages_used.append(pkg)

    for pkg in extra_packages:
        lines.append(f"\\usepackage{{{pkg}}}")
        packages_used.append(pkg)

    lines.append("")

    # Listings style configuration
    lines.append("\\lstset{")
    lines.append("  basicstyle=\\ttfamily\\small,")
    lines.append("  breaklines=true,")
    lines.append("  frame=single,")
    lines.append("  numbers=left,")
    lines.append("  numberstyle=\\tiny\\color{gray},")
    lines.append("  keywordstyle=\\color{blue},")
    lines.append("  commentstyle=\\color{green!60!black},")
    lines.append("  stringstyle=\\color{red},")
    lines.append("}")
    lines.append("")

    # Title, author, date
    if title:
        lines.append(f"\\title{{{_escape_latex(title)}}}")
    if author:
        lines.append(f"\\author{{{_escape_latex(author)}}}")
    if date:
        lines.append(f"\\date{{{_escape_latex(date)}}}")
    elif title:
        lines.append("\\date{\\today}")

    lines.append("")
    lines.append("\\begin{document}")
    lines.append("")

    if title:
        lines.append("\\maketitle")
        lines.append("")

    # Process content blocks
    blocks_count = 0
    for block in content_blocks:
        block_type = block.get("type", "text")

        if block_type == "section":
            text = block.get("text", "")
            label = block.get("label", "")
            lines.append(f"\\section{{{_escape_latex(text)}}}")
            if label:
                lines.append(f"\\label{{{label}}}")

        elif block_type == "subsection":
            text = block.get("text", "")
            label = block.get("label", "")
            lines.append(f"\\subsection{{{_escape_latex(text)}}}")
            if label:
                lines.append(f"\\label{{{label}}}")

        elif block_type == "text":
            text = block.get("text", "")
            lines.append(_escape_latex(text))

        elif block_type == "equation":
            text = block.get("text", "")
            label = block.get("label", "")
            lines.append("\\begin{equation}")
            if label:
                lines.append(f"\\label{{{label}}}")
            # Do not escape equation content - it's raw LaTeX math
            lines.append(text)
            lines.append("\\end{equation}")

        elif block_type == "itemize":
            items = block.get("items", [])
            lines.append("\\begin{itemize}")
            for item in items:
                lines.append(f"  \\item {_escape_latex(item)}")
            lines.append("\\end{itemize}")

        elif block_type == "enumerate":
            items = block.get("items", [])
            lines.append("\\begin{enumerate}")
            for item in items:
                lines.append(f"  \\item {_escape_latex(item)}")
            lines.append("\\end{enumerate}")

        elif block_type == "table":
            headers = block.get("headers", [])
            rows = block.get("rows", [])
            caption = block.get("caption", "")
            label = block.get("label", "")
            if headers:
                col_spec = " ".join(["l"] * len(headers))
                lines.append("\\begin{table}[htbp]")
                lines.append("\\centering")
                if caption:
                    lines.append(f"\\caption{{{_escape_latex(caption)}}}")
                if label:
                    lines.append(f"\\label{{{label}}}")
                lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
                lines.append("\\toprule")
                lines.append(" & ".join(_escape_latex(str(h)) for h in headers) + " \\\\")
                lines.append("\\midrule")
                for row in rows:
                    lines.append(" & ".join(_escape_latex(str(v)) for v in row) + " \\\\")
                lines.append("\\bottomrule")
                lines.append("\\end{tabular}")
                lines.append("\\end{table}")

        elif block_type == "code":
            text = block.get("text", "")
            language = block.get("language", "")
            if language:
                lines.append(f"\\begin{{lstlisting}}[language={language}]")
            else:
                lines.append("\\begin{lstlisting}")
            # Do not escape code content
            lines.append(text)
            lines.append("\\end{lstlisting}")

        elif block_type == "figure_placeholder":
            caption = block.get("caption", "Figure")
            label = block.get("label", "")
            lines.append("\\begin{figure}[htbp]")
            lines.append("\\centering")
            lines.append("% TODO: Replace with actual image")
            lines.append("\\fbox{\\parbox{0.8\\textwidth}{\\centering\\vspace{2cm}[Figure Placeholder]\\vspace{2cm}}}")
            if caption:
                lines.append(f"\\caption{{{_escape_latex(caption)}}}")
            if label:
                lines.append(f"\\label{{{label}}}")
            lines.append("\\end{figure}")

        lines.append("")
        blocks_count += 1

    # Bibliography
    has_bibliography = len(bibliography) > 0
    if has_bibliography:
        lines.append(f"\\begin{{thebibliography}}{{{len(bibliography)}}}")
        lines.append("")
        for entry in bibliography:
            key = entry.get("key", "")
            bib_author = entry.get("author", "")
            bib_title = entry.get("title", "")
            year = entry.get("year", "")
            journal = entry.get("journal", "")
            booktitle = entry.get("booktitle", "")
            publisher = entry.get("publisher", "")

            parts = []
            if bib_author:
                parts.append(_escape_latex(bib_author))
            if year:
                parts.append(f"({_escape_latex(year)})")
            if bib_title:
                parts.append(f"\\textit{{{_escape_latex(bib_title)}}}")
            if journal:
                parts.append(_escape_latex(journal))
            if booktitle:
                parts.append(_escape_latex(booktitle))
            if publisher:
                parts.append(_escape_latex(publisher))

            ref_text = ". ".join(parts) + "."
            lines.append(f"\\bibitem{{{key}}} {ref_text}")
            lines.append("")

        lines.append("\\end{thebibliography}")
        lines.append("")

    lines.append("\\end{document}")
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "path": str(output_path),
        "blocks_count": blocks_count,
        "has_bibliography": has_bibliography,
        "packages_used": packages_used,
    }
