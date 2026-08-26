---
name: verifying-practitioner-build
description: 'Entry-point orchestrator (the DoD Verifier) for verifying AI-built Practitioner-Creation
  redesign components against legacy parity and the eligibility rules. TRIGGER when: a developer/architect
  delivers or opens a PR for a PRM_*Service / PRM_*Batch / PRM_AsyncOrchestrator / PRM_*Selector
  / PractitionerCreationPayloadValidator / prm* intake LWC / objects-customMetadata-permissionsets
  for the practitioner-creation rebuild, or asks to ''verify'', ''validate'', ''check parity
  for'', or ''run the DoD check on'' such an artifact. It classifies the artifact, routes
  to the specialist verifier skills, runs the deterministic backbone, invokes the Critic,
  and renders one Verification Report. DO NOT TRIGGER when: authoring the component itself
  (use generating-apex / building-omnistudio-*), or for non-practitioner-creation work.'
metadata:
  version: 1.0-ibx
  family: build-verification
  spec: docs/build-verification/01_Agent_Catalog.md
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
argument-hint: '[epic, service, or batch under review]'
---

# verifying-practitioner-build — DoD Verifier (router / orchestrator)

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/verifying-practitioner-build` if it does not auto-load.


The single entry point for the build-verification layer. You are a **router + aggregator**, not a
reviewer: you classify the delivered artifact, select the specialist verifier skills, run the
deterministic backbone, invoke the Critic, and render **one** Verification Report whose verdict is
computed deterministically from a shared Verification State.

> Full spec: [`docs/build-verification/`](../../../docs/build-verification/) — architecture
> (`00_Architecture.md`), agent catalog (`01_Agent_Catalog.md`), Parity Ledger (`02_Parity_Ledger.md`),
> **Validation/Eligibility Rule Ledger (`02b_Validation_Rule_Ledger.md`)**, adoption playbook
> (`04_Adoption_Playbook.md`), eval harness (`06_Agent_Eval_Harness.md`).

## Golden rules

1. **The verdict is deterministic — never decided by the LLM.** Any `BLOCKED` → `BLOCKED`; else any
   unresolved Critic contradiction or any `NEEDS-FIX` → `NEEDS-FIX`; else `PASS`.
2. **Every verdict must rest on cited evidence** — a Ledger row, a `docs/reference/` line, or a tool
   output. An uncited claim is a low-confidence flag, not a PASS.
3. **Ground the legacy side in the *active* OmniStudio version only** (active-version rule). Reconcile
   reference tables against live metadata with the `analyzing-omnistudio-dependencies` skill before
   trusting them.
4. **Append-only state.** Each verifier appends findings + `reasoning_chain` lines; never overwrite
   another agent's findings.

## Step 1 — Classify & route

| Delivered artifact | Run these verifier skills |
|--------------------|---------------------------|
| `PRM_*Service.cls` (Epic E) | parity, branch-coverage, governor-safety, service-boundary, test-adequacy, clarification-log |
| `PRM_*Batch.cls` | parity, branch-coverage, governor-safety, async-reliability, test-adequacy, clarification-log |
| `PRM_AsyncOrchestrator` / async trigger / `*CleanupBatch` | governor-safety, async-reliability, test-adequacy, clarification-log |
| `PRM_*Selector.cls` (Epic D) | parity (object-level), governor-safety, test-adequacy, clarification-log |
| `PractitionerCreationPayloadValidator` / IP wrapper (Epic F) | **contract-conformance**, branch-coverage, governor-safety, test-adequacy, clarification-log |
| `prm*` intake LWC (Epic C5) | contract-conformance, test-adequacy, clarification-log |
| `objects/` · `customMetadata/` · `permissionsets/` (Epic A) | parity (object-level), clarification-log |

`clarification-log` (CL Gate) and `test-adequacy` always run for code; **`verifying-cross-validation`
(the Critic) always runs last**; this orchestrator always renders the report.

Resolve the legacy step (E# · IBC/Delegated) from [Plan §8.1](../../../docs/implementation-plan/PRM_Implementation_Plan.md)
and the [Parity Ledger](../../../docs/build-verification/02_Parity_Ledger.md) before dispatching.

## Step 2 — Seed the Verification State

Create the run state (doc/JSON) the verifiers append to:

```
VerificationState:
  artifact            # file(s) under review
  resolved_step       # E# · batch · IBC/Delegated (Parity Ledger row)
  agents_selected     # the routed subset
  parity_findings / branch_findings / contract_findings / governor_findings /
  async_findings / boundary_findings / test_findings / cl_findings   # each: {item, expected, actual, status, citation}
  evidence[]          # {tool, command, output_ref, citation}
  contradictions[]    # {between, description, resolved}   (Critic)
  risk_score          # 0-100                              (Critic)
  reasoning_chain[]   # append-only, one line per step
  verdict             # PASS | NEEDS-FIX | BLOCKED
  review_tier         # auto | architect | owner-block
  signoff             # reviewer + date (human)
```

## Step 3 — Run the deterministic backbone first

Run these and attach outputs to `evidence[]` **before** the reasoning verifiers (they cite this output):

- `sf code-analyzer run` over changed files (via `running-code-analyzer`) — PMD/SFGE: no SOQL/DML in
  loops, FLS/CRUD, no hardcoded Ids.
- `sf apex run test -n <Class>Test --target-org qa-sandbox --code-coverage` (via `running-apex-tests`) —
  capture pass/fail + coverage.
- Static SObject/DML scan of the changed class (for parity + governor).
- `analyzing-omnistudio-dependencies` to reduce the legacy reference to **active** versions.

## Step 4 — Dispatch the routed verifier skills

Invoke each selected skill; each appends its `*_findings` + `reasoning_chain` to the State:
`verifying-parity`, `verifying-branch-coverage`, `verifying-contract-conformance`,
`verifying-governor-safety`, `verifying-async-reliability`, `verifying-service-boundary`,
`verifying-test-adequacy`, `verifying-clarification-log`.

## Step 5 — Invoke the Critic

Run `verifying-cross-validation` over the **whole** State. It appends `contradictions[]`, the
`risk_score`, and sets `review_tier`. It overturns nothing — an **unresolved** contradiction demotes the
aggregate to at least `NEEDS-FIX`.

## Step 6 — Aggregate & render the report (deterministic)

Compute the verdict by the rule in Golden Rule #1; set the review tier from the risk score
(`0–20 auto` · `21–60 architect` · `61–100 owner-block`). Render the report — a **render of the State**,
nothing re-summarized:

```markdown
# Verification Report — <artifact>
Resolved step: <E# · IBC/Delegated>   Verdict: <PASS|NEEDS-FIX|BLOCKED>
Risk score: <0-100>   Review tier: <auto|architect|owner-block>

## Findings (by agent)
| Agent | Item | Expected (citation) | Actual | Status |
|-------|------|---------------------|--------|--------|

## Critic — cross-agent contradictions
| Between | Description | Resolved? |

## Evidence
| Tool | Command | Output |

## Required actions (NEEDS-FIX / BLOCKED only)
- <file:line> — <what to change> — <legacy expectation + citation>
```

## Definition of Done it enforces (per [`CLAUDE.md`](../../../CLAUDE.md) §7.3)

- DR→object field map extracted + signed off (no `*__c` "inferred").
- `extends PRM_ServiceBase`; hosted in its batch per CL-15; batch branches IBC/Delegated and calls back
  `findNextJob`.
- One bulk DML per object type; reads via Epic D selectors; record types via cached describe.
- ≥ 85% coverage incl. bulk (200) + negative/halt-on-failure; real outcome assertions.
- Conforms to the §6 pre-commit checklist.
