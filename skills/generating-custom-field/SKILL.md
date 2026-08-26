---
name: generating-custom-field
description: Use this skill when users need to create, generate, or validate Salesforce Custom
  Field metadata. Trigger when users mention custom fields, field types, Roll-up Summary fields,
  Master-Detail relationships, Lookup relationships, formula fields, picklists, or field metadata.
  Also use for field deployment errors, especially around Roll-up Summary format, Master-Detail
  constraints, or formula issues.
metadata:
  version: 1.0-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/generating-custom-field
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
argument-hint: '[object] [field type and purpose]'
---

# Salesforce Custom Field Generator and Validator

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/generating-custom-field` if it does not auto-load.


Generate/validate `CustomField` metadata XML with mandatory constraints to prevent deployment errors. Highest-failure-rate types: **Roll-up Summary** and **Master-Detail**.

## Universal Mandatory Attributes

Every field: `fullName` (Label → capitalize words, `_` for spaces, append `__c`), `label` (Title Case), `description` (business "why"), `inlineHelpText` (actionable end-user guidance). Set `externalId=true` for integration/unique-key fields (Text/Number/Email).

## Field Types (key)

`AutoNumber` (needs `displayFormat` w/ `{0}`, `startingNumber`) · `Checkbox` (default `false`) · `Lookup` (`referenceTo`, `relationshipName`, `deleteConstraint`) · `MasterDetail` (`referenceTo`, `relationshipName`, `relationshipOrder`) · `Number` (`precision`,`scale`) · `Currency` (18,2) · `Picklist` (`valueSet` w/ `restricted`) · `Text` (`length` ≤255) · `TextArea` (`length` 255) · `LongTextArea`/`Html` (`length`,`visibleLines`) · `Summary` (roll-up). Numeric rule: `precision ≤ 18` and `scale ≤ precision`.

## ⭐ Master-Detail — Forbidden attributes

NEVER include `required` (always required), `deleteConstraint` (always cascades), or `lookupFilter` (Lookup-only). DO include `relationshipOrder` (`0`/`1`). Parent object's child sharing must be `ControlledByParent`. Max 2 M-D per object.

## ⭐ Roll-Up Summary — Forbidden: `precision`, `scale`, `required`, `length`

Required: `type=Summary`, `summaryOperation` (`count`/`sum`/`min`/`max`), `summaryForeignKey` = `Child__c.MasterDetailField__c`. For sum/min/max also `summarizedField` = `Child__c.Field__c` (NOT for count). Only on the parent object.

## Formula

`Formula` is **not** a type — set `type` to the result type. Wrap `formula` body in `<![CDATA[ ... ]]>`. Never use `returnType`. Set `formulaTreatBlanksAs` = `BlankAsZero` (numeric) / `BlankAsBlank` (text/date). Function rules: `ISPICKVAL()` for picklist equality; `DAY()`/`MONTH()` only on Date; `CASE()` param count even (last = default).

## Common Errors

XML comments before root → `ConversionError` (remove them). Referenced field not deployed → deploy it first. `DUPLICATE_DEVELOPER_NAME` → unique name. Reserved words (`Order`, `Group`, …) → rename.

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win.

### 1 — Naming: `PRM_` Domain Prefix

IBX custom fields on credentialing objects are business-named with the **`PRM`/PRM-domain** vocabulary and end in `__c` (e.g. on `PRM_AdverseActionLog__c`, `PRM_CaseDataManager__c`). The platform requires the `__c` suffix; keep the human-readable label aligned with the provider-credentialing domain (NPI, Tax ID, Taxonomy, CAQH, PSV, credentialing dates, etc.). Match the casing/style of existing fields on the same object — read a sibling `*.field-meta.xml` first.

### 2 — Location in SFDX Source

Fields live under `force-app/main/default/objects/<Object>/fields/<Field>__c.field-meta.xml`. Create the file there; deploy via the Metadata API (see Override 6). Use **graph-first** (`code-review-graph` MCP) / a sibling field read to confirm the object's existing field conventions before adding.

### 3 — Confirm the Field Doesn't Already Exist

IBX has 1,100+ object files; duplicate/near-duplicate fields are a real risk. Search existing fields (`semantic_search_nodes` or list the object's `fields/` dir) before creating — reuse if an equivalent exists.

### 4 — Integration Fields → External ID

Fields that key off external systems IBX integrates with (Precisely, CAQH, NPPES/NPI, SDS, Mulesoft) should set `externalId=true` and a clear `inlineHelpText` naming the source system. This supports upserts from `handling-sf-data` and the integration skills.

### 5 — FLS Is Granted via `PRM_*` Permission Sets

IBX uses **permission sets, not profiles**, for access. After creating a field, expose it through the appropriate `PRM_*` permission set (e.g. `PRM_CredentialingUser`, `PRM_EditFieldsonUI`) — see `generating-permission-set`. Remember: **required** fields must NOT appear in `fieldPermissions`.

### 6 — Deploy

```bash
sf project deploy start \
  --source-dir force-app/main/default/objects/<Object>/fields/<Field>__c.field-meta.xml \
  --target-org qa-sandbox --wait 10
```
Deploy referenced fields before formula/roll-up fields that depend on them. Default alias `qa-sandbox`; prefer repo wrapper scripts where applicable.

### 7 — Validation Rules Are Separate

New data-quality rules on the field go in `validationRules/` via `generating-validation-rule`, not inline here.
