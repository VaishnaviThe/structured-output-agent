import pytest

from app.parser import (
    StructuredOutputError,
    parse_structured_output,
)
from app.schemas import JobSearchResult


VALID_RESPONSE = """
{
    "jobs": [
        {
            "title": "Python Developer",
            "company": "ABC Technologies",
            "location": "Remote",
            "experience_years": 2
        }
    ]
}
"""


def test_parse_valid_response():
    result = parse_structured_output(
        VALID_RESPONSE,
        JobSearchResult,
    )

    assert isinstance(result, JobSearchResult)
    assert result.jobs[0].title == "Python Developer"
    assert result.jobs[0].experience_years == 2


def test_reject_invalid_json():
    raw_output = '{"jobs": [}'

    with pytest.raises(StructuredOutputError, match="Invalid JSON"):
        parse_structured_output(raw_output, JobSearchResult)


def test_reject_missing_required_field():
    raw_output = """
    {
        "jobs": [
            {
                "title": "Python Developer",
                "location": "Remote",
                "experience_years": 2
            }
        ]
    }
    """

    with pytest.raises(
        StructuredOutputError,
        match="Schema validation failed",
    ):
        parse_structured_output(raw_output, JobSearchResult)


def test_reject_wrong_data_type():
    raw_output = """
    {
        "jobs": [
            {
                "title": "Python Developer",
                "company": "ABC Technologies",
                "location": "Remote",
                "experience_years": "two"
            }
        ]
    }
    """

    with pytest.raises(
        StructuredOutputError,
        match="Schema validation failed",
    ):
        parse_structured_output(raw_output, JobSearchResult)


def test_reject_extra_field():
    raw_output = """
    {
        "jobs": [
            {
                "title": "Python Developer",
                "company": "ABC Technologies",
                "location": "Remote",
                "experience_years": 2,
                "salary": "10 LPA"
            }
        ]
    }
    """

    with pytest.raises(
        StructuredOutputError,
        match="Schema validation failed",
    ):
        parse_structured_output(raw_output, JobSearchResult)


def test_reject_empty_response():
    with pytest.raises(
        StructuredOutputError,
        match="empty or not a string",
    ):
        parse_structured_output("", JobSearchResult)