# Structured Output Agent

A Python-based AI agent that uses Google's Gemini API to generate structured JSON responses and validates them using Pydantic.

The project demonstrates reliable LLM output processing through schema validation, retry mechanisms, API error handling, and logging.

## Features

- **Gemini API Integration:** Generate AI responses using Google's Gemini models.
- **Structured Output:** Request JSON responses that follow a defined schema.
- **Pydantic Validation:** Validate generated data against strict models.
- **Retry Mechanism:** Retry generation when the output fails validation.
- **API Retry Handling:** Retry eligible temporary API and network failures.
- **Error Handling:** Handle malformed JSON, schema validation errors, and API failures.
- **Logging:** Record generation attempts, validation failures, and API errors.
- **Tool Response Validation:** Validate tool outputs against Pydantic schemas.
- **Automated Tests:** Test core functionality using pytest.

## Tech Stack

- Python 3.12+
- Google Gen AI SDK
- Gemini API
- Pydantic
- pytest
- python-dotenv
- httpx

## Project Structure

```text
structured-output-agent/
├── app/
│   ├── __init__.py
│   ├── agent.py
│   ├── gemini_client.py
│   ├── logging_config.py
│   ├── main.py
│   ├── parser.py
│   ├── schemas.py
│   └── tools.py
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_gemini_client.py
│   ├── test_parser.py
│   ├── test_schemas.py
│   └── test_tools.py
├── logs/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md