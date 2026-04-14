"""Execution records and logging for capability runs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class ExecutionRecord(BaseModel):
    """Record of a single capability execution."""

    capability_name: str
    version: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: Optional[dict[str, Any]] = None
    status: Literal["success", "error", "timeout", "cache_hit"] = "success"
    duration_ms: float = 0.0
    cache_status: Literal["hit", "miss", "bypass", "disabled"] = "disabled"
    error: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionLog:
    """In-memory log of execution records with querying capabilities."""

    def __init__(self) -> None:
        self._records: list[ExecutionRecord] = []

    def add(self, record: ExecutionRecord) -> None:
        """Add an execution record to the log.

        Args:
            record: The execution record to store.
        """
        self._records.append(record)

    def query(
        self,
        capability_name: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> list[ExecutionRecord]:
        """Query execution records with optional filters.

        Args:
            capability_name: Filter by capability name (exact match).
            status: Filter by execution status.
            limit: Maximum number of records to return (most recent first).

        Returns:
            A list of matching execution records, ordered most recent first.
        """
        results = self._records

        if capability_name is not None:
            results = [r for r in results if r.capability_name == capability_name]

        if status is not None:
            results = [r for r in results if r.status == status]

        # Return most recent first, limited
        return list(reversed(results))[:limit]

    def summary(self) -> dict[str, Any]:
        """Generate a summary of all execution records.

        Returns:
            A dictionary with total count, counts by status, counts by
            capability, average duration, and cache hit rate.
        """
        total = len(self._records)

        if total == 0:
            return {
                "total": 0,
                "by_status": {},
                "by_capability": {},
                "avg_duration_ms": 0.0,
                "cache_hit_rate": 0.0,
            }

        by_status: dict[str, int] = {}
        by_capability: dict[str, int] = {}
        total_duration = 0.0
        cache_hits = 0

        for record in self._records:
            by_status[record.status] = by_status.get(record.status, 0) + 1
            by_capability[record.capability_name] = (
                by_capability.get(record.capability_name, 0) + 1
            )
            total_duration += record.duration_ms
            if record.cache_status == "hit":
                cache_hits += 1

        return {
            "total": total,
            "by_status": by_status,
            "by_capability": by_capability,
            "avg_duration_ms": round(total_duration / total, 2),
            "cache_hit_rate": round(cache_hits / total, 4),
        }
