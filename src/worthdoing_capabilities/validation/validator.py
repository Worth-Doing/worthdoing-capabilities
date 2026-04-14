"""Input and output validation for WorthDoing capability contracts."""

from __future__ import annotations

from typing import Any

from worthdoing_capabilities.contracts.models import CapabilityContract


def validate_input(contract: CapabilityContract, input_data: dict) -> dict:
    """Validate input data against the capability contract's input schema.

    Checks that all required fields are present and that provided fields match
    the declared types. Returns the validated (and possibly coerced) input dict.

    Args:
        contract: The capability contract defining the expected input schema.
        input_data: The raw input data to validate.

    Returns:
        A validated copy of the input data.

    Raises:
        ValueError: If required fields are missing or types do not match.
    """
    schema = contract.input
    validated: dict[str, Any] = {}

    # Check required fields
    for field_name in schema.required:
        if field_name not in input_data:
            raise ValueError(
                f"Missing required input field '{field_name}' for capability '{contract.name}'"
            )

    # Validate and copy provided fields
    for field_name, field_spec in schema.properties.items():
        if field_name in input_data:
            value = input_data[field_name]
            expected_type = field_spec.get("type") if isinstance(field_spec, dict) else None
            if expected_type and not _check_type(value, expected_type):
                raise ValueError(
                    f"Input field '{field_name}' expected type '{expected_type}', "
                    f"got '{type(value).__name__}' for capability '{contract.name}'"
                )
            validated[field_name] = value
        elif field_name in schema.required:
            raise ValueError(
                f"Missing required input field '{field_name}' for capability '{contract.name}'"
            )

    # Pass through any extra fields not in the schema
    for field_name, value in input_data.items():
        if field_name not in validated:
            validated[field_name] = value

    return validated


def validate_output(contract: CapabilityContract, output_data: dict) -> dict:
    """Validate output data against the capability contract's output schema.

    Performs a lightweight check that required output fields are present.

    Args:
        contract: The capability contract defining the expected output schema.
        output_data: The raw output data to validate.

    Returns:
        The validated output data.

    Raises:
        ValueError: If required output fields are missing.
    """
    if not isinstance(output_data, dict):
        raise ValueError(
            f"Output for capability '{contract.name}' must be a dict, "
            f"got '{type(output_data).__name__}'"
        )

    schema = contract.output
    for field_name in schema.required:
        if field_name not in output_data:
            raise ValueError(
                f"Missing required output field '{field_name}' from capability '{contract.name}'"
            )

    return output_data


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_TYPE_MAP: dict[str, type | tuple[type, ...]] = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
}


def _check_type(value: Any, expected: str) -> bool:
    """Return True if *value* matches the JSON Schema *expected* type string."""
    python_type = _TYPE_MAP.get(expected)
    if python_type is None:
        # Unknown type -- accept anything
        return True
    return isinstance(value, python_type)


# ---------------------------------------------------------------------------
# Contract-level validation
# ---------------------------------------------------------------------------


def validate_contract(contract: CapabilityContract) -> list[str]:
    """Validate a capability contract definition and return warnings.

    Checks for common issues such as missing descriptions, empty schemas,
    and misconfigured execution settings.

    Args:
        contract: The capability contract to validate.

    Returns:
        A list of warning messages. An empty list means no issues found.
    """
    warnings: list[str] = []

    # Check basic metadata
    if not contract.description or len(contract.description.strip()) < 10:
        warnings.append("Description is missing or too short (minimum 10 characters).")

    if not contract.tags:
        warnings.append("No tags defined. Tags help with discoverability.")

    if not contract.category:
        warnings.append("Category is empty.")

    # Check input schema
    if not contract.input.properties:
        warnings.append("Input schema has no properties defined.")

    # Check output schema
    if not contract.output.properties:
        warnings.append("Output schema has no properties defined.")

    # Check execution config
    executor = contract.execution.executor
    if executor == "http" and not contract.execution.url:
        warnings.append("HTTP executor requires a 'url' in execution config.")

    if executor == "http" and not contract.execution.method:
        warnings.append("HTTP executor should specify a 'method' (GET, POST, etc.).")

    if executor == "python" and not contract.execution.function:
        warnings.append("Python executor requires a 'function' in execution config.")

    if executor == "shell" and not contract.execution.command:
        warnings.append("Shell executor requires a 'command' in execution config.")

    if executor in ("chain", "workflow") and not contract.execution.steps:
        warnings.append("Chain/workflow executor requires 'steps' in execution config.")

    # Check auth config
    if contract.auth.type != "none" and not contract.auth.env:
        warnings.append(
            f"Auth type is '{contract.auth.type}' but no 'env' variable is specified."
        )

    # Check retry config
    if contract.retry.max_attempts > 1 and contract.retry.backoff == "none":
        warnings.append(
            "Retry max_attempts > 1 but backoff is 'none'. Consider setting a backoff strategy."
        )

    # Check planner hints
    if contract.planner is None:
        warnings.append("No planner hints defined. Planner hints improve agent decision-making.")

    return warnings
