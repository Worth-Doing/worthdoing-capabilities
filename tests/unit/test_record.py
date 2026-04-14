"""Tests for ExecutionRecord and ExecutionLog."""

import pytest

from worthdoing_capabilities.memory.record import ExecutionLog, ExecutionRecord


def _make_record(
    name: str = "test.cap",
    status: str = "success",
    duration_ms: float = 50.0,
    cache_status: str = "disabled",
) -> ExecutionRecord:
    """Helper to create a minimal ExecutionRecord."""
    return ExecutionRecord(
        capability_name=name,
        version="0.1.0",
        input_data={"query": "hello"},
        output_data={"result": "done"},
        status=status,
        duration_ms=duration_ms,
        cache_status=cache_status,
    )


class TestExecutionRecord:
    """Test creating ExecutionRecord instances."""

    def test_create_with_all_fields(self):
        record = ExecutionRecord(
            capability_name="file.read",
            version="1.0.0",
            input_data={"path": "/tmp/test.txt"},
            output_data={"content": "hello"},
            status="success",
            duration_ms=25.5,
            cache_status="miss",
            error=None,
        )

        assert record.capability_name == "file.read"
        assert record.version == "1.0.0"
        assert record.status == "success"
        assert record.duration_ms == 25.5
        assert record.cache_status == "miss"
        assert record.error is None
        assert record.timestamp is not None

    def test_create_with_error(self):
        record = ExecutionRecord(
            capability_name="net.fetch",
            version="0.1.0",
            input_data={"url": "http://fail"},
            output_data=None,
            status="error",
            duration_ms=100.0,
            error="Connection refused",
        )

        assert record.status == "error"
        assert record.error == "Connection refused"
        assert record.output_data is None

    def test_default_values(self):
        record = ExecutionRecord(
            capability_name="cap.x",
            version="0.1.0",
        )

        assert record.input_data == {}
        assert record.output_data is None
        assert record.status == "success"
        assert record.duration_ms == 0.0
        assert record.cache_status == "disabled"
        assert record.error is None
        assert record.metadata == {}


class TestExecutionLog:
    """Test the ExecutionLog add, query, and summary operations."""

    @pytest.fixture
    def log(self):
        return ExecutionLog()

    def test_add_records(self, log):
        log.add(_make_record())
        log.add(_make_record())

        results = log.query()
        assert len(results) == 2

    def test_query_returns_all_when_no_filters(self, log):
        log.add(_make_record("cap.a"))
        log.add(_make_record("cap.b"))

        results = log.query()

        assert len(results) == 2

    def test_query_filter_by_capability_name(self, log):
        log.add(_make_record("cap.a"))
        log.add(_make_record("cap.b"))
        log.add(_make_record("cap.a"))

        results = log.query(capability_name="cap.a")

        assert len(results) == 2
        assert all(r.capability_name == "cap.a" for r in results)

    def test_query_filter_by_status(self, log):
        log.add(_make_record(status="success"))
        log.add(_make_record(status="error"))
        log.add(_make_record(status="success"))

        results = log.query(status="error")

        assert len(results) == 1
        assert results[0].status == "error"

    def test_query_with_limit(self, log):
        for i in range(10):
            log.add(_make_record(f"cap.{i}"))

        results = log.query(limit=3)

        assert len(results) == 3

    def test_query_returns_most_recent_first(self, log):
        log.add(_make_record("first"))
        log.add(_make_record("second"))
        log.add(_make_record("third"))

        results = log.query()

        assert results[0].capability_name == "third"
        assert results[2].capability_name == "first"

    def test_summary_empty_log(self, log):
        summary = log.summary()

        assert summary["total"] == 0
        assert summary["by_status"] == {}
        assert summary["by_capability"] == {}
        assert summary["avg_duration_ms"] == 0.0
        assert summary["cache_hit_rate"] == 0.0

    def test_summary_aggregation(self, log):
        log.add(_make_record("cap.a", status="success", duration_ms=100.0))
        log.add(_make_record("cap.a", status="success", duration_ms=200.0, cache_status="hit"))
        log.add(_make_record("cap.b", status="error", duration_ms=50.0))

        summary = log.summary()

        assert summary["total"] == 3
        assert summary["by_status"]["success"] == 2
        assert summary["by_status"]["error"] == 1
        assert summary["by_capability"]["cap.a"] == 2
        assert summary["by_capability"]["cap.b"] == 1
        # avg = (100 + 200 + 50) / 3 = 116.67
        assert summary["avg_duration_ms"] == pytest.approx(116.67, abs=0.01)
        # cache hit rate = 1/3 = 0.3333
        assert summary["cache_hit_rate"] == pytest.approx(0.3333, abs=0.001)
