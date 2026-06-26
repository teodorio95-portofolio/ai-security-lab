# garak — model-level scanning

[garak](https://github.com/NVIDIA/garak) probes the base model served by
Ollama. It does not know about our agent's secret or tools — it establishes a
baseline of how the *model itself* responds to known attack families, which
complements the agent-level promptfoo suite.

```bash
# requires `make up` (installs the `attack` extra) and a running `ollama serve`
make garak
# equivalent to:
uv run garak --model_type ollama --model_name llama3.2:3b \
  --probes promptinject,dan.Dan_11_0,leakreplay \
  --report_prefix garak_runs/aisec
```

Reports (HTML + JSONL) are written under `garak_runs/` and are git-ignored —
findings are generated locally and never committed.
