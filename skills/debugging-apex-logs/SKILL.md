---
name: debugging-apex-logs
description: 'Salesforce debug log analysis and troubleshooting with 100-point scoring. TRIGGER
  when: user analyzes debug logs, hits governor limits, reads stack traces, or touches .log
  files from Salesforce orgs. DO NOT TRIGGER when: running Apex tests (use running-apex-tests),
  generating or fixing Apex code (use generating-apex), or Agentforce session tracing (use
  observing-agentforce).'
metadata:
  version: 1.1-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/debugging-apex-logs
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
argument-hint: '[user, request id, or reproduction]'
---

# debugging-apex-logs: Salesforce Debug Log Analysis & Troubleshooting

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/debugging-apex-logs` if it does not auto-load.


Use this skill for **root-cause analysis from debug logs**: governor-limit diagnosis, stack-trace interpretation, slow-query investigation, heap/CPU pressure analysis, or a reproduction-to-fix loop based on log evidence.

Delegate elsewhere when: running/repairing Apex tests (`running-apex-tests`), generating the code fix (`generating-apex`), Agentforce session traces (`observing-agentforce`).

## Required Context First

org alias · failing transaction/flow/test · timestamp window · user/record/request ID · diagnosis-only vs diagnosis+fix.

## Workflow

1. **Retrieve logs** (see CLI below).
2. **Analyze in order:** entry point/transaction type → exceptions/fatal errors → governor limits → repeated SOQL/DML → CPU/heap hotspots → callout timing/external failures.
3. **Classify severity:** Critical (runtime failure/hard limit), Warning (near-limit/non-selective), Info (optimization).
4. **Recommend the smallest correct fix** — root-cause, bulk-safe, testable, verifiable on rerun.

## High-Signal Issue Patterns

| Issue | Primary signal | Default fix direction |
|---|---|---|
| SOQL in loop | repeating `SOQL_EXECUTE_BEGIN` in a repeated path | query once, use maps |
| DML in loop | repeated `DML_BEGIN` | collect rows, bulk DML once |
| Non-selective query | high rows scanned | indexed filters, reduce scope |
| CPU pressure | CPU near sync limit | reduce complexity, cache, async |
| Heap pressure | heap near limit | SOQL for-loops, reduce in-memory data |
| Null/fatal error | `EXCEPTION_THROWN`/`FATAL_ERROR` | guard nulls, fix empty-query handling |

## Output Format

```text
Issue: <summary>
Location: <class / line / transaction>
Root cause: <explanation>
Severity: Critical | Warning | Info
Fix: <specific action>
Verify: <test or rerun step>
```

## Gotchas

| Pitfall | Resolution |
|---------|------------|
| Log truncated at 2 MB | Reduce levels (`ApexCode: INFO`) and re-capture |
| Same issue shows as SOQL + CPU | Fix SOQL-in-loop first; CPU is secondary |
| No logs after trace flag set | Verify `ExpirationDate` in future and correct user traced |
| Async changes limit values | CPU limit 60,000ms async vs 10,000ms sync |
| Stack trace points to framework line | Walk up past handlers to originating user code |

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win.

### 1 — CLI Against `qa-sandbox`

```bash
sf apex list log --target-org qa-sandbox
sf apex get log --log-id <id> --target-org qa-sandbox
sf apex tail log --target-org qa-sandbox            # live stream during repro
```
Default alias is **`qa-sandbox`**.

### 2 — Check `PRM_ExceptionLogger` First

IBX funnels handled exceptions through **`PRM_ExceptionLogger`**. Before (or alongside) reading raw logs, check the project's log object/records the logger writes to — it often already captures class, method, and message. Cross-reference the logged entry with the debug log timestamp to pinpoint the failure.

### 3 — OmniStudio Transactions Look Different

A huge share of IBX runtime is OmniStudio. When the entry point is an **Integration Procedure / DataRaptor / OmniScript**, the stack trace surfaces `omnistudio` managed-package frames, then drops into a `PRM_*` `Callable`/`VlocityOpenInterface2` class. Walk **up** past `omnistudio.*` frames to find the `PRM_*` `invokeMethod`/`methodName` that actually failed (see `building-omnistudio-callable-apex`). Errors are commonly returned in the output map (`outMap.put('error', ...)`) rather than thrown — check IP response payloads, not just `FATAL_ERROR`.

### 4 — Common IBX Hot Spots

- DataRaptor/IP-driven **SOQL/DML in loops** when an IP loops over a list and calls Apex per-iteration → bulkify the `PRM_*` method.
- **Non-selective queries** on high-volume `PRM_*__c` objects (e.g. `PRM_AdverseActionLog__c`, history-style objects) → add indexed filters; archive query patterns to `requirements/SOQL/`.
- **Callout latency** to `PRM_Precisely_API`, `PRM_CAQH_API`, `PRM_SDSApi`, `NPPES_API`, `PRM_SendGrid` → check callout timing; ensure callouts are async from triggers.

### 5 — Trace Flags & Levels

Set a trace flag on the running/integration user before reproducing. Use `ApexCode: FINEST` + `Database: FINEST` for SOQL/DML-in-loop hunts; drop to `INFO` if logs truncate at 2 MB.

### 6 — Hand-offs

Reproduce via tests → `running-apex-tests`. Implement the fix → `generating-apex` (keep `PRM_ExceptionLogger`, `WITH USER_MODE`). Seed repro data → `handling-sf-data`. Deploy the fix → `deploying-metadata`.
