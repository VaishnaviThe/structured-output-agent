from unittest.mock import MagicMock, patch

import pytest

from app.gemini_client import build_gemini_generator
from app.schemas import JobSearchResult
import httpx
from google.genai import errors

def test_build_generator_requires_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with patch("app.gemini_client.load_dotenv"):
        with pytest.raises(ValueError, match="GEMINI_API_KEY"):
            build_gemini_generator(JobSearchResult)


def test_generator_returns_gemini_response(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value.text = (
        '{"jobs": [{"title": "Python Developer", '
        '"company": "ABC Technologies", '
        '"location": "Remote", '
        '"experience_years": 2}]}'
    )

    with (
        patch("app.gemini_client.load_dotenv"),
        patch(
            "app.gemini_client.genai.Client",
            return_value=mock_client,
        ),
    ):
        generator = build_gemini_generator(JobSearchResult)
        response = generator("Find Python developer jobs.")

    assert '"Python Developer"' in response

    mock_client.models.generate_content.assert_called_once()

    call_kwargs = mock_client.models.generate_content.call_args.kwargs
    assert call_kwargs["model"] == "gemini-3.8-flash"
    assert call_kwargs["contents"] == "Find Python developer jobs."
    assert (
        call_kwargs["config"].response_mime_type
        == "application/json"
    )


def test_generator_rejects_empty_response(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value.text = None

    with (
        patch("app.gemini_client.load_dotenv"),
        patch(
            "app.gemini_client.genai.Client",
            return_value=mock_client,
        ),
    ):
        generator = build_gemini_generator(JobSearchResult)

        with pytest.raises(RuntimeError, match="empty response"):
            generator("Find Python developer jobs.")

def test_retries_after_rate_limit(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        errors.ClientError(
            429,
            {"error": {"message": "Rate limit exceeded"}},
        ),
        MagicMock(
            text='{"jobs": [{"title": "Python Developer", '
            '"company": "ABC Technologies", '
            '"location": "Remote", '
            '"experience_years": 2}]}'
        ),
    ]

    with (
        patch("app.gemini_client.load_dotenv"),
        patch(
            "app.gemini_client.genai.Client",
            return_value=mock_client,
        ),
        patch("app.gemini_client.time.sleep") as mock_sleep,
    ):
        generator = build_gemini_generator(
            JobSearchResult,
            max_api_attempts=3,
            retry_delay_seconds=1,
        )
        response = generator("Find Python developer jobs.")

    assert '"Python Developer"' in response
    assert mock_client.models.generate_content.call_count == 2
    mock_sleep.assert_called_once_with(1)


def test_retries_after_server_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        errors.ServerError(
            500,
            {"error": {"message": "Internal server error"}},
        ),
        MagicMock(text='{"jobs": []}'),
    ]

    with (
        patch("app.gemini_client.load_dotenv"),
        patch(
            "app.gemini_client.genai.Client",
            return_value=mock_client,
        ),
        patch("app.gemini_client.time.sleep") as mock_sleep,
    ):
        generator = build_gemini_generator(
            JobSearchResult,
            max_api_attempts=3,
            retry_delay_seconds=1,
        )

        response = generator("Find Python developer jobs.")

    assert response == '{"jobs": []}'
    assert mock_client.models.generate_content.call_count == 2
    mock_sleep.assert_called_once_with(1)


def test_does_not_retry_invalid_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = errors.ClientError(
        400,
        {"error": {"message": "Invalid API key"}},
    )

    with (
        patch("app.gemini_client.load_dotenv"),
        patch(
            "app.gemini_client.genai.Client",
            return_value=mock_client,
        ),
        patch("app.gemini_client.time.sleep") as mock_sleep,
    ):
        generator = build_gemini_generator(
            JobSearchResult,
            max_api_attempts=3,
        )

        with pytest.raises(errors.ClientError):
            generator("Find Python developer jobs.")

    assert mock_client.models.generate_content.call_count == 1
    mock_sleep.assert_not_called()

def test_retries_after_network_failure(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        httpx.ConnectError("Network unavailable"),
        MagicMock(text='{"jobs": []}'),
    ]

    with (
        patch("app.gemini_client.load_dotenv"),
        patch(
            "app.gemini_client.genai.Client",
            return_value=mock_client,
        ),
        patch("app.gemini_client.time.sleep") as mock_sleep,
    ):
        generator = build_gemini_generator(
            JobSearchResult,
            max_api_attempts=3,
            retry_delay_seconds=1,
        )

        response = generator("Find Python developer jobs.")

    assert response == '{"jobs": []}'
    assert mock_client.models.generate_content.call_count == 2
    mock_sleep.assert_called_once_with(1)

def test_raises_after_all_api_attempts_fail(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = errors.ServerError(
        500,
        {"error": {"message": "Internal server error"}},
    )

    with (
        patch("app.gemini_client.load_dotenv"),
        patch(
            "app.gemini_client.genai.Client",
            return_value=mock_client,
        ),
        patch("app.gemini_client.time.sleep") as mock_sleep,
    ):
        generator = build_gemini_generator(
            JobSearchResult,
            max_api_attempts=3,
            retry_delay_seconds=1,
        )

        with pytest.raises(errors.ServerError):
            generator("Find Python developer jobs.")

    assert mock_client.models.generate_content.call_count == 3

    assert mock_sleep.call_count == 2
    assert [call.args[0] for call in mock_sleep.call_args_list] == [1, 2]