---
name: verifying-cross-validation
description: Build-verification Critic (Agent 9) — a dedicated adversarial reviewer that runs
  AFTER the routed verifiers, reads the whole Verification State, finds contradictions BETWEEN
  agents, and computes a numeric risk score (0-100) + review tier. TRIGGER when the verifying-practitioner-build
  orchestrator has collected verifier findings and needs cross-validation. DO NOT TRIGGER
  as a first-pass reviewer or to author components.
metadata:
  version: 1.0-ibx
  family: build-verification
  spec: docs/build-verification/01_Agent_Catalog.md
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
---

# verifying-cross-validation — Critic / Cross-Validator (Agent 9)

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/verifying-cross-validation` if it does not auto-load.


Run **after** the routed verifiers. A single verifier only sees its own concern; you read the **whole**
[Verification State](../../../docs/build-verification/00_Architecture.md) and catch conflicts **between**
agents, then assign a numeric risk score. You run **no new tools** and make **no new parity claims** — you
reason only over what the verifiers already proved. (Pattern proven in the Senior Mortgage Underwriting
system: specialists → Critic → decision.)

## Inputs

The full Verification State: every agent's findings + evidence + `reasoning_chain`.

## Cross-agent contradiction checks

- **Parity PASS but Test-Adequacy has no assertion** for that object/field → parity unproven by tests.
- **Branch-Coverage says Delegated-only** but Parity cited an **IBC-only** object (or vice versa) → branch/parity conflict.
- **Contract Conformance PASS** for an output field **no** parity finding shows being written → contract claims a record never created.
- **Governor PASS** (one bulk DML) but a parity finding implies a **per-record** child insert → bulk vs. parity conflict.
- **Async PASS** but a finding references a synchronous response field → model conflict.
- **Any verdict resting on uncited evidence** (no Ledger row / tool output) → low-confidence flag.

## Risk score (0–100, deterministic weights — computed, not LLM-judged)

`BLOCKED` finding = 40 · unresolved contradiction = 25 · `NEEDS-FIX` = 15 · uncited claim = 10 · low
test-coverage delta = 10 (capped at 100). The score sets the **review tier**: `0–20 auto-accept` ·
`21–60 architect review` · `61–100 owner-block`. Thresholds are tunable and pinned by the eval harness
([`06_Agent_Eval_Harness.md`](../../../docs/build-verification/06_Agent_Eval_Harness.md)).

## Verdict / output

You do not overturn a verifier verdict — you **append** `contradictions[]` + `risk_score` + `review_tier`
to the State. An **unresolved** contradiction demotes the aggregate to at least `NEEDS-FIX` (the
orchestrator applies this in its deterministic aggregation).
