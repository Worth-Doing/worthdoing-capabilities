"""Tests for capability input and output validation."""

import pytest

from worthdoing_capabilities.contracts.models import CapabilityContract
from worthdoing_capabilities.validation.validator import validate_input, validate_output


@pytest.fixture
def contract(sample_contract_data):
    """Build a CapabilityContract from the shared sample data."""
    return CapabilityContract.model_validate(sample_contract_data)


class TestValidateInput:
    """Test input validation against a contract schema."""

    def test_valid_input_passes(self, contract):
        result = validate_input(contract, {"query": "hello"})

        assert result["query"] == "hello"

    def test_missing_required_field_raises_value_error(self, contract):
        with pytest.raises(ValueError, match="query"):
            validate_input(contract, {})

    def test_wrong_type_raises_value_error(self, contract):
        with pytest.raises(ValueError, match="type"):
            validate_input(contract, {"query": 42})

    def test_extra_fields_are_passed_through(self, contract):
        """Extra fields not in the schema are passed through."""
        result = validate_input(contract, {"query": "ok", "extra": "value"})

        assert result["query"] == "ok"
        assert result["extra"] == "value"


class TestValidateOutput:
    """Test output validation against a contract schema."""

    def test_valid_output_passes(self, contract):
        result = validate_output(contract, {"result": "done"})

        assert result == {"result": "done"}

    def test_non_dict_output_raises_value_error(self, contract):
        with pytest.raises(ValueError, match="dict"):
            validate_output(contract, "not a dict")

    def test_output_with_required_fields_satisfied(self, sample_contract_data):
        """When the output schema has required fields, they must be present."""
        sample_contract_data["output"]["required"] = ["result"]
        contract = CapabilityContract.model_validate(sample_contract_data)

        # Valid - has required field
        result = validate_output(contract, {"result": "ok"})
        assert result["result"] == "ok"

        # Invalid - missing required field
        with pytest.raises(ValueError, match="result"):
            validate_output(contract, {"other": "data"})
