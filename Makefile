# ai-security-lab — attack & defend the runtime of an LLM agent.
# Everything is free & local: model via Ollama, scanners via uv / npx.

MODEL ?= llama3.2:3b
OLLAMA_HOST ?= http://localhost:11434
VENV_PY := .venv/bin/python

# promptfoo (node) drives our Python provider; tell it which interpreter to use.
export PROMPTFOO_PYTHON := $(VENV_PY)
export AISEC_MODEL := $(MODEL)
export OLLAMA_HOST := $(OLLAMA_HOST)

# promptfoo runs through npx, so there is nothing to install globally.
PROMPTFOO := npx -y promptfoo@latest
EVAL_CONFIG := eval/promptfooconfig.yaml

.DEFAULT_GOAL := help
.PHONY: help up agent attack defend eval redteam garak demo down clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

up: ## Install deps (uv) and pull the local model
	uv sync --extra attack
	ollama pull $(MODEL)

agent: ## Ask the agent one question: make agent Q="hello" [GUARDRAILS=on]
	@GUARDRAILS=$${GUARDRAILS:-off} uv run ai-sec-agent --prompt "$(Q)"

attack: ## Run the adversarial suite with guardrails OFF (expect failures)
	GUARDRAILS=off $(PROMPTFOO) eval -c $(EVAL_CONFIG) --no-cache

defend: ## Run the same suite with guardrails ON (expect passes)
	GUARDRAILS=on $(PROMPTFOO) eval -c $(EVAL_CONFIG) --no-cache

eval: ## Before/after: run OFF then ON and print both pass rates
	@echo "== ATTACK (guardrails OFF) =="
	-@GUARDRAILS=off $(PROMPTFOO) eval -c $(EVAL_CONFIG) --no-cache -o output-attack.json >/dev/null 2>&1 || true
	@$(VENV_PY) scripts/passrate.py output-attack.json "guardrails OFF"
	@echo "== DEFEND (guardrails ON) =="
	-@GUARDRAILS=on $(PROMPTFOO) eval -c $(EVAL_CONFIG) --no-cache -o output-defend.json >/dev/null 2>&1 || true
	@$(VENV_PY) scripts/passrate.py output-defend.json "guardrails ON"

redteam: ## Auto red-team the agent (promptfoo generates attacks via Ollama)
	cd attacks/promptfoo && GUARDRAILS=off $(PROMPTFOO) redteam run

garak: ## Scan the underlying Ollama model with garak
	uv run garak --model_type ollama --model_name $(MODEL) \
		--probes promptinject,dan.Dan_11_0,leakreplay --report_prefix garak_runs/aisec

demo: up eval ## One-shot story: setup + before/after evaluation

down: ## Stop helpers (this lab has no long-running services)
	@echo "nothing to stop — ai-security-lab runs on demand"

clean: ## Remove local scan artifacts and caches
	rm -rf output-*.json garak_runs .promptfoo promptfoo-output
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
