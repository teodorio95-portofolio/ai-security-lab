"""Guardrails (active only when GUARDRAILS=on).

Three local, no-network layers built on llm-guard:
  1. input scan  — reject prompt-injection / extraction attempts (LLM01/LLM07)
  2. tool policy — allow-list, block dangerous tools (LLM06)
  3. output scan — redact the planted secret and PII (LLM02/LLM05)

The llm-guard scanners download a detection model on first use, so they are
loaded lazily and fail open with a logged reason if unavailable — the lab still
runs, it just tells you the scan was skipped.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache

from .config import PLANTED_SECRET
from .tools import DANGEROUS_TOOLS

_SECRET_RE = re.compile(re.escape(PLANTED_SECRET), re.IGNORECASE)


@dataclass
class ScanResult:
    allowed: bool
    text: str
    reasons: list[str] = field(default_factory=list)


@lru_cache(maxsize=1)
def _input_scanner():
    from llm_guard.input_scanners import PromptInjection
    from llm_guard.input_scanners.prompt_injection import MatchType

    return PromptInjection(threshold=0.5, match_type=MatchType.FULL)


@lru_cache(maxsize=1)
def _output_scanner():
    from llm_guard.output_scanners import Sensitive

    return Sensitive(redact=True)


def scan_input(text: str) -> ScanResult:
    """Block instruction-override / extraction prompts before they reach the model."""
    try:
        sanitized, is_valid, risk = _input_scanner().scan(text)
    except Exception as exc:  # model unavailable, etc. — fail open, but say so.
        return ScanResult(True, text, [f"input-scan-skipped: {exc}"])
    if not is_valid:
        return ScanResult(False, sanitized, [f"prompt_injection risk={risk:.2f}"])
    return ScanResult(True, sanitized, [])


def check_tool_call(name: str) -> ScanResult:
    """Allow-list tool calls; refuse dangerous tools regardless of the prompt."""
    if name in DANGEROUS_TOOLS:
        return ScanResult(False, "", [f"blocked dangerous tool: {name}"])
    return ScanResult(True, "", [])


def scan_output(prompt: str, text: str) -> ScanResult:
    """Redact the planted secret and PII from the reply."""
    reasons: list[str] = []
    sanitized = text
    # Backstop: always redact the known planted secret, even if the ML scanner
    # misses it. Defense in depth.
    if _SECRET_RE.search(sanitized):
        sanitized = _SECRET_RE.sub("[REDACTED-SECRET]", sanitized)
        reasons.append("redacted planted secret")
    try:
        sanitized, is_valid, risk = _output_scanner().scan(prompt, sanitized)
        if not is_valid:
            reasons.append(f"sensitive-output risk={risk:.2f}")
    except Exception as exc:
        reasons.append(f"output-scan-skipped: {exc}")
    return ScanResult(True, sanitized, reasons)
