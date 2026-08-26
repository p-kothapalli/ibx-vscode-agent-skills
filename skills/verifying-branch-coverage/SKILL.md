---
name: verifying-branch-coverage
description: Build-verification specialist (Agent 2, Branch-Coverage) that proves a delivery
  branches IBC Professional Staff vs Delegated Credentialing exactly as legacy and honors
  the Delegated sub-gates. TRIGGER when verifying an Epic-E service/batch or Epic-F validator
  (or when verifying-practitioner-build routes branch-coverage). DO NOT TRIGGER when authoring
  the class.
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

# verifying-branch-coverage — Branch-Coverage (Agent 2)

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/verifying-branch-coverage` if it does not auto-load.


Prove the delivery branches **IBC Professional Staff vs Delegated Credentialing** exactly as legacy, and
honors the Delegated sub-gates.

## Inputs

Delivered class; the branch decision trees in
[`PRM_PractitionerCreation_Apex_Service_Flow.md`](../../../docs/reference/PRM_PractitionerCreation_Apex_Service_Flow.md) §"Branch decision tree"
and [`PRM_PractitionerCreationContainer_Process.md`](../../../docs/reference/PRM_PractitionerCreationContainer_Process.md) §6;
branch rules R-B1–R-B6 in [`02b_Validation_Rule_Ledger.md`](../../../docs/build-verification/02b_Validation_Rule_Ledger.md) §1.

## Checks

- Branch key is `PractitionerCreationType`; the two values match legacy exactly.
- Delegated-only services (E3 Group, E6 Education, E7 BoardCert, E9 File, E10 Contact, E11 Language,
  E13–E15, E17–E18) do **not** run on the IBC branch.
- Sub-gates honored: `CaseManagerId` present → location/facility/network block (legacy steps 11–15);
  `FileData` present → file pipeline; `languages` non-empty → PersonLanguage; existing-primary path.
- IBC default info code `C64 (IBC Professional Staff)`; Delegated info codes come from selection (R-B5).
- `isExistingNPI` delta behavior (only deltas processed) matches legacy.

## Verdict

- **NEEDS-FIX** if a Delegated-only object is created on IBC, a gate is missing/inverted, or an
  existing-NPI path creates records it should skip.
- **PASS** otherwise.

## Append to State

`branch_findings[]` = `{gate, expected, actual, status, citation}`; one `reasoning_chain` line.
