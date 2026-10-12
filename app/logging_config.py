import logging
from pathlib import Path


def setup_logging() -> logging.Logger:
    """Configure logging to write agent events to a file."""

    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("structured_output_agent")
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if setup_logging() is called repeatedly.
    if not any(
        getattr(handler, "_agent_file_handler", False)
        for handler in logger.handlers
    ):
        file_handler = logging.FileHandler(
            log_dir / "agent.log",
            encoding="utf-8",
        )

        file_handler._agent_file_handler = True

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger