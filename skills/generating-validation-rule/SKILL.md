---
name: generating-validation-rule
description: Use this skill when users need to create, modify, or validate Salesforce Validation
  Rules. Trigger when users mention validation rules, field validation, data quality rules,
  formula validation, error messages, or validation logic. Also use when users encounter validation
  errors or need to enforce business rules at the data layer.
metadata:
  version: 1.0-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/generating-validation-rule
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
---

# generating-validation-rule

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/generating-validation-rule` if it does not auto-load.


Validation Rules enforce data quality: a formula is evaluated on save and **blocks the save when it returns TRUE**. File extension: `.validationRule-meta.xml`.

## Required Properties

- **fullName** — API name: start with a letter, alphanumeric + underscore, no trailing/double underscore, **no `__c` suffix**, ≤ 40 chars.
- **active** — `true`/`false`.
- **errorConditionFormula** — returns TRUE/FALSE; TRUE triggers the error.
- **errorMessage** — ≤ 255 chars.

## Function Guidelines

`TEXT()` not on Text fields · `CASE()` last param = default, even param count · `VALUE()` only on Text fields · `DAY()`/`MONTH()` only on Date (convert Datetime via `DATEVALUE`) · `DATEVALUE()` only on DateTime · `ISPICKVAL()` for picklist equality · `ISCHANGED()` to detect changes.

## Critical Rules

1. **CDATA**: any `errorConditionFormula` containing XML/`<`/`>`/`&` MUST be wrapped in `<![CDATA[ ... ]]>`.
2. **"Update to X" vs "Update to also X"**: the first replaces the formula; the second appends (wrap existing in `AND()`/`OR()`).
3. Always use the `.validationRule-meta.xml` extension.

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win.

### 1 — Location in SFDX Source

Validation rules live under `force-app/main/default/objects/<Object>/validationRules/<RuleName>.validationRule-meta.xml` — a separate decomposed file, not inline in the object. Read a sibling rule on the same object first to match style.

### 2 — Naming

Use a descriptive, domain-aligned API name (no `__c`). Match the convention of existing rules on the target object. For provider-credentialing guardrails, name for the rule's intent (e.g. `Require_NPI_When_Practitioner`, `Block_Inactive_Taxonomy`).

### 3 — Bypass Must Respect IBX Trigger/Flow Bypass Model

IBX uses custom permissions to bypass automation. If a validation rule must be skippable for integration/admin/data-load users, gate it with `$Permission` on the relevant **custom permission** (the project already uses `PRM_TriggerBypassPermission` for Apex triggers and `PRM_TriggerFlowBypassPermission` for Flows). Example pattern:

```
AND(
  /* business condition */,
  NOT($Permission.PRM_TriggerBypassPermission)
)
```
Reuse an existing `PRM_*` custom permission where one fits rather than inventing a new bypass flag; create a new one only when justified.

### 4 — Don't Duplicate Apex/Flow Logic

Much IBX business logic runs in Apex (`PRM_*` services) and Integration Procedures. Add a validation rule for **declarative data-integrity guardrails**, not to re-implement complex cross-object logic already handled in Apex/IP. For complex logic, prefer the existing Apex layer (`generating-apex`).

### 5 — Bulk-Load Safety

Because IBX runs large data scripts/imports (`handling-sf-data`) and integrations, ensure new active rules won't break legitimate bulk upserts from `PRM_Precisely_API`/`PRM_CAQH_API`/`NPPES_API`/Mulesoft flows. Verify against existing data and consider the bypass permission for integration users.

### 6 — Deploy

```bash
sf project deploy start \
  --source-dir force-app/main/default/objects/<Object>/validationRules/<RuleName>.validationRule-meta.xml \
  --target-org qa-sandbox --wait 10
```
Default alias `qa-sandbox`. Test the rule with `running-apex-tests`/`handling-sf-data` data before activating in higher orgs.
