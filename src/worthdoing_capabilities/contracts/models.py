"""Pydantic models for the WorthDoing capability contract system."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Optional

import yaml
from pydantic import BaseModel, Field


class InputSchema(BaseModel):
    """Schema definition for capability inputs."""

    type: str = "object"
    properties: dict[str, Any] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)


class OutputSchema(BaseModel):
    """Schema definition for capability outputs."""

    type: str = "object"
    properties: dict[str, Any] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)


class ExecutionConfig(BaseModel):
    """Configuration for how a capability is executed."""

    executor: str
    method: Optional[str] = None
    url: Optional[str] = None
    query: Optional[dict[str, Any]] = None
    function: Optional[str] = None
    command: Optional[str] = None
    steps: Optional[list[dict[str, Any]]] = None


class AuthConfig(BaseModel):
    """Authentication configuration for a capability."""

    type: Literal["none", "api_key", "bearer"] = "none"
    env: Optional[str] = None


class CacheConfig(BaseModel):
    """Cache configuration for a capability."""

    enabled: bool = False
    ttl_seconds: int = 60


class RetryConfig(BaseModel):
    """Retry configuration for a capability."""

    max_attempts: int = 1
    backoff: Literal["none", "linear", "exponential"] = "none"


class TimeoutConfig(BaseModel):
    """Timeout configuration for a capability."""

    seconds: int = 30


class PlannerHints(BaseModel):
    """Hints for AI planners on when and how to use a capability."""

    when_to_use: list[str] = Field(default_factory=list)
    when_not_to_use: list[str] = Field(default_factory=list)
    latency_hint: str = "low"
    cost_hint: str = "low"


class CapabilityContract(BaseModel):
    """Full contract definition for a WorthDoing capability."""

    name: str
    version: str
    description: str
    category: str
    tags: list[str] = Field(default_factory=list)
    input: InputSchema
    output: OutputSchema
    execution: ExecutionConfig
    auth: AuthConfig = Field(default_factory=lambda: AuthConfig(type="none"))
    cache: CacheConfig = Field(default_factory=CacheConfig)
    retry: RetryConfig = Field(default_factory=RetryConfig)
    timeout: TimeoutConfig = Field(default_factory=TimeoutConfig)
    planner: Optional[PlannerHints] = None

    @classmethod
    def from_yaml(cls, path: Path) -> CapabilityContract:
        """Load a capability contract from a YAML file.

        Args:
            path: Path to the YAML file.

        Returns:
            A validated CapabilityContract instance.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
            ValueError: If the YAML content is invalid.
        """
        if not path.exists():
            raise FileNotFoundError(f"Contract file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Invalid contract file: expected a YAML mapping, got {type(data).__name__}")

        return cls.model_validate(data)

    def to_yaml(self, path: Path) -> None:
        """Serialize the capability contract to a YAML file.

        Args:
            path: Path where the YAML file will be written.
        """
        path.parent.mkdir(parents=True, exist_ok=True)

        data = self.model_dump(mode="json", exclude_none=True)

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
