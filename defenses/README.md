# Defenses — guardrails that stop the attacks

Defenses are toggled with `GUARDRAILS=on`. There are three layers, all local
(`llm-guard`, no external service):

1. **Input scanning** — `llm_guard.input_scanners.PromptInjection` rejects
   instruction-override / extraction prompts before they reach the model
   (LLM01, LLM07).
2. **Tool-call policy** — an allow-list (`guardrails.check_tool_call`) blocks
   dangerous tools (`run_shell`, `delete_file`). Least privilege beats hoping
   the model behaves (LLM06).
3. **Output scanning** — `llm_guard.output_scanners.Sensitive` plus a regex
   backstop redact the planted secret and PII before the reply is returned
   (LLM02, LLM05).

The scanners load a detection model on first use and **fail open** (with a
logged reason) if it cannot be downloaded — the lab keeps working and tells you
the scan was skipped.

## Run the before/after

```bash
make attack    # GUARDRAILS=off — attacks land
make defend    # GUARDRAILS=on  — attacks blocked
make eval      # prints both pass rates
```

## Extending

- Tighten the `PromptInjection` threshold in `guardrails.py`.
- Add more `llm-guard` scanners (`BanTopics`, `Toxicity`, `Code`).
- Replace the static allow-list with human-in-the-loop approval for tool calls.
- Layer a second detector (e.g. self-hosted rebuff) for defense in depth.
