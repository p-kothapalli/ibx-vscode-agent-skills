---
name: generating-flow
description: Generate Salesforce Flows using the MCP tool execute_metadata_action. Use when
  the user asks to create, build, or generate a flow — including Screen, Autolaunched, Record-Triggered
  (before/after-save), Scheduled. Also trigger for flow-like requests such as 'when a record
  is created', 'trigger daily at', 'send an email when', 'update the field when', 'automate',
  'workflow', or 'flow XML/metadata'.
metadata:
  version: 1.0-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/generating-flow
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
---

# generating-flow

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/generating-flow` if it does not auto-load.


Generate Salesforce Flow metadata by running the required **3-step MCP pipeline** and return the flow XML.

## Mandatory Pipeline (`execute_metadata_action`)

There is **no alternative** — do not hand-author flow XML. Call all three steps in order, via the `action` parameter:

1. **`fetchGroundedObjectMetadata`** — inputs: `userPrompt` (string), `inflightMetadata` (ARRAY, `[]` if none). Output `groundingMetadata` (string).
2. **`flowElementSelection`** — inputs: same `userPrompt`, `groundingMetadata` (pass the string from step 1 directly, do not re-serialize), `operationId` = `""`. Output `operationId`.
3. **`flowElementGeneration`** — inputs: `operationId` (from step 2), `requestSource` = `"A4V"` (XML). **Call repeatedly in a loop with the same `operationId` until `isComplete` is `true`** or errors return. Don't pause/ask between iterations. Extract XML from `result` only when `isComplete`.

**Strict constraints on returned XML:** do not modify, add, or remove nodes/attributes/text. Exception: if the user explicitly asks to fix validation/deployment errors in already-generated XML, targeted manual edits are allowed.

## inflightMetadata

ARRAY (never the string `"[]"`). Property names exactly: `apiName`, `type`, `label`, `referenceTo` (lookup), `values` (picklist). Scan the local SFDX project for custom objects/fields relevant to the flow and include only those; otherwise `[]`.

## Multiple Flows

If the user asks for N flows, run **N separate sequential pipelines**, each with its own single-flow `userPrompt` and its own `inflightMetadata`. Never club multiple flows into one `userPrompt`; never parallelize.

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win.

### 1 — Flows Are a Minor Surface; Prefer Existing Patterns

IBX has only ~22 flows vs thousands of OmniStudio assets and 1,200+ Apex classes. Most automation already lives in **Apex (`PRM_*` services/triggers)** and **Integration Procedures**. Before generating a flow, check whether the requirement is better served by an existing IP/Apex path (graph-first via `code-review-graph`). Use a Flow for genuinely declarative, admin-maintainable automation.

### 2 — `inflightMetadata` Comes from `PRM_*` Schema

When scanning the local project for the flow's objects/fields, use the IBX **`PRM_*__c`** objects (e.g. `PRM_CaseDataManager__c`, `PRM_AdverseActionLog__c`) and their `__c` fields. Pull these from `force-app/main/default/objects/` and pass them as structured array entries — don't pass descriptions.

### 3 — Respect the Flow Bypass Permission

IBX bypasses Flow automation for integration/data-load/admin users via the **`PRM_TriggerFlowBypassPermission`** custom permission. Record-Triggered/Autolaunched flows that perform DML should honor this — describe the bypass in the `userPrompt` (e.g. "skip when the running user has the PRM_TriggerFlowBypassPermission custom permission") so the generated decision/entry logic accounts for it. (Apex triggers use the separate `PRM_TriggerBypassPermission`.)

### 4 — Naming

Use clear, domain-aligned flow API names consistent with existing IBX flows (PascalCase/underscored, credentialing-domain vocabulary). Avoid `__c`-style names.

### 5 — Deploy & Activate

The pipeline returns XML; save it under `force-app/main/default/flows/<Name>.flow-meta.xml` and deploy via the Metadata API (default alias `qa-sandbox`):
```bash
sf project deploy start \
  --source-dir force-app/main/default/flows/<Name>.flow-meta.xml \
  --target-org qa-sandbox --wait 10
```
Only one flow version is active at a time (active-version concept, like OmniStudio). For callouts inside a flow see `building-sf-integrations`; for seed/test data see `handling-sf-data`.
