---
name: verifying-clarification-log
description: Build-verification specialist (Agent 8, Clarification-Log Gate) that stops deliveries
  which silently resolve or contradict an OPEN Clarification-Log item or diverge from the
  golden source-of-truth hierarchy. TRIGGER when verifying any Practitioner-Creation delivery
  (or when verifying-practitioner-build routes the CL gate). DO NOT TRIGGER when authoring
  the component.
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

# verifying-clarification-log — Clarification-Log Gate (Agent 8)

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/verifying-clarification-log` if it does not auto-load.


Stop deliveries that silently resolve or contradict an **open** Clarification-Log item, or diverge from the
golden source-of-truth hierarchy.

## Inputs

Delivered artifact; the Clarification Log ([`CLAUDE.md`](../../../CLAUDE.md) §3.4, TDD §12).

## Checks

- No `*__c` left **"inferred"** in the delivered service before its tests (CL-11 gate).
- `GroupRelatedBatch` deliveries are `BLOCKED` until the batch↔service mapping is assigned (CL-15).
- Async target scope honored — `HealthcareFacilityNetwork` only; **not** `NetworkMember`/`NetworkMemberChunk`
  (CL-6 partial: roster-sync, out of pilot scope).
- Real log object names `PRM_ExceptionLog__c` / `PRM_ExceptionLogEvent__e` (CL-5), not legacy
  `PRM_Exception_Log__c`.
- Reuses existing selectors/validator (CL-8/CL-9) rather than rebuilding — including the existing
  `PRM_PractitionerCreationValidator` effective-date rules (do not re-implement R-D*).

## Verdict

**BLOCKED** on any open-CL contradiction; **NEEDS-FIX** on a stale name / rebuilt-instead-of-reused
component. **PASS** otherwise. Always name the CL item id + owner.

## Append to State

`cl_findings[]` = `{cl_id, expected, actual, status, owner}`; one `reasoning_chain` line.
