"""The vulnerable support agent: an Ollama chat loop with tool-calling.

With GUARDRAILS=off it is the unprotected baseline. With GUARDRAILS=on the
same loop runs input scanning, a tool-call allow-list, and output redaction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import ollama

from . import guardrails
from .config import SYSTEM_PROMPT, Settings, load_settings
from .tools import TOOL_SPECS, call_tool


@dataclass
class AgentResult:
    reply: str
    tool_calls: list[str] = field(default_factory=list)
    guardrail_events: list[str] = field(default_factory=list)
    blocked: bool = False


def respond(user_input: str, settings: Settings | None = None) -> AgentResult:
    """Run one turn of the agent and return its reply plus a security trace."""
    settings = settings or load_settings()
    events: list[str] = []
    tool_log: list[str] = []

    if settings.guardrails:
        scan = guardrails.scan_input(user_input)
        events += scan.reasons
        if not scan.allowed:
            return AgentResult(
                reply="Request blocked: potential prompt injection detected.",
                guardrail_events=events,
                blocked=True,
            )
        user_input = scan.text

    client = ollama.Client(host=settings.ollama_host)
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    for _ in range(settings.max_tool_iterations):
        resp = client.chat(
            model=settings.model,
            messages=messages,
            tools=TOOL_SPECS,
            options={"temperature": settings.temperature},
        )
        msg = resp["message"]
        messages.append(msg)
        calls = msg.get("tool_calls") or []
        if not calls:
            break
        for call in calls:
            name = call["function"]["name"]
            args = dict(call["function"].get("arguments") or {})
            if settings.guardrails:
                policy = guardrails.check_tool_call(name)
                if not policy.allowed:
                    events += policy.reasons
                    tool_log.append(f"{name}(BLOCKED)")
                    messages.append(
                        {"role": "tool", "content": f"error: tool {name} not permitted by policy"}
                    )
                    continue
            tool_log.append(f"{name}({args})")
            output = call_tool(name, args)
            messages.append({"role": "tool", "content": output})

    last = messages[-1] if messages else {}
    reply = (last.get("content") if hasattr(last, "get") else "") or ""

    if settings.guardrails:
        out = guardrails.scan_output(user_input, reply)
        events += out.reasons
        reply = out.text

    return AgentResult(reply=reply, tool_calls=tool_log, guardrail_events=events)
