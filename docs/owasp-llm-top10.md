# OWASP LLM Top 10 — coverage map

This lab targets the agent-runtime risks. Each row links a risk to the attack
that demonstrates it and the guardrail that stops it. The 2025 OWASP Top 10 for
LLM Applications is the reference list.

| ID | Risk | Attack (guardrails OFF) | Defense (guardrails ON) | Scenario |
|----|------|-------------------------|-------------------------|----------|
| LLM01 | Prompt Injection | Direct override + indirect injection via poisoned tool output | llm-guard `PromptInjection` input scanner | 01, 02 |
| LLM02 | Sensitive Information Disclosure | Agent leaks the planted operations key | Output `Sensitive` scanner + secret-redaction backstop | 01, 04 |
| LLM05 | Improper Output Handling | Tool output treated as trusted instructions | Tool output never elevated; reply re-scanned | 02 |
| LLM06 | Excessive Agency | Agent runs `run_shell` on attacker request | Tool allow-list blocks dangerous tools | 03 |
| LLM07 | System Prompt Leakage | Agent prints its system prompt | Input scanner blocks extraction; output redaction | 04 |

Scenario numbers refer to the writeups in [`../attacks/scenarios/`](../attacks/scenarios/).

## Not covered here (and why)

- **LLM03 Supply Chain / LLM04 Data & Model Poisoning** — handled by
  [#3 supply-chain-security](https://github.com/teodorio95-portofolio/supply-chain-security)
  (modelscan / picklescan + cosign). #7 deliberately assumes a clean model and
  attacks the runtime around it.
- **LLM08 Vector & Embedding Weaknesses** — no RAG store in this lab.
- **LLM10 Unbounded Consumption** — out of scope for a single-laptop demo.
