---
name: verifying-governor-safety
description: Build-verification specialist (Agent 4, Governor & Bulk-Safety) that proves a
  delivery is bulk-first and within per-batch governor budgets using sf code-analyzer and
  a perf harness. TRIGGER when verifying any Practitioner-Creation Apex delivery (or when
  verifying-practitioner-build routes governor-safety). DO NOT TRIGGER when authoring the
  class (use generating-apex).
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

# verifying-governor-safety — Governor & Bulk-Safety (Agent 4)

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/verifying-governor-safety` if it does not auto-load.


Mostly deterministic. Prove the delivery is bulk-first and within the per-batch governor budgets.

## Inputs

Delivered class; org standards ([`CLAUDE.md`](../../../CLAUDE.md) §6); legacy DML/SOQL baselines in
[`PRM_PractitionerCreation_Apex_Service_Flow.md`](../../../docs/reference/PRM_PractitionerCreation_Apex_Service_Flow.md) §"Sync DML count audit".

## Deterministic checks

- `sf code-analyzer run` (PMD/SFGE) over changed files via `running-code-analyzer` — no SOQL/DML in loops,
  FLS/CRUD enforced, no hardcoded Ids.
- Static scan: at most **one bulk DML per object type**; parents inserted before children.
- Perf harness (G3): `Test.startTest()/stopTest()` capture asserting per-submission budgets —
  **IBC DML ≤ 12 · Delegated DML ≤ 28 · SOQL ≤ 40 · CPU < 5000 ms · heap < 2 MB** (per-batch ceilings, CL-10).
- `WITH USER_MODE` / `Security.stripInaccessible`; record types via cached describe.

## LLM reasoning

Explain each analyzer finding in the context of this service's job; flag loops that *look* bulk-safe but
accumulate per-record DML across helper calls.

## Verdict

**NEEDS-FIX** on any SOQL/DML-in-loop, multiple DML per object type, missing FLS, or a budget breach in
the perf harness. **PASS** otherwise.

## Append to State

`governor_findings[]` = `{check, expected, actual, status}`; attach analyzer + harness output to
`evidence[]`; one `reasoning_chain` line.
