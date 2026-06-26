"""
AI-assisted test case generation from banking analytics requirements.

Sends each plain-text requirement from requirements_input.txt to the Claude API
and writes the generated pytest functions to ai_testing/generated/ai_generated_tests.py.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python ai_testing/test_generator.py

If no API key is set, see ai_testing/generated/sample_ai_tests.py for
pre-generated example output that was produced and reviewed manually.
"""
import os
import sys
from pathlib import Path

REQUIREMENTS_FILE = Path("ai_testing/requirements_input.txt")
OUTPUT_FILE       = Path("ai_testing/generated/ai_generated_tests.py")

SYSTEM_PROMPT = (
    "You are a QA automation engineer specialising in banking analytics data validation. "
    "Given a plain-text business requirement, generate exactly one pytest test function "
    "that validates the requirement against a pandas DataFrame named 'df'. "
    "Use only pandas and standard Python — no mocking, no external libraries. "
    "Output only valid Python code. No explanations, no markdown fences."
)


def generate_test(requirement: str, client) -> str:
    msg = client.messages.create(
        model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Requirement:\n{requirement.strip()}"
        }],
    )
    return msg.content[0].text.strip()


def main():
    try:
        import anthropic
    except ImportError:
        print("anthropic package not installed. Run: pip install anthropic")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "ANTHROPIC_API_KEY not set.\n"
            "See ai_testing/generated/sample_ai_tests.py for pre-generated output."
        )
        sys.exit(0)

    client = anthropic.Anthropic(api_key=api_key)
    raw    = REQUIREMENTS_FILE.read_text().strip()
    reqs   = [r.strip() for r in raw.split("\n\n") if r.strip()]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        '"""',
        "AI-generated test cases produced by test_generator.py.",
        "Each function was reviewed before being committed.",
        '"""',
        "import pandas as pd",
        "",
    ]

    for req in reqs:
        print(f"Generating test for: {req[:70]}...")
        code = generate_test(req, client)
        lines.append(f"# Requirement: {req[:100]}")
        lines.append(code)
        lines.append("")

    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"\nSaved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
