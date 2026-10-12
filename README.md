# Structured Output Agent

A Python application that uses Google's Gemini API to generate structured,
validated JSON outputs using Pydantic schemas.

The application supports job-search data generation and task summarization.
It includes schema validation, retry handling, error logging, and automated tests.

## Features

- Generate structured job-search results.
- Generate structured task summaries.
- Validate LLM responses using Pydantic.
- Reject missing fields, invalid values, and unexpected fields.
- Retry generation when responses contain invalid JSON or fail validation.
- Retry transient Gemini API and network errors.
- Log generation attempts and validation failures.
- Interactive command-line interface.
- Automated tests using pytest.

## Tech Stack

- Python 3.12+
- Google Gemini API
- `google-genai`
- Pydantic
- `python-dotenv`
- pytest

## Project Structure

```text
structured-output-agent/
├── app/
│   ├── __init__.py
│   ├── schemas.py
│   ├── parser.py
│   ├── tools.py
│   ├── agent.py
│   ├── logging_config.py
│   ├── gemini_client.py
│   └── main.py
├── tests/
├── logs/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md