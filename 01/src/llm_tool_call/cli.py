"""Command-line entry point."""

import argparse
import sys

from openai import OpenAIError

from llm_tool_call.agent import ask
from llm_tool_call.config import Settings

DEFAULT_QUESTION = "Jedeme na chalupu, 7 lidí, 6 hodin, pořádná žízeň. Kolik piv koupit a za kolik?"


def _use_utf8_output() -> None:
    """Windows terminals default to a legacy code page that cannot encode Czech."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    _use_utf8_output()
    parser = argparse.ArgumentParser(
        prog="llm-tool-call",
        description="Ask a local LLM a question it can only answer by calling a Python tool.",
    )
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION, help="question to ask")
    args = parser.parse_args(argv)

    settings = Settings.from_env()
    print(f"Model:    {settings.model} @ {settings.base_url}")
    print(f"Question: {args.question}\n")

    try:
        answer = ask(args.question, settings)
    except OpenAIError as exc:
        print(f"Cannot reach the LLM endpoint at {settings.base_url}: {exc}", file=sys.stderr)
        print("Is the LM Studio server running? Start it with: lms server start", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    for call in answer.tool_calls:
        print(f"  tool  {call.name}({call.arguments}) -> {call.result}")

    print(f"\nAnswer:   {answer.text}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
