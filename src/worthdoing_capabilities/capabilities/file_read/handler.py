"""File read capability handler."""

from pathlib import Path


async def execute(input_data: dict) -> dict:
    filepath = Path(input_data["path"])

    if not filepath.exists():
        return {
            "path": str(filepath),
            "content": "",
            "size": 0,
            "exists": False,
            "encoding": "utf-8",
        }

    content = filepath.read_text(encoding="utf-8")
    stat = filepath.stat()

    return {
        "path": str(filepath.resolve()),
        "content": content,
        "size": stat.st_size,
        "exists": True,
        "encoding": "utf-8",
    }
