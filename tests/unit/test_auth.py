"""Tests for authentication resolution."""

import pytest

from worthdoing_capabilities.contracts.models import AuthConfig
from worthdoing_capabilities.auth.resolver import resolve_auth


class TestResolveAuth:
    """Test resolve_auth for all auth types."""

    def test_type_none_returns_empty_dict(self):
        config = AuthConfig(type="none")

        result = resolve_auth(config, capability_name="test.cap")

        assert result == {}

    def test_api_key_reads_env_var(self, monkeypatch):
        monkeypatch.setenv("MY_API_KEY", "secret-key-123")
        config = AuthConfig(type="api_key", env="MY_API_KEY")

        result = resolve_auth(config, capability_name="test.cap")

        assert result == {"X-API-Key": "secret-key-123"}

    def test_bearer_reads_env_var(self, monkeypatch):
        monkeypatch.setenv("MY_BEARER_TOKEN", "tok-abc")
        config = AuthConfig(type="bearer", env="MY_BEARER_TOKEN")

        result = resolve_auth(config, capability_name="test.cap")

        assert result == {"Authorization": "Bearer tok-abc"}

    def test_missing_env_var_raises_environment_error(self, monkeypatch):
        monkeypatch.delenv("NONEXISTENT_VAR", raising=False)
        config = AuthConfig(type="api_key", env="NONEXISTENT_VAR")

        with pytest.raises(EnvironmentError, match="NONEXISTENT_VAR"):
            resolve_auth(config, capability_name="test.cap")

    def test_api_key_without_env_field_raises_value_error(self):
        config = AuthConfig(type="api_key")

        with pytest.raises(ValueError, match="env"):
            resolve_auth(config, capability_name="test.cap")

    def test_bearer_without_env_field_raises_value_error(self):
        config = AuthConfig(type="bearer")

        with pytest.raises(ValueError, match="env"):
            resolve_auth(config, capability_name="test.cap")
