import json

from app.agent import run_with_retries
from app.gemini_client import build_gemini_generator
from app.schemas import JobSearchResult, TaskSummary


def main() -> None:
    print("=" * 45)
    print("       STRUCTURED OUTPUT AGENT")
    print("=" * 45)

    schema_options = {
        "1": ("Job Search", JobSearchResult),
        "2": ("Task Summary", TaskSummary),
    }

    while True:
        print("\nChoose an option:")
        print("1. Job Search")
        print("2. Task Summary")
        print("3. Exit")

        try:
            choice = input("\nEnter your choice: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if choice == "3":
            print("Goodbye!")
            break

        if choice not in schema_options:
            print("Invalid choice. Please select 1, 2, or 3.")
            continue

        mode_name, schema = schema_options[choice]

        try:
            prompt = input(
                f"\nEnter your {mode_name.lower()} prompt: "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not prompt:
            print("Prompt cannot be empty. Please try again.")
            continue

        try:
            print("\nGenerating response...")

            generate_response = build_gemini_generator(schema)

            result = run_with_retries(
                generate_response=generate_response,
                schema=schema,
                prompt=prompt,
                max_attempts=3,
            )

            print("\nValidated structured output:\n")
            print(json.dumps(result.model_dump(mode="json"), indent=2))

        except Exception as exc:
            print(f"\nCould not generate a valid response: {exc}")

        print()


if __name__ == "__main__":
    main()