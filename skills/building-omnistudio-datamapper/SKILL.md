---
name: building-omnistudio-datamapper
description: 'OmniStudio Data Mapper (formerly DataRaptor) creation and validation with 100-point
  scoring. Use when building Extract, Transform, Load, or Turbo Extract Data Mappers, mapping
  Salesforce object fields, or reviewing existing Data Mapper configurations. TRIGGER when:
  user creates Data Mappers, configures field mappings, works with OmniDataTransform metadata,
  or asks about DataRaptor/Data Mapper patterns. DO NOT TRIGGER when: building Integration
  Procedures (use building-omnistudio-integration-procedure), authoring OmniScripts (use building-omnistudio-omniscript),
  or analyzing cross-component dependencies (use analyzing-omnistudio-dependencies).'
metadata:
  version: 1.0-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/building-omnistudio-datamapper
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
argument-hint: '[Extract/Transform/Load and objects]'
---

# building-omnistudio-datamapper: OmniStudio Data Mapper Creation and Validation

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/building-omnistudio-datamapper` if it does not auto-load.


Expert OmniStudio Data Mapper developer specializing in Extract, Transform, Load, and Turbo Extract configurations. Generate production-ready, performant, and maintainable Data Mapper definitions with proper field mappings, query optimization, and data integrity safeguards.

---

## Scope

- **In scope**: Creating and validating OmniStudio Data Mapper configurations (Extract, Transform, Load, Turbo Extract); field mapping design; query optimization; FLS (Field-Level Security) validation; deployment via deploying-metadata skill
- **Out of scope**: Building Integration Procedures (use `building-omnistudio-integration-procedure`), authoring OmniScripts (use `building-omnistudio-omniscript`), designing FlexCards (use `building-omnistudio-flexcard`), analyzing cross-component dependencies (use `analyzing-omnistudio-dependencies`)

---

## Core Responsibilities

1. **Generation**: Create Data Mapper configurations (Extract, Transform, Load, Turbo Extract) from requirements
2. **Field Mapping**: Design object-to-output field mappings with proper type handling, lookup resolution, and null safety
3. **Dependency Tracking**: Identify related OmniStudio components (Integration Procedures, OmniScripts, FlexCards) that consume or feed Data Mappers
4. **Validation & Scoring**: Score Data Mapper configurations against 5 categories (0-100 points)

---

## CRITICAL: Orchestration Order

**analyzing-omnistudio-dependencies -> building-omnistudio-datamapper -> building-omnistudio-integration-procedure -> building-omnistudio-omniscript -> building-omnistudio-flexcard** (you are here: building-omnistudio-datamapper)

Data Mappers are the data access layer of the OmniStudio stack. They must be created and deployed before Integration Procedures or OmniScripts that reference them. Use analyzing-omnistudio-dependencies FIRST to understand existing component dependencies.

---

## Key Insights

| Insight | Details |
|---------|---------|
| **Extract vs Turbo Extract** | Extract uses standard SOQL with relationship queries. Turbo Extract uses server-side compiled queries for read-heavy, high-volume scenarios (10x+ faster). Turbo Extract does not support formula fields, related lists, or write operations. |
| **Transform is in-memory** | Transform Data Mappers operate entirely in memory with no DML or SOQL. They reshape data structures between steps in an Integration Procedure. Use for JSON-to-JSON transformations, field renaming, and data flattening. |
| **Load = DML** | Load Data Mappers perform insert, update, upsert, or delete operations. They require proper FLS checks and error handling. Always validate field-level security before deploying Load Data Mappers to production. |
| **OmniDataTransform metadata** | Data Mappers are stored as OmniDataTransform and OmniDataTransformItem records. Retrieve and deploy using these metadata type names, not the legacy DataRaptor API names. |

---

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

**Ask the user** to gather:
- Data Mapper type (Extract, Transform, Load, Turbo Extract)
- Target Salesforce object(s) and fields
- Target org alias
- Consuming component (Integration Procedure, OmniScript, or FlexCard name)
- Data volume expectations (record counts, frequency)

**Then**:
1. Check existing Data Mappers: `Glob: **/OmniDataTransform*`
2. Check existing OmniStudio metadata: `Glob: **/omnistudio/**`
3. Create a task list

---

### Phase 2: Design & Type Selection

| Type | Use Case | Naming Prefix | Supports DML | Supports SOQL |
|------|----------|---------------|--------------|---------------|
| **Extract** | Read data from one or more objects with relationship queries | `DR_Extract_` | No | Yes |
| **Turbo Extract** | High-volume read-only queries, server-side compiled | `DR_TurboExtract_` | No | Yes (compiled) |
| **Transform** | In-memory data reshaping between procedure steps | `DR_Transform_` | No | No |
| **Load** | Write data (insert, update, upsert, delete) | `DR_Load_` | Yes | No |

**Upstream Naming Format**: `[Prefix][Object]_[Purpose]` using PascalCase (see IBX Overrides for this org's actual convention).

**Examples**:
- `DR_Extract_Account_Details` -- Extract Account with related Contacts
- `DR_TurboExtract_Case_List` -- High-volume Case list for FlexCard
- `DR_Transform_Lead_Flatten` -- Flatten nested Lead data structure
- `DR_Load_Opportunity_Create` -- Insert Opportunity records

---

### Phase 3: Generation & Validation

**For Generation**:
1. Configure query filters, sort order, and limits for Extract types
2. Set up lookup mappings and default values for Load types
3. Validate field-level security for all mapped fields

**For Review**:
1. Read existing Data Mapper configuration
2. Run validation against best practices
3. Generate improvement report with specific fixes

---

### Generation Guardrails (MANDATORY)

If ANY of these patterns would be generated, **STOP and ask the user**.

| Anti-Pattern | Detection | Impact |
|--------------|-----------|--------|
| Extracting all fields | No field list specified, wildcard selection | Performance degradation, excessive data transfer |
| Missing lookup mappings | Load references lookup field without resolution | DML failure, null foreign key |
| Writing without FLS check | Load Data Mapper with no security validation | Security violation, data corruption in restricted profiles |
| Unbounded Extract query | No LIMIT or filter on Extract | Governor limit failure, timeout on large objects |
| Transform with side effects | Transform attempting DML or callout | Runtime error, Transform is in-memory only |
| Hardcoded record IDs | 15/18-char ID literal in filter or mapping | Deployment failure across environments |
| Nested relationship depth >3 | Extract with deeply nested parent traversal | Query performance degradation, SOQL complexity limits |
| Load without error handling | No upsert key or duplicate rule consideration | Silent data corruption, duplicate records |

**DO NOT generate anti-patterns even if explicitly requested.**

---

### Phase 4: Deployment

**Step 1: Validation** — Use the **deploying-metadata** skill with `--dry-run`.
**Step 2: Deploy** (only if validation succeeds).
**Post-Deploy**: Activate the Data Mapper in the target org. Verify it appears in OmniStudio Designer.

**If deploy fails**: Check error for specific cause — common issues: `Entity cannot be found` (Data Mapper is in Draft status; activate first), namespace prefix mismatch, or missing parent `OmniDataTransform` record for item deployments.

**If Load DM fails at runtime**: Check debug logs via `sf apex log list -o `; verify FLS and object permissions for the running user profile; confirm the upsert key field is populated and unique; Load DMs follow `allOrNone=false` by default — partial successes are possible, check for `isSuccess=false` rows.

---

### Phase 5: Testing & Documentation

**Testing Checklist**:
- [ ] Preview data output in OmniStudio Designer
- [ ] Verify field mappings produce expected JSON structure
- [ ] Test with representative data volume (not just 1 record)
- [ ] Validate FLS enforcement with restricted profile user
- [ ] Confirm consuming Integration Procedure/OmniScript receives correct data shape

---

## Best Practices (100-Point Scoring)

| Category | Points | Key Rules |
|----------|--------|-----------|
| **Design & Naming** | 20 | Correct type selection; naming follows convention; single responsibility per Data Mapper |
| **Field Mapping** | 25 | Explicit field list (no wildcards); correct input/output paths; proper type conversions; null-safe default values |
| **Data Integrity** | 25 | FLS validation on all fields; lookup resolution for Load types; upsert keys defined; duplicate handling configured |
| **Performance** | 15 | Bounded queries with LIMIT/filters; Turbo Extract for read-heavy scenarios; minimal relationship depth; indexed filter fields |
| **Documentation** | 15 | Description on OmniDataTransform record; field mapping rationale documented; consuming components identified |

**Thresholds**: 90+ (Deploy) | 67-89 (Review) | <67 (Block - fix required)

---

## CLI Commands

```bash
# Query existing Data Mappers
sf data query -q "SELECT Id,Name,Type FROM OmniDataTransform LIMIT 200" -o <org>

# Query Data Mapper field mappings (FK is OmniDataTransformationId — full word)
sf data query -q "SELECT Id,Name,InputObjectName,OutputObjectName,LookupObjectName FROM OmniDataTransformItem WHERE OmniDataTransformationId='<id>' LIMIT 200" -o <org>

# Retrieve / Deploy Data Mapper metadata
sf project retrieve start -m OmniDataTransform:<Name> -o <org>
sf project deploy start -m OmniDataTransform:<Name> -o <org>
```

---

## Gotchas

| Issue | Resolution |
|-------|-----------|
| Large data volume (>10K records) | Use Turbo Extract; add pagination via Integration Procedure; warn about heap limits |
| Polymorphic lookup fields | Specify the concrete object type in the mapping; test each type separately |
| Formula fields in Extract | Standard Extract supports formula fields; Turbo Extract does not — fall back to standard Extract |
| Cross-object Load (master-detail) | Insert parent records first, then child records in a separate Load step; orchestrate sequence via IP |
| Namespace-prefixed fields | Include namespace prefix in field paths; verify prefix matches target org |
| Multi-currency orgs | Map CurrencyIsoCode explicitly |
| RecordType-dependent mappings | Filter by RecordType in Extract; set RecordTypeId in Load |
| Draft Data Mapper not retrievable | Activate before retrieving |
| Foreign key field name wrong | The parent lookup on `OmniDataTransformItem` is `OmniDataTransformationId` (full word "Transformation") |

---

## Notes

- **Metadata Type**: OmniDataTransform (not DataRaptor — legacy name deprecated)
- **Turbo Extract Limitations**: No formula fields, no related lists, no aggregate queries, no polymorphic fields
- **Activation**: Data Mappers must be activated after deployment to be callable

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win. Grounded in the **1,409** Data Mappers
> under `force-app/main/default/omniDataTransforms/`.

### 1 — Source Format, NOT REST Record Creation (most important)

IBX manages Data Mappers as **SFDX metadata source**, not via `sf api request rest` record creation.

- DataRaptors live as `force-app/main/default/omniDataTransforms/<Name>_<Version>.rpt-meta.xml`.
- Edit the source (or author in OmniStudio Designer and retrieve), then deploy via the Metadata API:

```bash
sf project retrieve start -m OmniDataTransform:PRMDRExtractPracticeLocation_1 -o qa-sandbox
sf project deploy start  -m OmniDataTransform:PRMDRExtractPracticeLocation_1 -o qa-sandbox --wait 10
```

- For cross-org migration, IBX also uses **Vlocity Build datapacks** (`export-omnistudio.yaml`) — see `deploying-omnistudio-datapacks`.

### 2 — Namespace = `omnistudio` Managed Package

- Metadata type is the Core-style `OmniDataTransform` (not `vlocity_cmt__DRBundle__c`). `sfdx-project.json` namespace is empty; custom assets are not namespace-prefixed.

### 3 — Naming Convention (verified — differs from upstream `DR_Type_Object_Purpose`)

IBX uses two grounded styles; the trailing integer is the **version**:
- **Preferred (new):** `PRMDR<Verb><Subject>_<Version>` — e.g. `PRMDRExtractPracticeLocation_1`, `PRMDRTransformAddData_1`, `PRMDRCreateCDMForPractitioner_1`. Also `PRM<...>` for create/transform helpers (`PRMCreateNewCase_1`, `PRMCredentialingTransform_1`).
- **Legacy:** `DR<Verb><Subject>_<Version>` — e.g. `DRExtractCase_1`, `DRGetMedicareIdentifier_1`, `DRTransformNwTaxonomyPDM_1`.

Rules: use the **`PRMDR`** form for new Data Mappers; keep the verb (`Extract`/`Transform`/`Create`/`Get`/`Load`) in the name; do not rename legacy `DR*`/`PRM*` assets. The upstream `DR_Extract_` underscore-delimited convention is **not** used here.

### 4 — Active-Version Rule (critical)

Each Data Mapper has versions (the `_N` suffix). Only the active version is live. **Always ground edits against the active version**; activating a new version supersedes the prior one.

### 5 — Graph-First Dependency Checks

Before tracing which IPs/OmniScripts/FlexCards consume a Data Mapper, use the **code-review-graph MCP** tools first; fall back to `analyzing-omnistudio-dependencies` / Glob only if the graph returns nothing.

### 6 — Security: `WITH USER_MODE` Equivalence

Load Data Mappers must enforce FLS (the project standard mirrors the Apex `WITH USER_MODE` rule). Validate field-level security for every mapped field before deploying any Load DM to a restricted-profile environment.

### 7 — IBX Review Checklist

- [ ] Asset edited as `.rpt-meta.xml` source and deployed with `sf project deploy start -m OmniDataTransform:` (no REST record creation)
- [ ] New DM named `PRMDR<Verb><Subject>_<Version>`; legacy `DR*`/`PRM*` left as-is
- [ ] Change targets the **active** version (verified)
- [ ] Explicit field list (no wildcards); lookups resolved on Load; upsert keys defined
- [ ] FLS validated on all mapped fields; no hardcoded Salesforce IDs
- [ ] Extracts bounded with filters/LIMIT; Turbo Extract considered for high-volume reads
- [ ] Consuming IP/OmniScript/FlexCard identified (graph-checked)
