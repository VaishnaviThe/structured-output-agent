import logging
from collections.abc import Callable

from pydantic import BaseModel

from app.logging_config import setup_logging
from app.parser import (
    StructuredOutputError,
    parse_structured_output,
)


logger = logging.getLogger("structured_output_agent")


def run_with_retries(
    generate_response: Callable[[str], str],
    schema: type[BaseModel],
    prompt: str,
    max_attempts: int = 3,
) -> BaseModel:
    """
    Generate an LLM response, validate it, and retry output failures.

    Args:
        generate_response: Callable accepting a prompt and returning text.
        schema: Pydantic model used to validate the response.
        prompt: Initial instruction sent to the LLM.
        max_attempts: Maximum total generation attempts.

    Returns:
        A validated Pydantic model instance.

    Raises:
        ValueError: If max_attempts is less than one.
        StructuredOutputError: If all attempts produce invalid output.
    """

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1.")

    setup_logging()

    current_prompt = prompt
    last_error = None

    for attempt in range(1, max_attempts + 1):
        logger.info(
            "generation_started attempt=%d max_attempts=%d",
            attempt,
            max_attempts,
        )

        try:
            raw_output = generate_response(current_prompt)

            result = parse_structured_output(raw_output, schema)

        except StructuredOutputError as exc:
            last_error = exc

            logger.warning(
                "validation_failed attempt=%d error_type=%s",
                attempt,
                type(exc).__name__,
            )

            if attempt == max_attempts:
                break

            current_prompt = (
                f"{prompt}\n\n"
                "Your previous response failed validation.\n"
                f"Error: {exc}\n\n"
                "Return a corrected response as valid JSON only. "
                "Follow the required schema exactly. "
                "Do not include Markdown fences or explanations."
            )

            continue

        except Exception:
            logger.exception(
                "generation_failed attempt=%d error_type=unexpected",
                attempt,
            )
            raise

        logger.info(
            "generation_succeeded attempt=%d",
            attempt,
        )

        return result

    logger.error(
        "generation_exhausted max_attempts=%d last_error_type=%s",
        max_attempts,
        type(last_error).__name__ if last_error else "unknown",
    )

    raise StructuredOutputError(
        f"Failed to generate valid structured output after "
        f"{max_attempts} attempts. Last error: {last_error}"
    ) from last_error