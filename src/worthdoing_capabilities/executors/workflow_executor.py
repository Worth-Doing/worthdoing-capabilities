"""Workflow executor for chaining WorthDoing capabilities."""

from __future__ import annotations

import re
from typing import Any, TYPE_CHECKING

from worthdoing_capabilities.executors.base import BaseExecutor

if TYPE_CHECKING:
    from worthdoing_capabilities.runtime.engine import CapabilityRuntime


def _template_steps(value: Any, steps_results: list[dict]) -> Any:
    """Replace ``{{ steps.N.field }}`` placeholders with previous step outputs.

    Supports dotted access into nested dicts, e.g. ``{{ steps.0.data.name }}``.

    Args:
        value: The value to template (string, dict, list, or scalar).
        steps_results: List of result dicts from previously executed steps.

    Returns:
        The templated value with placeholders replaced.
    """
    if isinstance(value, str):
        def _replacer(match: re.Match) -> str:
            key = match.group(1).strip()
            if key.startswith("steps."):
                parts = key.split(".", 2)  # steps, N, field_path
                if len(parts) < 3:
                    return match.group(0)
                try:
                    step_index = int(parts[1])
                except ValueError:
                    return match.group(0)
                if step_index < 0 or step_index >= len(steps_results):
                    return match.group(0)

                # Navigate into the result dict via dotted field path
                result = steps_results[step_index]
                field_parts = parts[2].split(".")
                current: Any = result
                for fp in field_parts:
                    if isinstance(current, dict) and fp in current:
                        current = current[fp]
                    else:
                        return match.group(0)
                return str(current)
            return match.group(0)

        return re.sub(r"\{\{\s*(.+?)\s*\}\}", _replacer, value)

    if isinstance(value, dict):
        return {k: _template_steps(v, steps_results) for k, v in value.items()}

    if isinstance(value, list):
        return [_template_steps(item, steps_results) for item in value]

    return value


class WorkflowExecutor(BaseExecutor):
    """Executor that chains multiple capabilities together sequentially.

    Each step in the workflow can reference outputs from previous steps via
    ``{{ steps.N.field }}`` templating in its ``input_map``.

    Args:
        runtime: A reference to the CapabilityRuntime used to execute
            individual capabilities.
    """

    def __init__(self, runtime: CapabilityRuntime) -> None:
        self._runtime = runtime

    @property
    def executor_type(self) -> str:
        return "workflow"

    async def execute(
        self, config: dict, input_data: dict, auth_headers: dict
    ) -> dict:
        """Execute a multi-step workflow sequentially.

        Reads ``steps`` from *config* -- a list of dicts each containing:

        - ``capability``: the name of the capability to execute
        - ``input_map``: a dict mapping input field names to values, which
          may include ``{{ steps.N.field }}`` references to previous outputs

        Args:
            config: Execution configuration with a ``steps`` list.
            input_data: Initial input data available to the first step.
            auth_headers: Authentication headers (passed through to the
                runtime for individual capability execution).

        Returns:
            The output dict from the final step, with an additional
            ``__intermediate_results__`` key containing all step outputs.

        Raises:
            ValueError: If the ``steps`` field is missing or empty.
            RuntimeError: If any step fails.
        """
        steps: list[dict] | None = config.get("steps")
        if not steps:
            raise ValueError(
                "WorkflowExecutor requires a non-empty 'steps' list in config."
            )

        steps_results: list[dict] = []

        for i, step in enumerate(steps):
            capability_name: str | None = step.get("capability")
            if not capability_name:
                raise ValueError(
                    f"Workflow step {i} is missing a 'capability' field."
                )

            # Build input for this step from input_map
            input_map: dict = step.get("input_map", {})

            # Template the input_map with previous step results
            templated_map = _template_steps(input_map, steps_results)

            # Also template with the original input_data for {{ input.xxx }}
            resolved_input: dict[str, Any] = {}
            for key, val in templated_map.items():
                if isinstance(val, str):
                    resolved_input[key] = re.sub(
                        r"\{\{\s*input\.(\w+)\s*\}\}",
                        lambda m: str(input_data.get(m.group(1), m.group(0))),
                        val,
                    )
                else:
                    resolved_input[key] = val

            try:
                result = await self._runtime.run_async(
                    capability_name,
                    resolved_input,
                    bypass_cache=True,
                )
            except Exception as exc:
                raise RuntimeError(
                    f"Workflow step {i} ('{capability_name}') failed: {exc}"
                ) from exc

            steps_results.append(result)

        # Return final step output, enriched with intermediate results
        final_output = dict(steps_results[-1]) if steps_results else {}
        final_output["__intermediate_results__"] = steps_results
        return final_output
