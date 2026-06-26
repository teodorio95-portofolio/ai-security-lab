# Attacks

Two complementary, fully local tools:

- **promptfoo** (agent-level) — drives the *actual agent* (planted secret,
  tools, system prompt) through adversarial prompts. This is the before/after
  gate. Deterministic suite: [`../eval/promptfooconfig.yaml`](../eval/promptfooconfig.yaml);
  auto red-team: [`promptfoo/`](promptfoo/).
- **garak** (model-level) — probes the *underlying Ollama model* for known
  weakness categories. Complementary baseline. See [`garak/`](garak/).

```bash
make attack    # promptfoo suite, guardrails OFF (attacks land)
make redteam   # promptfoo auto red-team (Ollama generates the attacks)
make garak     # garak model probes
```

Step-by-step before/after writeups live in [`scenarios/`](scenarios/).
