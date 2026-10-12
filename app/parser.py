import json

from pydantic import BaseModel, ValidationError


class StructuredOutputError(Exception):
    """Raised when an LLM response cannot be parsed or validated."""


def parse_structured_output(
    raw_output: str,
    schema: type[BaseModel],
) -> BaseModel:
    """
    Parse raw JSON and validate it against a Pydantic schema.

    Args:
        raw_output: Raw JSON string returned by the LLM.
        schema: Pydantic model used to validate the response.

    Returns:
        A validated Pydantic model instance.

    Raises:
        StructuredOutputError: If JSON parsing or schema validation fails.
    """

    if not isinstance(raw_output, str) or not raw_output.strip():
        raise StructuredOutputError("LLM response is empty or not a string.")

    try:
        data = json.loads(raw_output)

    except json.JSONDecodeError as exc:
        raise StructuredOutputError(
            f"Invalid JSON at line {exc.lineno}, column {exc.colno}."
        ) from exc

    try:
        return schema.model_validate(data, strict=False)

    except ValidationError as exc:
        raise StructuredOutputError(
            f"Schema validation failed: {exc}"
        ) from exc