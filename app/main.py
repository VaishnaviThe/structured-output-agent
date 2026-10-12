import json

from app.agent import run_with_retries
from app.gemini_client import build_gemini_generator
from app.schemas import JobSearchResult


def main() -> None:
    prompt = """
    Find 3 example job listings for Python developers in India.

    Return a JSON object containing a "jobs" list.
    Each job must include:
    - title: string
    - company: string
    - location: string
    - experience_years: integer between 0 and 50

    Return only structured data that follows the required schema.
    """

    generate_response = build_gemini_generator(JobSearchResult)

    result = run_with_retries(
        generate_response=generate_response,
        schema=JobSearchResult,
        prompt=prompt,
        max_attempts=3,
    )

    print("\nValidated structured output:\n")
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    main()