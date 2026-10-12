import json

from app.agent import run_with_retries
from app.gemini_client import build_gemini_generator
from app.schemas import JobSearchResult


def main() -> None:
    print("=" * 45)
    print("       STRUCTURED OUTPUT AGENT")
    print("=" * 45)
    print("Generate structured job-search data using Gemini.")
    print("Type 'exit' or 'quit' to stop.\n")

    try:
        generate_response = build_gemini_generator(JobSearchResult)
    except (ValueError, Exception) as exc:
        print(f"Failed to initialize Gemini client: {exc}")
        return

    while True:
        try:
            prompt = input("Enter your prompt: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting agent. Goodbye!")
            break

        if prompt.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not prompt:
            print("Prompt cannot be empty. Please try again.\n")
            continue

        try:
            print("\nGenerating response...\n")

            result = run_with_retries(
                generate_response=generate_response,
                schema=JobSearchResult,
                prompt=prompt,
                max_attempts=3,
            )

            print("Validated structured output:\n")
            print(json.dumps(result.model_dump(), indent=2))
            print()

        except Exception as exc:
            print(f"Could not generate a valid response: {exc}\n")


if __name__ == "__main__":
    main()