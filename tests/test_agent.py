import pytest
import logging

from app.agent import run_with_retries
from app.parser import StructuredOutputError
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

INVALID_RESPONSE = '{"jobs": [}'

WRONG_SCHEMA_RESPONSE = """
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


def test_returns_valid_response_without_retry():
    calls = []

    def mock_llm(prompt: str) -> str:
        calls.append(prompt)
        return VALID_RESPONSE

    result = run_with_retries(
        generate_response=mock_llm,
        schema=JobSearchResult,
        prompt="Find Python developer jobs.",
        max_attempts=3,
    )

    assert len(calls) == 1
    assert result.jobs[0].title == "Python Developer"


def test_retries_after_invalid_json():
    responses = [INVALID_RESPONSE, VALID_RESPONSE]
    calls = []

    def mock_llm(prompt: str) -> str:
        calls.append(prompt)
        return responses[len(calls) - 1]

    result = run_with_retries(
        generate_response=mock_llm,
        schema=JobSearchResult,
        prompt="Find Python developer jobs.",
        max_attempts=3,
    )

    assert len(calls) == 2
    assert result.jobs[0].company == "ABC Technologies"
    assert "failed validation" in calls[1].lower()


def test_retries_after_schema_validation_error():
    responses = [WRONG_SCHEMA_RESPONSE, VALID_RESPONSE]
    calls = []

    def mock_llm(prompt: str) -> str:
        calls.append(prompt)
        return responses[len(calls) - 1]

    result = run_with_retries(
        generate_response=mock_llm,
        schema=JobSearchResult,
        prompt="Find Python developer jobs.",
        max_attempts=3,
    )

    assert len(calls) == 2
    assert result.jobs[0].experience_years == 2


def test_raises_error_when_all_attempts_fail():
    calls = []

    def mock_llm(prompt: str) -> str:
        calls.append(prompt)
        return INVALID_RESPONSE

    with pytest.raises(
        StructuredOutputError,
        match="after 3 attempts",
    ):
        run_with_retries(
            generate_response=mock_llm,
            schema=JobSearchResult,
            prompt="Find Python developer jobs.",
            max_attempts=3,
        )

    assert len(calls) == 3


def test_rejects_invalid_attempt_count():
    def mock_llm(prompt: str) -> str:
        return VALID_RESPONSE

    with pytest.raises(ValueError, match="at least 1"):
        run_with_retries(
            generate_response=mock_llm,
            schema=JobSearchResult,
            prompt="Find Python developer jobs.",
            max_attempts=0,
        )

def test_logs_successful_generation(caplog):
    caplog.set_level(
        logging.INFO,
        logger="structured_output_agent",
    )

    def mock_llm(prompt: str) -> str:
        return VALID_RESPONSE

    run_with_retries(
        generate_response=mock_llm,
        schema=JobSearchResult,
        prompt="Find Python developer jobs.",
    )

    assert "generation_started" in caplog.text
    assert "generation_succeeded" in caplog.text


def test_logs_validation_failure(caplog):
    caplog.set_level(
        logging.INFO,
        logger="structured_output_agent",
    )


def test_logs_when_all_attempts_fail(caplog):
    caplog.set_level(
        logging.ERROR,
        logger="structured_output_agent",
    )

    def mock_llm(prompt: str) -> str:
        return INVALID_RESPONSE

    with pytest.raises(StructuredOutputError):
        run_with_retries(
            generate_response=mock_llm,
            schema=JobSearchResult,
            prompt="Find Python developer jobs.",
            max_attempts=2,
        )

    assert "generation_exhausted" in caplog.text