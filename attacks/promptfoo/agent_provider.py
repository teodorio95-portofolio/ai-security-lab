"""promptfoo custom provider that targets the vulnerable agent.

promptfoo (node) imports this file and calls `call_api`. Because the package is
installed in the project venv (`uv sync`), absolute imports work regardless of
where promptfoo runs the file from. Point promptfoo at the venv interpreter
with PROMPTFOO_PYTHON (the Makefile does this).

The provider reads the GUARDRAILS env var like every other entrypoint, so the
same config runs before/after defenses by toggling one variable.
"""

from __future__ import annotations

from typing import Any

from ai_security_lab.agent import respond
from ai_security_lab.config import load_settings


def call_api(
    prompt: str,
    options: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    settings = load_settings()
    result = respond(prompt, settings)
    return {
        "output": result.reply,
        "metadata": {
            "tool_calls": result.tool_calls,
            "guardrail_events": result.guardrail_events,
            "blocked": result.blocked,
            "guardrails": settings.guardrails,
        },
    }
