---
name: verifying-test-adequacy
description: Build-verification specialist (Agent 7, Test-Adequacy) that proves a delivery's
  tests exercise parity behavior (bulk/single/empty/negative) with real outcome assertions
  and >=85% coverage, not just compile-coverage. TRIGGER when verifying any Practitioner-Creation
  Apex delivery (or when verifying-practitioner-build routes test-adequacy). DO NOT TRIGGER
  when authoring tests (use generating-apex-test).
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

# verifying-test-adequacy — Test-Adequacy (Agent 7)

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/verifying-test-adequacy` if it does not auto-load.


Prove the delivery's tests actually exercise the parity behavior, not just compile-coverage.

## Inputs

The `PRM_*Test` class; org test standards ([`CLAUDE.md`](../../../CLAUDE.md) §6 Tests); the
`running-apex-tests` skill.

## Deterministic checks

- `sf apex run test -n <Class>Test --target-org qa-sandbox --code-coverage` → **≥ 85%** (deploy gate is 75%).
- Coverage spans **bulk (200) · single · empty · negative/halt-on-failure** paths.

## LLM reasoning

- Assertions check **outcomes** (records created with the right fields/RTs per the Parity Ledger), not just
  "no exception."
- No `@isTest(SeeAllData=true)`; uses `PRM_TestDataFactory`.
- Async wrapped in `Test.startTest()/stopTest()`; asserts the async completed and the DLQ behaves on a
  forced failure.
- For an Epic-F validator: there is a **negative test per eligibility rule** in
  [`02b_Validation_Rule_Ledger.md`](../../../docs/build-verification/02b_Validation_Rule_Ledger.md)
  (coordinate with `verifying-contract-conformance`).

## Verdict

**NEEDS-FIX** on < 85%, a missing bulk/negative path, `SeeAllData`, or assertion-free "happy path only"
tests. **PASS** otherwise.

## Append to State

`test_findings[]` = `{path, expected, actual, status}`; attach the test run + coverage to `evidence[]`;
one `reasoning_chain` line.
