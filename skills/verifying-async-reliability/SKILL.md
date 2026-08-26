---
name: verifying-async-reliability
description: 'Build-verification specialist (Agent 5, Async/Reliability) that proves async-framework
  semantics: halt-on-failure chain, idempotency, DLQ, resumable retry, and NO whole-submission
  savepoint. TRIGGER when verifying a PRM_*Batch / PRM_AsyncOrchestrator / async trigger /
  cleanup batch (or when verifying-practitioner-build routes async-reliability). DO NOT TRIGGER
  when authoring the class.'
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

# verifying-async-reliability — Async / Reliability (Agent 5)

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/verifying-async-reliability` if it does not auto-load.


Prove the async-framework semantics of a batch / orchestrator / trigger delivery.

## Inputs

Delivered batch / `PRM_AsyncOrchestrator` / trigger; the async design in [`CLAUDE.md`](../../../CLAUDE.md) §4.3
+ [`PRM_Implementation_Plan.md`](../../../docs/implementation-plan/PRM_Implementation_Plan.md) §6; the CMA
spec (`epic-e-services/E19_PRM_CMAService.md`).

## Checks

- Chain **halts on first `Failed` step** (later steps do not run; completed records persist).
- **Idempotency:** External-Id upserts and/or status guards (a `Completed` step is never reprocessed);
  CMA uses the **pre-check** dedup (`PRM_CaseManager__c` + RecordType + primary lookup), no duplicate
  `PRM_CaseManagerAssociation__c`.
- Failures logged via `PRM_ExceptionLogger` → `PRM_FailedRecordStaging__c` (DLQ) with the
  `PRM_AsyncJobDetails__c` lookup.
- **No whole-submission savepoint/rollback** — legacy `rollbackOnError` is intentionally NOT reproduced
  (see [Audit](../../../docs/build-verification/03_Plan_Audit_Findings.md)).
- Batch calls back `findNextJob` in `finish()`; `Database.executeBatch` not started from a trigger body.
- Payload read from the ContentVersion file (`jsonFileParser`), not a Long Text field.

## Verdict

**NEEDS-FIX** on a missing status guard, a duplicate-prone CMA write, a savepoint that re-introduces
synchronous atomicity, or a chain that continues past a failure. **PASS** otherwise.

## Append to State

`async_findings[]` = `{check, expected, actual, status, citation}`; one `reasoning_chain` line.
