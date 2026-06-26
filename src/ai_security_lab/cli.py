"""Command-line entrypoint: `ai-sec-agent --prompt "..."`."""

from __future__ import annotations

import argparse
import json
import sys

from .agent import respond
from .config import load_settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ai-sec-agent",
        description="Talk to the (intentionally vulnerable) support agent.",
    )
    parser.add_argument("--prompt", "-p", help="Single prompt; if omitted, read stdin.")
    parser.add_argument("--json", action="store_true", help="Emit the full JSON result.")
    args = parser.parse_args(argv)

    prompt = (args.prompt if args.prompt is not None else sys.stdin.read()).strip()
    if not prompt:
        parser.error("no prompt provided")

    settings = load_settings()
    result = respond(prompt, settings)

    if args.json:
        print(
            json.dumps(
                {
                    "reply": result.reply,
                    "tool_calls": result.tool_calls,
                    "guardrail_events": result.guardrail_events,
                    "blocked": result.blocked,
                    "guardrails": settings.guardrails,
                },
                indent=2,
            )
        )
    else:
        guard = "ON" if settings.guardrails else "OFF"
        print(f"[guardrails={guard}] {result.reply}")
        if result.tool_calls:
            print(f"  tools: {', '.join(result.tool_calls)}", file=sys.stderr)
        if result.guardrail_events:
            print(f"  guardrails: {'; '.join(result.guardrail_events)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
