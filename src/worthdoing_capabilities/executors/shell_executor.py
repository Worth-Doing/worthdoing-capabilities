"""Shell executor for WorthDoing local command capabilities."""

from __future__ import annotations

import asyncio
import re
import shlex
from typing import Any

from worthdoing_capabilities.executors.base import BaseExecutor


def _template_safe(command: str, input_data: dict) -> str:
    """Replace ``{{ input.xxx }}`` placeholders with shell-escaped input values.

    Each substituted value is passed through ``shlex.quote`` to prevent
    shell injection attacks.

    Args:
        command: The command template string.
        input_data: Input data for placeholder substitution.

    Returns:
        The command string with placeholders replaced by safe values.
    """
    def _replacer(match: re.Match) -> str:
        key = match.group(1).strip()
        if key.startswith("input."):
            field = key[len("input."):]
            value = input_data.get(field)
            if value is None:
                return match.group(0)
            return shlex.quote(str(value))
        return match.group(0)

    return re.sub(r"\{\{\s*(.+?)\s*\}\}", _replacer, command)


class ShellExecutor(BaseExecutor):
    """Executor that runs local shell commands via asyncio subprocess."""

    @property
    def executor_type(self) -> str:
        return "shell"

    async def execute(
        self, config: dict, input_data: dict, auth_headers: dict
    ) -> dict:
        """Execute a shell command from the capability configuration.

        Reads ``command`` from *config*, templates ``{{ input.xxx }}``
        placeholders (with shell-safe escaping via ``shlex.quote``), and
        runs the command as an async subprocess.

        Args:
            config: Execution configuration with ``command`` and optional
                ``timeout`` keys.
            input_data: Validated input data for placeholder substitution.
            auth_headers: Authentication headers (unused for shell execution
                but accepted for interface consistency).

        Returns:
            A dict with ``stdout``, ``stderr``, and ``returncode`` keys.

        Raises:
            ValueError: If the ``command`` field is missing.
            asyncio.TimeoutError: If the command exceeds the configured timeout.
        """
        raw_command: str | None = config.get("command")
        if not raw_command:
            raise ValueError(
                "ShellExecutor requires a 'command' field in the execution config."
            )

        command = _template_safe(raw_command, input_data)
        timeout: int | float | None = config.get("timeout")

        # Use shell=True via create_subprocess_shell for full command-line support
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise asyncio.TimeoutError(
                f"Shell command timed out after {timeout}s: {command[:200]}"
            )

        return {
            "stdout": stdout_bytes.decode("utf-8", errors="replace").strip(),
            "stderr": stderr_bytes.decode("utf-8", errors="replace").strip(),
            "returncode": process.returncode,
        }
