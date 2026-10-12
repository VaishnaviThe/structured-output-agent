import pytest

from pydantic import BaseModel, ConfigDict, Field

from app.tools import (
    ToolValidationError,
    validate_tool_response,
)


class ToolJob(BaseModel):
    """Expected structure of a job returned by a tool."""

    model_config = ConfigDict(extra="forbid", strict=True)

    title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    location: str = Field(min_length=1)
    experience_years: int = Field(ge=0, le=50)


VALID_TOOL_DATA = {
    "title": "Python Developer",
    "company": "ABC Technologies",
    "location": "Remote",
    "experience_years": 2,
}


def test_valid_tool_response():
    result = validate_tool_response(
        VALID_TOOL_DATA,
        ToolJob,
    )

    assert isinstance(result, ToolJob)
    assert result.title == "Python Developer"
    assert result.experience_years == 2


def test_rejects_negative_experience():
    invalid_data = {
        **VALID_TOOL_DATA,
        "experience_years": -5,
    }

    with pytest.raises(ToolValidationError):
        validate_tool_response(invalid_data, ToolJob)


def test_rejects_missing_fields():
    invalid_data = {
        "title": "Python Developer",
        "location": "Remote",
        "experience_years": 2,
    }

    with pytest.raises(ToolValidationError):
        validate_tool_response(invalid_data, ToolJob)


def test_rejects_wrong_data_type():
    invalid_data = {
        **VALID_TOOL_DATA,
        "experience_years": "two",
    }

    with pytest.raises(ToolValidationError):
        validate_tool_response(invalid_data, ToolJob)


def test_rejects_extra_fields():
    invalid_data = {
        **VALID_TOOL_DATA,
        "salary": "10 LPA",
    }

    with pytest.raises(ToolValidationError):
        validate_tool_response(invalid_data, ToolJob)


def test_rejects_non_dictionary_input():
    with pytest.raises(ToolValidationError):
        validate_tool_response(
            ["unexpected", "list"],
            ToolJob,
        )