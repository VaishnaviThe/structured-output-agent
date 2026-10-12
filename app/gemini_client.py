import logging
import os
import time
from collections.abc import Callable
from typing import Any

import httpx
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import BaseModel

logger = logging.getLogger("structured_output_agent")

DEFAULT_MODEL = "gemini-3.8-flash"


def _remove_unsupported_schema_fields(schema: Any) -> Any:
    """Remove JSON Schema fields unsupported by Gemini's schema API."""

    if isinstance(schema, dict):
        schema.pop("additionalProperties", None)
        schema.pop("additional_properties", None)

        for value in schema.values():
            _remove_unsupported_schema_fields(value)

    elif isinstance(schema, list):
        for item in schema:
            _remove_unsupported_schema_fields(item)

    return schema


def build_gemini_generator(
    schema: type[BaseModel],
    model: str = DEFAULT_MODEL,
    max_api_attempts: int = 3,
    retry_delay_seconds: float = 1.0,
) -> Callable[[str], str]:
    """Build a Gemini generator with retries for temporary API failures."""

    if max_api_attempts < 1:
        raise ValueError("max_api_attempts must be at least 1.")

    if retry_delay_seconds < 0:
        raise ValueError("retry_delay_seconds cannot be negative.")

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Add it to your .env file."
        )

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=30000),
    )

    response_schema = _remove_unsupported_schema_fields(
        schema.model_json_schema()
    )

    def generate_response(prompt: str) -> str:
        for attempt in range(1, max_api_attempts + 1):
            logger.info(
                "gemini_request_started model=%s attempt=%d",
                model,
                attempt,
            )

            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=response_schema,
                    ),
                )

                if not response.text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                logger.info(
                    "gemini_response_received model=%s attempt=%d",
                    model,
                    attempt,
                )

                return response.text

            except errors.ClientError as exc:
                # Retry rate limits, but not other client errors.
                if exc.code != 429 or attempt == max_api_attempts:
                    logger.exception(
                        "gemini_request_failed attempt=%d error_type=%s",
                        attempt,
                        type(exc).__name__,
                    )
                    raise

                logger.warning(
                    "gemini_rate_limited attempt=%d max_attempts=%d",
                    attempt,
                    max_api_attempts,
                )

            except (errors.ServerError, httpx.TransportError) as exc:
                if attempt == max_api_attempts:
                    logger.exception(
                        "gemini_request_failed attempt=%d error_type=%s",
                        attempt,
                        type(exc).__name__,
                    )
                    raise

                logger.warning(
                    "gemini_temporary_failure attempt=%d error_type=%s",
                    attempt,
                    type(exc).__name__,
                )

            delay = retry_delay_seconds * (2 ** (attempt - 1))

            logger.info(
                "gemini_retry_scheduled next_attempt=%d delay_seconds=%s",
                attempt + 1,
                delay,
            )

            time.sleep(delay)

        raise RuntimeError("Gemini request attempts exhausted.")

    return generate_response