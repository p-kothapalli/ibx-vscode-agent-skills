---
name: generating-permission-set
description: Generates correct, deployable Salesforce permission set metadata (PermissionSet
  XML) with object, field, user, and app permissions. Use this skill when creating or editing
  permission set metadata, object permissions, field-level security (FLS), tab visibility,
  or deploying permission sets.
compatibility: Salesforce Metadata API v60.0+
metadata:
  version: 1.0-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/generating-permission-set
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
user-invocable: true
---

# generating-permission-set

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/generating-permission-set` if it does not auto-load.


Generate/edit `PermissionSet` metadata (`.permissionset-meta.xml`).

## Core Properties

```xml
<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>Display Name</label>
    <description>Purpose and intended audience</description>
</PermissionSet>
```
(fullName comes from the filename.)

## Sections

- **objectPermissions** — `allowCreate/Read/Edit/Delete`, `modifyAllRecords`, `viewAllRecords`, `viewAllFields`, `object`.
- **fieldPermissions** — `editable`, `readable`, `field` (`Object.Field__c`). **Required fields must NEVER appear** — granting FLS on a required field fails deployment. Formula fields cannot be `editable`. Master-detail fields are required on the child.
- **userPermissions** — system perms (`ApiEnabled`, `RunReports`). Security-review: `ViewAllData`, `ModifyAllData`, `ManageUsers`.
- **applicationVisibilities** / **tabSettings** — tab names: custom object tabs include `__c`; standard tabs use `standard-Account` form.
- **classAccesses** / **pageAccesses** — Apex/VF access.
- **recordTypeVisibilities**, `license`, `hasActivationRequired` — optional.

## What Causes Deployment Failure

Field permissions on required fields; wrong/missing API name suffixes (`__c`); duplicate permissions. Follow least privilege.

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win.

### 1 — Permission Sets & PSGs Are THE Access Model (not profiles)

IBX provisions access almost entirely through **permission sets** and **permission set groups**, all `PRM_`-prefixed. Existing building blocks (reuse before creating):

- **Base/role PS:** `PRM_Base`, `PRM_CredentialingUser`, `PRM_CredentialingCompliance`, `PRM_AncillaryCredSpecialist`, `PRM_NetworkManagementQC`, `PRM_DevOpsPermissionSet`
- **Data scope:** `PRM_DataViewAll`, `PRM_DataModifyAll`, `PRM_DataHardDelete`
- **Feature/UI:** `PRM_EditFieldsonUI`, `PRM_APIEnabled`, `PRM_OmniStudioPermission`, `PRM_OSSavedForLater`
- **Integration:** `PRM_Mulesoft_Connector`, `PRM_Mulesoft_Integration`, `PRM_ManageDataIntegrations`
- **PSGs:** `PRM_BasePSG`, `PRM_BusinessAdminPSG`, `PRM_PortalUsersPSG`, `PRM_SupportPSG`, `PRM_SystemIntegrationPSG`

New permission sets use the **`PRM_`** prefix and a clear `description`. Prefer extending an existing PS or composing a **PSG** over creating broad new sets.

### 2 — Custom Permissions Drive Behavior

IBX gates logic with **custom permissions** (`customPermissions` section + `$Permission` checks in Apex/Flow/validation). Reuse the existing ones rather than minting duplicates:

`PRM_TriggerBypassPermission` (bypass Apex triggers), `PRM_TriggerFlowBypassPermission` (bypass Flows), `PRM_CredentialingPermission`, `PRM_AncillaryCredSpecialistPermission`, `PRM_NetworkManagementQCPermission`, `PRM_EditFieldonUIPermission`, `PRM_RunRoundRobin`, `PRM_UpdateNPIPermission`, `PRM_UpdatePrimaryTaxonomy`, `PRM_PDMPermission`, etc.

Grant a custom permission in a permission set via:
```xml
<customPermissions>
    <enabled>true</enabled>
    <name>PRM_TriggerBypassPermission</name>
</customPermissions>
```

### 3 — Trigger/Flow Bypass Pattern

Integration, data-load, and certain admin users get `PRM_TriggerBypassPermission` / `PRM_TriggerFlowBypassPermission` so bulk operations skip automation. When creating an integration/data PS, include the appropriate bypass custom permission (this is the established IBX pattern, used by `generating-apex`, `generating-apex-test`, and `generating-validation-rule`).

### 4 — FLS for New `PRM_*` Fields

When you add a field via `generating-custom-field`, expose it here through the right `PRM_*` PS (commonly `PRM_CredentialingUser` for read, `PRM_EditFieldsonUI` for edit). Never add **required** fields to `fieldPermissions`.

### 5 — OmniStudio Access

Users running OmniScripts/IPs/FlexCards need `PRM_OmniStudioPermission` (and `PRM_OSSavedForLater`/`OmniScript_Saved_session_permission` for saved sessions). Reference these rather than re-granting OmniStudio package perms ad hoc.

### 6 — Location & Deploy

Files: `force-app/main/default/permissionsets/<Name>.permissionset-meta.xml` (PSGs in `permissionsetgroups/`, custom perms in `customPermissions/`). Read a sibling `PRM_*` PS first to match style. Deploy:
```bash
sf project deploy start \
  --source-dir force-app/main/default/permissionsets/<Name>.permissionset-meta.xml \
  --target-org qa-sandbox --wait 10
```
Default alias `qa-sandbox`.
