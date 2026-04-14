"""Tests for CapabilityContract loading, validation, and serialization."""

import pytest
from pathlib import Path
from pydantic import ValidationError

from worthdoing_capabilities.contracts.models import CapabilityContract


class TestCapabilityContractFromDict:
    """Test constructing a CapabilityContract from a dictionary."""

    def test_load_from_dict_with_all_fields(self, sample_contract_data):
        contract = CapabilityContract.model_validate(sample_contract_data)

        assert contract.name == "test.capability"
        assert contract.version == "0.1.0"
        assert contract.description == "A test capability"
        assert contract.category == "testing"
        assert contract.tags == ["test"]
        assert contract.execution.executor == "python"
        assert contract.execution.function == "tests.fixtures.sample_handler.execute"
        assert contract.auth.type == "none"
        assert contract.cache.enabled is False
        assert contract.retry.max_attempts == 1
        assert contract.retry.backoff == "none"
        assert contract.timeout.seconds == 10

    def test_input_schema_populated(self, sample_contract_data):
        contract = CapabilityContract.model_validate(sample_contract_data)

        assert contract.input.type == "object"
        assert "query" in contract.input.properties
        assert contract.input.required == ["query"]

    def test_output_schema_populated(self, sample_contract_data):
        contract = CapabilityContract.model_validate(sample_contract_data)

        assert contract.output.type == "object"
        assert "result" in contract.output.properties

    def test_missing_name_raises_validation_error(self, sample_contract_data):
        del sample_contract_data["name"]

        with pytest.raises(ValidationError) as exc_info:
            CapabilityContract.model_validate(sample_contract_data)

        assert "name" in str(exc_info.value)

    def test_missing_execution_raises_validation_error(self, sample_contract_data):
        del sample_contract_data["execution"]

        with pytest.raises(ValidationError) as exc_info:
            CapabilityContract.model_validate(sample_contract_data)

        assert "execution" in str(exc_info.value)

    def test_missing_input_raises_validation_error(self, sample_contract_data):
        del sample_contract_data["input"]

        with pytest.raises(ValidationError) as exc_info:
            CapabilityContract.model_validate(sample_contract_data)

        assert "input" in str(exc_info.value)

    def test_missing_description_raises_validation_error(self, sample_contract_data):
        del sample_contract_data["description"]

        with pytest.raises(ValidationError) as exc_info:
            CapabilityContract.model_validate(sample_contract_data)

        assert "description" in str(exc_info.value)


class TestCapabilityContractFromYAML:
    """Test loading a CapabilityContract from YAML files."""

    def test_load_valid_contract_yaml(self, fixtures_dir):
        path = fixtures_dir / "valid_contract.yaml"
        contract = CapabilityContract.from_yaml(path)

        assert contract.name == "test.sample"
        assert contract.version == "0.1.0"
        assert contract.description == "A sample test capability for unit testing"
        assert contract.category == "testing"
        assert "test" in contract.tags
        assert "sample" in contract.tags
        assert contract.execution.executor == "python"
        assert contract.execution.function == "tests.fixtures.sample_handler.execute"

    def test_load_invalid_contract_yaml_raises(self, fixtures_dir):
        path = fixtures_dir / "invalid_contract.yaml"

        with pytest.raises(ValidationError):
            CapabilityContract.from_yaml(path)

    def test_load_nonexistent_file_raises(self, tmp_path):
        path = tmp_path / "does_not_exist.yaml"

        with pytest.raises(FileNotFoundError):
            CapabilityContract.from_yaml(path)


class TestCapabilityContractSerialization:
    """Test round-trip serialization of CapabilityContract."""

    def test_serialization_roundtrip(self, sample_contract_data, tmp_path):
        original = CapabilityContract.model_validate(sample_contract_data)
        yaml_path = tmp_path / "roundtrip.yaml"

        original.to_yaml(yaml_path)
        assert yaml_path.exists()

        reloaded = CapabilityContract.from_yaml(yaml_path)

        assert reloaded.name == original.name
        assert reloaded.version == original.version
        assert reloaded.description == original.description
        assert reloaded.category == original.category
        assert reloaded.tags == original.tags
        assert reloaded.execution.executor == original.execution.executor
        assert reloaded.execution.function == original.execution.function
        assert reloaded.auth.type == original.auth.type
        assert reloaded.cache.enabled == original.cache.enabled
        assert reloaded.retry.max_attempts == original.retry.max_attempts
        assert reloaded.timeout.seconds == original.timeout.seconds

    def test_model_dump_produces_dict(self, sample_contract_data):
        contract = CapabilityContract.model_validate(sample_contract_data)
        dumped = contract.model_dump(mode="json", exclude_none=True)

        assert isinstance(dumped, dict)
        assert dumped["name"] == "test.capability"
        assert dumped["execution"]["executor"] == "python"
