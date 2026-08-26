---
name: verifying-parity
description: Build-verification specialist (Agent 1, Parity Auditor) that proves a delivered
  PRM_*Service / PRM_*Batch creates/updates the SAME objects, fields, and record types the
  legacy DataRaptor chain created for the equivalent step. TRIGGER when verifying an Epic-E
  service/batch (or when verifying-practitioner-build routes parity). DO NOT TRIGGER when
  authoring the class (use generating-apex) or for payload contracts (use verifying-contract-conformance).
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

# verifying-parity — Parity Auditor (Agent 1)

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/verifying-parity` if it does not auto-load.


Prove the delivered service/batch produces the **same object set, record types, and field map** the legacy
DataRaptor chain produced for its resolved step — no missing objects, no extra objects.

## Inputs

- The delivered `PRM_*Service` / `PRM_*Batch`; its resolved legacy step (Plan §8.1).
- [Parity Ledger](../../../docs/build-verification/02_Parity_Ledger.md) row(s) for the step.
- Legacy DR→object tables in [`PRM_PractitionerCreationContainer_Process.md`](../../../docs/reference/PRM_PractitionerCreationContainer_Process.md) §5
  and step tables in [`PRM_PractitionerCreation_Apex_Service_Flow.md`](../../../docs/reference/PRM_PractitionerCreation_Apex_Service_Flow.md).

## Deterministic checks

- Static-scan the SObject types the class touches (DML + `newSObject`/typed builders) — fact, not opinion.
- Record types must be resolved by **cached describe**, never SOQL on `RecordType`.
- Reconcile the legacy reference against **active** OmniStudio metadata via `analyzing-omnistudio-dependencies`
  before trusting any reference table.

## LLM reasoning

Map delivered object set ↔ Ledger expected set; classify each `matched / missing / extra / renamed-by-CL`;
explain each delta with a citation.

## Watch the traps (from the Parity Ledger)

- **PPL = `HealthcarePractitionerFacility`** (CL-2).
- **`HealthcarePractitionerFacilityNetwork` must NOT be created** (CL-3) — async creates
  `HealthcareFacilityNetwork` only.
- **CDM is one coalesced write** — assert final field state, never a write count.

## Verdict

- **PASS** — every expected object produced, no unexplained extras, RTs correct; if the field map is signed
  off, every required field mapped.
- **NEEDS-FIX** — a missing/extra object, wrong record type, or field mapped to the wrong target.
- **BLOCKED** — the DR→object **field map is still "inferred"** (CL-11): certify object-level, block
  field-level until the per-service map is signed off.

## Append to State

`parity_findings[]` = `{object, expected, actual, status, ledger_citation}`; evidence for the static scan;
one `reasoning_chain` line.
