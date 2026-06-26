"""Summarise a promptfoo JSON output file as a pass rate.

Usage: passrate.py <output.json> [label]
Kept dependency-free so it runs under the project venv without extra installs.
"""

from __future__ import annotations

import json
import sys


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else "output.json"
    label = sys.argv[2] if len(sys.argv) > 2 else path
    try:
        with open(path) as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"  {label}: no results ({exc})")
        return 0

    results = data.get("results", data)
    stats = results.get("stats", {}) if isinstance(results, dict) else {}
    passed = stats.get("successes")
    failed = stats.get("failures")
    if passed is None:
        rows = results.get("results", []) if isinstance(results, dict) else []
        passed = sum(1 for r in rows if r.get("success"))
        failed = sum(1 for r in rows if not r.get("success"))
    total = (passed or 0) + (failed or 0)
    pct = (100 * passed / total) if total else 0
    print(f"  {label}: {passed}/{total} checks passed ({pct:.0f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
