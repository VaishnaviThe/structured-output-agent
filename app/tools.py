import logging
from typing import Any

from pydantic import BaseModel, ValidationError

from app.logging_config import setup_logging


logger = logging.getLogger("structured_output_agent")


class ToolValidationError(Exception):
    """Raised when a tool response fails validation."""


def validate_tool_response(
    raw_data: Any,
    schema: type[BaseModel],
) -> BaseModel:
    """
    Validate raw tool output against a Pydantic schema.

    Args:
        raw_data: Data returned by an external tool.
        schema: Pydantic model defining the expected data structure.

    Returns:
        A validated Pydantic model instance.

    Raises:
        ToolValidationError: If the data violates the schema.
    """

    setup_logging()

    try:
        validated_data = schema.model_validate(
            raw_data,
            strict=True,
        )

    except ValidationError as exc:
        logger.warning(
            "tool_validation_failed schema=%s error_count=%d",
            schema.__name__,
            exc.error_count(),
        )

        raise ToolValidationError(
            f"Tool response failed validation against {schema.__name__}."
        ) from exc

    logger.info(
        "tool_validation_succeeded schema=%s",
        schema.__name__,
    )

    return validated_data