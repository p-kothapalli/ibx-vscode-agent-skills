---
name: generating-custom-object
description: Use this skill when users need to create, generate, or validate Salesforce Custom
  Object metadata. Trigger when users mention custom objects, creating objects, object metadata,
  .object files, sharing models, name fields, or validation rules on objects. Also use when
  troubleshooting object deployment errors, especially around sharing models and Master-Detail
  relationships.
metadata:
  version: 1.0-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/generating-custom-object
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
argument-hint: '[object purpose]'
---

# generating-custom-object

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/generating-custom-object` if it does not auto-load.


Generate `CustomObject` metadata XML (`.object-meta.xml`). The API name (fullName) is the **filename** (e.g. `Vehicle__c.object-meta.xml`), NOT a tag.

## Required Elements

`label` (singular), `pluralLabel`, `nameField` (with `label` + `type`), `deploymentStatus` = `Deployed`, `sharingModel`, `visibility` = `Public`.

### Sharing Model Rules
- No Master-Detail field → `sharingModel = ReadWrite`
- Has Master-Detail field → `sharingModel = ControlledByParent` (required; `ReadWrite` will error)

### Name Field
- **Text** for human-named entities; **AutoNumber** for transactions/logs (needs `displayFormat` e.g. `INV-{0000}` + `startingNumber`).

### Other
- `description` mandatory (professional summary). Junction objects named by combining parents (`Position_Candidate__c`). User-facing objects: enable search/activities/reports/history; system/junction objects: omit to keep XML lean.

## Critical Constraints

- Never use reserved words (`Select`, `User`, `Date`, `Type`, …) as API names.
- Max **2 Master-Detail** relationships per object (use Lookup beyond that).
- Do NOT include `<fullName>` at the XML root (derived from filename).
- Validation rule names: alphanumeric + underscore, start with letter, no trailing/double underscore, **no `__c` suffix** (unlike fields/objects).

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win.

### 1 — Naming: `PRM_<DomainNoun>__c`

New IBX objects use the **`PRM_` prefix** and end in `__c`, named for the provider-credentialing domain — consistent with existing objects such as `PRM_AdverseActionLog__c`, `PRM_CaseDataManager__c`, `PRM_AncillaryAssessment__c`, `PRM_ContractHierarchy__c`. Junction objects still combine the two parents but keep the `PRM_` prefix.

### 2 — Reuse Before Create (graph-first)

IBX already has a very large object footprint. Before creating an object, use **`code-review-graph` MCP** (`semantic_search_nodes`) / list `force-app/main/default/objects/` to confirm no existing `PRM_*__c` already models the concept. Extend the existing object instead of duplicating.

### 3 — Location & Structure in SFDX Source

Create `force-app/main/default/objects/<Object>__c/<Object>__c.object-meta.xml`, with child fields under `.../fields/` (see `generating-custom-field`), validation rules under `.../validationRules/` (see `generating-validation-rule`). Don't inline large field/validation sets into the object file — IBX keeps them in their own decomposed files for clean source diffs.

### 4 — Sharing Aligns with `PRM_*` Permission Sets

IBX grants object CRUD via **permission sets** (`PRM_CredentialingUser`, `PRM_DataViewAll`, `PRM_DataModifyAll`, etc.), not profiles. Default OWD to the most restrictive workable model; after creating the object, grant access through the right `PRM_*` permission set (see `generating-permission-set`).

### 5 — Triggers & Logging Conventions

If the object needs automation, its trigger/handler follows IBX conventions: `PRM_` prefix, trigger bypass via **`PRM_TriggerBypassPermission`**, and error logging via **`PRM_ExceptionLogger`** (see `generating-apex`). Flow-based automation bypasses via **`PRM_TriggerFlowBypassPermission`**.

### 6 — Deploy

```bash
sf project deploy start \
  --source-dir force-app/main/default/objects/<Object>__c \
  --target-org qa-sandbox --wait 10
```
Default alias `qa-sandbox`. For non-source-tracking orgs use the manifest (`manifest/package.xml`) per `deploying-metadata`.
