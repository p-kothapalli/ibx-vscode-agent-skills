# LSC Component & Naming Reference

OmniStudio and platform component types used in LSC stories, plus the naming
conventions to apply to any **new** component. Verify **existing** components via
`code-review-graph`; verify **standard LSC** features via `salesforce-docs`.

## Contents

- Component types
- OmniScript element types (common in LSC flows)
- Action Launcher (LSC guided actions)
- Naming conventions (LSC)

---

## Component types

| Component | What It Is | When to Use | Runtime |
|-----------|-----------|-------------|---------|
| **OmniScript** | Multi-step guided UI flow | Field data collection, guided visit/sample flows | Client-side (LWC) |
| **FlexCard** | Data display component | Record display, dashboards, inventory tiles, embedded in OmniScript | Client-side (LWC) |
| **DataRaptor Extract** | Read data from Salesforce | Fetch records for display | Server-side |
| **DataRaptor Transform** | Reshape JSON data | Transform without DML | Server-side |
| **DataRaptor Load** | Write data to Salesforce | Create/Update/Upsert records | Server-side |
| **Integration Procedure (IP)** | Server-side orchestration | Chain DRs, Apex, callouts, matrices | Server-side |
| **DataMapper** | Declarative field mapping | Map fields between schemas | Server-side |
| **Decision Matrix** | Lookup/rule table | Eligibility, routing, tiering | Server-side |
| **Action Launcher** | Guided-action launcher on a record | Launch OmniScripts/flows from a record (Visit, Account) | Client-side |
| **LWC** | Lightning Web Component | Custom UI (dashboards, timelines) | Client-side |
| **Apex Service** | Business logic | Inventory reconciliation, eligibility, callouts | Server-side |

---

## OmniScript element types (common in LSC flows)

| Element Type | Purpose | Example (LSC) |
|-------------|---------|---------------|
| **Step** | Container grouping form elements | `RecordSampleDropStep` |
| **Type Ahead** | Autocomplete search | HCP account search |
| **Select** | Dropdown/picklist | Product / lot selector |
| **Edit Block** | Table/grid of records | Sample lines by lot |
| **Set Values** | Assign data to the OmniScript JSON | Default disbursement date |
| **DataRaptor Post Action** | Save via DataRaptor Load | Save sample transaction |
| **IP Action** | Invoke an Integration Procedure | Reconcile inventory |
| **Remote Action** | Call Apex method | Validate HCP eligibility |
| **Signature** | Capture signature | HCP signature on sample drop |
| **Navigate Action** | Redirect on completion | Return to Visit record |
| **Conditional** | Show/hide logic | Show only if licensed to sample |

---

## Action Launcher (LSC guided actions)

LSC surfaces guided quick actions (record a visit, drop a sample, initiate a
product request) via **Action Launcher** on records like Visit or Account. When a
story asks for a "quick action" or "button on the record", model it as an Action
Launcher action that launches an OmniScript/flow — name the launched flow, not a
raw button.

---

## Naming conventions (LSC)

Apply an `LSC_` prefix to new custom components in a net-new LSC build. If the
target org already uses a customer-specific prefix, prefer that; note the choice
in a Clarification Question.

| Component | Pattern | Example |
|-----------|---------|---------|
| OmniScript | `LSC_[FlowName]_English` | `LSC_RecordSampleDrop_English` |
| DataRaptor Extract | `LSCDRExtract[Object][Context]` | `LSCDRExtractProductItemInventory` |
| DataRaptor Load | `LSCDRUpdate[Object][Context]` | `LSCDRUpdateSampleTransaction` |
| Integration Procedure | `LSC_[Name]` | `LSC_InventoryReconciliation` |
| Parent IP | `LSC_[Name]Parent` | `LSC_SampleDropParent` |
| FlexCard | `lsc[ComponentName]` | `lscSampleInventoryCard` |
| LWC | `lsc[ComponentName]` | `lscInventoryTimeline` |
| Apex service | `LSC_[Name]Service` | `LSC_SampleAccountabilityService` |
| Apex selector | `LSC_[Object]Selector` | `LSC_ProductItemSelector` |
| Custom Metadata | `LSC_[Name]__mdt` | `LSC_SampleEligibility__mdt` |
| Custom Field | `LSC_[FieldName]__c` | `LSC_OnHandQuantity__c` |
| Set Values Element | `SV_[Name]` | `SV_DisbursementDefaults` |
| IP Action Element | `IP[Name]` | `IPReconcileInventory` |

Prefer **standard LSC objects/fields** over new custom ones; only introduce
`LSC_*` custom metadata when the standard model cannot carry the requirement.
