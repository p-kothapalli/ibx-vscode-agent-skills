---
name: building-omnistudio-integration-procedure
description: 'OmniStudio Integration Procedure creation and validation with 110-point scoring.
  Use this skill when building server-side process orchestrations that combine Data Mapper
  actions, Apex Remote Actions, HTTP callouts, and conditional logic. TRIGGER when: user creates
  Integration Procedures, adds Data Mapper steps, configures Remote Actions, or reviews existing
  IP configurations. DO NOT TRIGGER when: building OmniScripts (use building-omnistudio-omniscript),
  creating Data Mappers directly (use building-omnistudio-datamapper), or analyzing cross-component
  dependencies (use analyzing-omnistudio-dependencies).'
metadata:
  version: 1.0-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/building-omnistudio-integration-procedure
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
argument-hint: '[IP name or orchestration goal]'
---

# building-omnistudio-integration-procedure: OmniStudio Integration Procedure Creation and Validation

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/building-omnistudio-integration-procedure` if it does not auto-load.


Expert OmniStudio Integration Procedure (IP) builder with deep knowledge of server-side process orchestration. Create production-ready IPs that combine DataRaptor/Data Mapper actions, Apex Remote Actions, HTTP callouts, conditional logic, and nested procedure calls into declarative multi-step operations.

## Scope

- **In scope**: Creating well-structured Integration Procedures from requirements; selecting and wiring element types (DataRaptor, Remote Action, HTTP, Conditional Block, Loop, Set Values, nested IP); dependency validation; error handling patterns; 110-point scoring; deployment and activation
- **Out of scope**: Building OmniScripts (use `building-omnistudio-omniscript`), creating Data Mappers directly (use `building-omnistudio-datamapper`), designing FlexCards (use `building-omnistudio-flexcard`), mapping full dependency trees (use `analyzing-omnistudio-dependencies`), deploying metadata to org (use `deploying-metadata`)

---

## Required Inputs

- **Purpose**: What business process is this IP orchestrating? (e.g., "onboard a new account", "process an order")
- **Target objects / data sources**: Which Salesforce objects, external APIs, or both?
- **Type / SubType naming**: PascalCase pair that uniquely identifies the IP (e.g., `Type=OrderProcessing`, `SubType=Standard`)
- **Target org alias**: Authenticated org alias for deployment (e.g., `myDevOrg`)

---

## Quick Reference

**Scoring**: 110 points across 6 categories. **Thresholds**: 90+ (Deploy) | 67-89 (Review) | <67 (Block - fix required)

---

## Core Responsibilities

1. **IP Generation**: Create well-structured Integration Procedures from requirements, selecting correct element types and wiring inputs/outputs
2. **Element Composition**: Assemble DataRaptor actions, Remote Actions, HTTP callouts, conditional blocks, loops, and nested IP calls into coherent orchestrations
3. **Dependency Analysis**: Validate that referenced DataRaptors, Apex classes, and nested IPs exist and are active before deployment
4. **Error Handling**: Enforce try/catch patterns, conditional rollback, and response validation across all data-modifying steps (DML — Data Manipulation Language)

---

## CRITICAL: Orchestration Order

**analyzing-omnistudio-dependencies -> building-omnistudio-datamapper -> building-omnistudio-integration-procedure -> building-omnistudio-omniscript -> building-omnistudio-flexcard** (you are here: building-omnistudio-integration-procedure)

Data Mappers referenced by the IP must exist FIRST. Build and deploy DataRaptors/Data Mappers before the IP that calls them. The IP must be active before any OmniScript or FlexCard can invoke it.

---

## Key Insights

| Insight | Details |
|---------|---------|
| **Chaining** | IPs call other IPs via Integration Procedure Action elements. Output of one step feeds input of the next via response mapping. Design data flow linearly where possible. |
| **Response Mapping** | Each element's output is namespaced under its element name in the response JSON. Use `%elementName:keyPath%` syntax to reference upstream outputs in downstream inputs. |
| **Caching** | IPs support platform cache for read-heavy orchestrations. Set `cacheType` and `cacheTTL` in the procedure's PropertySet. Avoid caching procedures that perform DML. |
| **Versioning** | Type/SubType pairs uniquely identify an IP. Use SubType for versioning (e.g., `Type=AccountOnboarding`, `SubType=v2`). Only one version can be active at a time per Type/SubType. |

**Core Namespace Discriminator**: OmniStudio Core stores both Integration Procedures and OmniScripts in the `OmniProcess` table. Use `IsIntegrationProcedure = true` or `OmniProcessType = 'Integration Procedure'` to filter IPs. Without a filter, queries return mixed results.

> **CRITICAL — Creating IPs via Data API**: When creating OmniProcess records, set `IsIntegrationProcedure = true` to make the record an Integration Procedure. The `OmniProcessType` picklist is **computed from this boolean** and cannot be set directly. Also, `Name` is a required field on `OmniProcess` (not documented in standard OmniStudio docs). Use `sf api request rest --method POST --body @file.json` for creation — the `sf data create record --values` flag cannot handle JSON textarea fields like `PropertySetConfig`. (NOTE: in IBX this REST path is NOT used — see IBX Overrides.)

---

## Workflow Design (5-Phase Pattern)

### Phase 1: Requirements Gathering

**Before building, evaluate alternatives**: Sometimes a single DataRaptor, an Apex service, or a Flow is the better choice. IPs are optimal when you need declarative multi-step orchestration with branching, error handling, and mixed data sources.

**Ask the user** to gather:
- Purpose and business process being orchestrated
- Target objects and data sources (Salesforce objects, external APIs, or both)
- Type/SubType naming (e.g., `Type=OrderProcessing`, `SubType=Standard`)
- Target org alias for deployment

**Then**: Check existing IPs via CLI query (see CLI Commands below), identify reusable DataRaptors/Data Mappers, and review dependent components with analyzing-omnistudio-dependencies.

### Phase 2: Design & Element Selection

| Element Type | Use Case | PropertySet Key |
|--------------|----------|-----------------|
| DataRaptor Extract Action | Read Salesforce data | `bundle` |
| DataRaptor Load Action | Write Salesforce data | `bundle` |
| DataRaptor Transform Action | Data shaping/mapping | `bundle` |
| Remote Action | Call Apex class method | `remoteClass`, `remoteMethod` |
| Integration Procedure Action | Call nested IP | `ipMethod` (format: `Type_SubType`) |
| HTTP Action | External API callout | `path`, `method` |
| Conditional Block | Branching logic | -- |
| Loop Block | Iterate over collections | -- |
| Set Values | Assign variables/constants | -- |

**Naming Convention**: `[Type]_[SubType]` using PascalCase. Element names within the IP should describe their action clearly (e.g., `GetAccountDetails`, `ValidateInput`, `CreateOrderRecord`).

**Data Flow**: Design the element chain so each step's output feeds naturally into the next step's input. Map outputs explicitly rather than relying on implicit namespace merging.

### Phase 3: Generation & Validation

Build the IP definition with:
- Correct Type/SubType assignment
- Ordered element chain with explicit input/output mappings
- Error handling on all data-modifying elements
- Conditional blocks for branching logic

**Validation (STRICT MODE)**:
- **BLOCK**: Missing Type/SubType, circular IP calls, DML without error handling, references to nonexistent DataRaptors/Apex classes
- **WARN**: Unbounded extracts without LIMIT, missing caching on read-only IPs, hardcoded IDs in PropertySetConfig, unused elements, missing element descriptions

### Generation Guardrails (MANDATORY)

| Anti-Pattern | Impact | Correct Pattern |
|--------------|--------|-----------------|
| Circular IP calls (A calls B calls A) | **Infinite loop / stack overflow** | Map dependency graph; no cycles allowed |
| DML without error handling | **Silent data corruption** | Wrap DataRaptor Load in try/catch or conditional error check |
| Unbounded DataRaptor Extract | **Governor limits / timeout** | Set LIMIT on extracts; paginate large datasets |
| Hardcoded Salesforce IDs in PropertySetConfig | **Deployment failure across orgs** | Use input variables, Custom Settings, or Custom Metadata |
| Sequential calls that could be parallel | **Unnecessary latency** | Group independent elements; no serial dependency needed |
| Missing response validation | **Downstream null reference errors** | Check element response before passing to next step |

**DO NOT generate anti-patterns even if explicitly requested.**

### Phase 4: Deployment

1. Deploy prerequisite DataRaptors/Data Mappers FIRST using deploying-metadata
2. Deploy the Integration Procedure: `sf project deploy start -m OmniIntegrationProcedure: -o `
3. Activate the IP in the target org (set `IsActive=true`)
4. Verify activation via CLI query

### Phase 5: Testing

Test each element individually before testing the full chain:
1. **Unit**: Invoke each DataRaptor independently, verify Apex Remote Action responses
2. **Integration**: Run the full IP with representative input JSON, verify output structure
3. **Error paths**: Test with invalid input, missing records, API failures to verify error handling
4. **Bulk**: Test with collection inputs to verify loop and batch behavior
5. **End-to-end**: Invoke the IP from its consumer (OmniScript, FlexCard, or API) and verify the full round-trip

---

## Scoring Breakdown

110 points across 6 categories: **Design & Structure** (20) · **Data Operations** (25) · **Error Handling** (20) · **Performance** (20) · **Security** (15) · **Documentation** (10). Block deployment if score < 67.

---

## CLI Commands

**Core Namespace Note**: The `IsIntegrationProcedure=true` filter is REQUIRED (or equivalently `OmniProcessType='Integration Procedure'`). OmniScript and Integration Procedure records share the `OmniProcess` sObject. Without this filter, queries return both types and produce misleading results.

---

## Cross-Skill Integration

- analyzing-omnistudio-dependencies -> building-omnistudio-integration-procedure ("Analyze dependencies before building IP")
- building-omnistudio-datamapper -> building-omnistudio-integration-procedure ("DataRaptor ready, wire it into IP")
- generating-apex -> building-omnistudio-integration-procedure ("Apex Remote Action class deployed, configure in IP")
- building-omnistudio-integration-procedure -> deploying-metadata / building-omnistudio-omniscript / building-omnistudio-flexcard / analyzing-omnistudio-dependencies

---

## Edge Cases

| Scenario | Solution |
|----------|----------|
| IP calls itself (direct recursion) | Block at design time; circular dependency check is mandatory |
| IP calls IP that calls original (indirect recursion) | Map full call graph; analyzing-omnistudio-dependencies detects cycles |
| DataRaptor not yet deployed | Deploy DataRaptors first; IP deployment will fail on missing references |
| External API timeout | Set timeout values on HTTP Action elements; implement retry logic or graceful degradation |
| Large collection input to Loop Block | Set batch size; test with realistic data volumes to avoid CPU timeout |
| Type/SubType collision with existing IP | Query existing IPs before creating; SubType versioning avoids collisions |
| Mixed namespace (Vlocity vs Core) | Confirm org namespace; element property names differ between packages |

**Debug**: IP not executing -> check IsActive flag + Type/SubType match | Elements skipped -> verify conditional block logic + input data shape | Timeout -> check DataRaptor query scope + HTTP timeout settings | Deployment failure -> verify all referenced components deployed and active

---

## Notes

**API**: 66.0 | **Mode**: Strict (warnings block) | **Scoring**: Block deployment if score < 67

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win. Grounded in the **1,483** Integration
> Procedures under `force-app/main/default/omniIntegrationProcedures/`.

### 1 — Source Format, NOT REST Record Creation (most important)

IBX manages OmniStudio as **SFDX metadata source**, version-controlled in the repo. The upstream "create `OmniProcess` records via `sf api request rest --method POST`" workflow is **NOT used here**.

- IPs live as `force-app/main/default/omniIntegrationProcedures/<Name>.oip-meta.xml`.
- Edit the metadata source (or author in OmniStudio Designer and retrieve), then deploy via the Metadata API:

```bash
# Retrieve an IP from the org
sf project retrieve start -m OmniIntegrationProcedure:PRM_VerifyPractitionerDetails_Procedure_30 -o qa-sandbox

# Deploy an IP (and dependencies) to the org
sf project deploy start -m OmniIntegrationProcedure:PRM_VerifyPractitionerDetails_Procedure_30 -o qa-sandbox --wait 10
```

- For cross-org migration, IBX also uses **Vlocity Build datapacks** (`export-omnistudio.yaml`) — see `deploying-omnistudio-datapacks`.

### 2 — Namespace = `omnistudio` Managed Package (metadata-driven)

- The org runs the **OmniStudio managed package** (`omnistudio` runtime namespace), but `sfdx-project.json` has an **empty namespace** — custom assets are **not** namespace-prefixed; they use the `PRM` prefix.
- Therefore the metadata type is the Core-style `OmniIntegrationProcedure` (not `vlocity_cmt__`/`vlocity_ins__`). Do not apply a `vlocity_*` prefix.

### 3 — Naming Convention (verified)

IPs follow `PRM_<ProcessName>_<SubType>_<Version>`:
- `PRM_VerifyPractitionerDetails_Procedure_30` (SubType `Procedure`)
- `PRM_FetchDetailsForNoCAQH_English_1` (SubType `English`)
- `PRM_DelegatedPractitionerCreation_Procedure_3`

Rules: `PRM_` prefix is mandatory; Type is `PRM_<PascalCaseName>`; SubType is usually `Procedure` (or `English` for older assets); the trailing integer is the **version number**.

### 4 — Active-Version Rule (critical)

Each IP has **many versions** (e.g., `..._Procedure_29`, `..._Procedure_30`). Only the file/record with `<isActive>true</isActive>` is live at runtime.

- **Always ground edits against the active version.** Identify it before changing anything.
- Never edit a stale/inactive version assuming it is live.
- Activating a new version deactivates the prior one (one active version per Type/SubType).

### 5 — Graph-First Dependency Checks

Per the project rules, before tracing which OmniScripts/FlexCards/Apex consume or feed an IP, use the **code-review-graph MCP** tools (`semantic_search_nodes`, `query_graph`, `get_impact_radius`) first; fall back to `analyzing-omnistudio-dependencies` / Grep only if the graph returns nothing.

### 6 — Apex Remote Actions Use `omnistudio.VlocityOpenInterface2`

Remote Action elements call Apex implementing `omnistudio.VlocityOpenInterface2`, routing by `methodName`, writing to `outMap`, and logging via `PRM_ExceptionLogger`. See `building-omnistudio-callable-apex` and the `generating-apex` IBX overrides for the full pattern.

### 7 — IBX Review Checklist

- [ ] Asset edited as `.oip-meta.xml` source and deployed with `sf project deploy start -m OmniIntegrationProcedure:` (no REST record creation)
- [ ] `PRM_` naming with correct `Type_SubType_Version`
- [ ] Change targets the **active** version (verified)
- [ ] Referenced DataRaptors / IPs / Apex exist and are active (graph-checked)
- [ ] DML (DataRaptor Load) steps have error handling; no hardcoded Salesforce IDs
- [ ] Extracts bounded with filters/limits; read-only IPs consider caching
- [ ] Apex Remote Actions use `omnistudio.VlocityOpenInterface2` + `PRM_ExceptionLogger`
