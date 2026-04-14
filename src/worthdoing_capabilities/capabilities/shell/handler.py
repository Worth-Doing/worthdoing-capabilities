"""Shell capability handler.

This capability uses the ShellExecutor directly via the ``execution.command``
template in capability.yaml. No Python handler is needed at runtime; the
ShellExecutor resolves ``{{ input.command }}`` and runs the process.

This file exists for documentation and testing purposes.
"""


async def execute(input_data: dict) -> dict:
    """Placeholder -- the shell executor handles this capability.

    This function is not called in production; the ShellExecutor processes
    the command template from capability.yaml directly.
    """
    import asyncio

    command = input_data["command"]

    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    return {
        "stdout": stdout.decode("utf-8", errors="replace").strip(),
        "stderr": stderr.decode("utf-8", errors="replace").strip(),
        "returncode": proc.returncode,
    }
