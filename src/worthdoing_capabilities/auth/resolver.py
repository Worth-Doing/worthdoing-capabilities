"""Authentication resolver for WorthDoing capability contracts."""

from __future__ import annotations

import os

from worthdoing_capabilities.contracts.models import AuthConfig


def resolve_auth(auth_config: AuthConfig, capability_name: str = "") -> dict[str, str]:
    """Resolve authentication configuration into HTTP headers.

    Reads credentials from environment variables as specified in the
    auth configuration and returns the appropriate headers.

    Args:
        auth_config: The authentication configuration from a capability contract.

    Returns:
        A dict of HTTP headers to include in the request.

    Raises:
        EnvironmentError: If the required environment variable is not set.
    """
    if auth_config.type == "none":
        return {}

    if not auth_config.env:
        raise ValueError(
            f"Auth type '{auth_config.type}' requires an 'env' field "
            "specifying the environment variable name."
        )

    value = os.environ.get(auth_config.env)
    if value is None:
        raise EnvironmentError(
            f"Environment variable '{auth_config.env}' is not set. "
            f"It is required for auth type '{auth_config.type}'."
        )

    if auth_config.type == "bearer":
        return {"Authorization": f"Bearer {value}"}
    elif auth_config.type == "api_key":
        return {"X-API-Key": value}

    return {}
