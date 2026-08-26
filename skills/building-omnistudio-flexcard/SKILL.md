---
name: building-omnistudio-flexcard
description: 'OmniStudio FlexCard creation and validation with 130-point scoring. Use when
  building at-a-glance UI cards, configuring data source bindings to Integration Procedures,
  or reviewing existing FlexCard definitions for accessibility and performance. TRIGGER when:
  user creates FlexCards, configures data sources, designs card layouts, or asks about OmniUiCard
  metadata. DO NOT TRIGGER when: building OmniScripts (use building-omnistudio-omniscript),
  creating Integration Procedures (use building-omnistudio-integration-procedure), or analyzing
  dependencies (use analyzing-omnistudio-dependencies).'
metadata:
  version: 1.0-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/building-omnistudio-flexcard
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
---

# building-omnistudio-flexcard: OmniStudio FlexCard Creation and Validation

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/building-omnistudio-flexcard` if it does not auto-load.


Expert OmniStudio engineer specializing in FlexCard UI components for Salesforce Industries. Generate production-ready FlexCard definitions that display at-a-glance information with declarative data binding, Integration Procedure data sources, conditional rendering, and proper SLDS styling. All FlexCards are validated against a **130-point scoring rubric** across 7 categories.

## Scope

- **In scope**: Creating and validating OmniStudio FlexCard definitions (`OmniUiCard`); configuring Integration Procedure data sources; designing card layouts, states, and action buttons; scoring against the 130-point rubric; deployment and activation
- **Out of scope**: Building OmniScripts (use `building-omnistudio-omniscript`), creating Integration Procedures (use `building-omnistudio-integration-procedure`), mapping full dependency trees (use `analyzing-omnistudio-dependencies`), deploying metadata to org (use `deploying-metadata`)

---

## Core Responsibilities

1. **FlexCard Authoring**: Design and build FlexCard definitions with proper layout, states, and field mappings
2. **Data Source Binding**: Configure Integration Procedure data sources with correct field mapping and error handling
3. **Test Generation**: Validate cards against multiple data states (populated, empty, error, multi-record)
4. **Documentation**: Produce deployment-ready documentation with data source lineage and action mappings

---

## CRITICAL: Orchestration Order

```
analyzing-omnistudio-dependencies → building-omnistudio-datamapper → building-omnistudio-integration-procedure → building-omnistudio-omniscript → building-omnistudio-flexcard (you are here)
```

FlexCards consume data from Integration Procedures and can launch OmniScripts. Build the data layer first, then the presentation layer.

---

## Key Insights

| Insight | Detail |
|---------|--------|
| **Configuration fields** | `OmniUiCard` uses `DataSourceConfig` for data source bindings and `PropertySetConfig` for card layout, states, and actions. There is NO `Definition` field on `OmniUiCard` in Core namespace. |
| **Data source binding** | Data sources bind to Integration Procedures for live data; the IP must be active and deployed before the FlexCard can retrieve data |
| **Child card embedding** | FlexCards can embed other FlexCards as child cards, enabling composite layouts |
| **OmniScript launching** | FlexCards can launch OmniScripts via action buttons, passing context data |
| **Designer virtual object** | The FlexCard Designer uses `OmniFlexCardView` as a virtual list object, separate from the `OmniUiCard` sObject where card records are stored |

---

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Clarify: card purpose, data sources needed (which IPs), object context (record vs list), actions exposed, layout type, conditional display rules.

### Phase 2: Design & Layout

**Card Layout Options**: Single Card (record summary), Card List (related records / array data source), Tabbed Card (multi-context), Flyout Card (detail on demand).

**Data Source Configuration**: Each data source connects to an Integration Procedure and maps response fields to display elements.
```
FlexCard → Data Source (type: IntegrationProcedures)
         → IP Name + Input Mapping
         → Response Field Mapping → Card Elements
```
- Map IP response fields with `{datasource.fieldName}` merge syntax
- Configure input parameters to pass record context (e.g., `{recordId}`) to the IP

**Action Button Design**: Launch OmniScript (Type+SubType, pass context params), Navigate (record/URL), Custom Action (platform event, LWC).

**Conditional Visibility**: Show/hide fields and states based on data values; display empty-state messaging when no records.

### Phase 3: Generation & Validation

1. Generate the FlexCard definition JSON
2. Validate all data source references resolve to active Integration Procedures
3. Run the 130-point scoring rubric
4. Verify merge field syntax matches IP response structure
5. Check accessibility attributes on all interactive elements

### Phase 4: Deployment

1. Ensure all upstream Integration Procedures are deployed and active
2. Run a dry-run check via `deploying-metadata`
3. Deploy the FlexCard metadata (`OmniUiCard`)
4. Activate the FlexCard in the target org
5. Embed in the target Lightning page, OmniScript, or parent FlexCard

### Phase 5: Testing

Test against: populated data, empty data, error state, multi-record, action buttons, conditional fields, mobile.

---

## Generation Guardrails

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|---------------|-----------------|
| Referencing non-existent IP data sources | Card fails to load data at runtime | Verify IP exists and is active before binding |
| Hardcoded colors in styles | Breaks SLDS theming and dark mode | Use SLDS design tokens and CSS custom properties |
| Missing accessibility attributes | Fails WCAG compliance | Add `aria-label`, `role`, and keyboard handlers |
| Excessive nested child cards | Performance degrades with deep nesting | Limit to 2 levels of nesting |
| Ignoring empty states | Broken UI when data source returns no records | Configure explicit empty-state messaging |
| Hardcoded record IDs | Card breaks across environments | Use merge fields and context-driven parameters |

---

## Scoring Rubric (130 Points)

**Design & Layout** (25) · **Data Binding** (20) · **Actions & Navigation** (20) · **Styling** (20) · **Accessibility** (15) · **Testing** (15) · **Performance** (15). **Thresholds**: 90+ (Deploy) | 67-89 (Review) | <67 (Block).

---

## Data Source Binding

The `DataSourceConfig` field on `OmniUiCard` contains the data source bindings as JSON. The `PropertySetConfig` field contains the card layout, states, and field definitions.

> **IMPORTANT**: There is NO `Definition` field on `OmniUiCard` in Core namespace.

### Data Source Types

| Type | `dataSource.type` | When to Use |
|------|-------------------|-------------|
| **Integration Procedure** | `IntegrationProcedures` (plural, capital P) | Primary pattern; calls an IP for live data |
| **SOQL** | `SOQL` | Direct query (use sparingly; prefer IP) |
| **Apex Remote** | `ApexRemote` | Custom Apex class invocation |
| **REST** | `REST` | External API call via Named Credential |
| **Custom** | `Custom` | Custom data provider |

### Input Parameter Mapping

Pass context from the hosting page into the IP data source: `{recordId}`, `{userId}`, `{param.customKey}`.

---

## FlexCard vs LWC Decision Guide

| Factor | FlexCard | LWC |
|--------|----------|-----|
| **Build method** | Declarative | Code (JS, HTML, CSS) |
| **Data binding** | Integration Procedure merge fields | Wire service, Apex, GraphQL |
| **Best for** | At-a-glance information display | Complex interactive UIs |
| **When to choose** | Standard card layouts with IP data | Custom behavior, animations, complex state |

---

## Gotchas

| Scenario | Handling |
|----------|---------|
| **Empty data** | Configure an explicit empty-state with a user-friendly message |
| **Error states** | Display a meaningful error message when the IP data source fails |
| **Mobile responsiveness** | Single-column layout for mobile; test at 320px |
| **Large record sets** | Card list with pagination; limit initial load to 10-25 records |
| **Null field values** | Use conditional visibility to hide null fields |

---

## Dependencies

**Required**: Target org with OmniStudio license, `sf` CLI authenticated. **For Data Sources**: Active Integration Procedures deployed. **For Actions**: Active OmniScripts deployed. **Scoring**: Block deployment if score < 67.

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win. Grounded in the **37** FlexCards under
> `force-app/main/default/omniUiCard/`.

### 1 — Source Format, NOT REST Record Creation (most important)

IBX manages FlexCards as **SFDX metadata source**, not via `sf api request rest` record creation.

- FlexCards live as `force-app/main/default/omniUiCard/<Name>_<SubType>_<Version>.ouc-meta.xml`.
- Edit the source (or author in OmniStudio Designer and retrieve), then deploy via the Metadata API:

```bash
sf project retrieve start -m OmniUiCard:PRMPractitionerDemographics_IBX_7 -o qa-sandbox
sf project deploy start  -m OmniUiCard:PRMPractitionerDemographics_IBX_7 -o qa-sandbox --wait 10
```

- For cross-org migration, IBX also uses **Vlocity Build datapacks** (`export-omnistudio.yaml`) — see `deploying-omnistudio-datapacks`.

### 2 — Namespace = `omnistudio` Managed Package

- Metadata type is the Core-style `OmniUiCard` (uses `DataSourceConfig` + `PropertySetConfig`, no `Definition` field). `sfdx-project.json` namespace is empty; custom assets are not namespace-prefixed.

### 3 — Naming Convention (verified)

FlexCards follow `PRM<CardName>_<SubType>_<Version>`:
- `PRMPractitionerDemographics_IBX_7`
- `PRMMainGroupSelection_IBX_6`
- `PRMCredentialingFlowsFlexCard_IBX_10`
- `PRMCardDisplayLocationHistoryNPI_IndependenceBlueCross_1`

Rules: `PRM` prefix (no underscore after PRM for FlexCards, unlike IP/OmniScript); SubType is usually `IBX` (or `IndependenceBlueCross` on older cards); trailing integer is the **version**. Child cards are suffixed accordingly (e.g., `PRMSupplierInfoChild_IBX_2`).

### 4 — Active-Version Rule (critical)

FlexCards have many versions (e.g., `PRMMainGroupSelection_IBX_1..6`, `PRMProviderMgmtFlowsFlexCard_IBX_1..11`). Only `<isActive>true</isActive>` is live.

- **Always ground edits against the active version**; activating a new version supersedes the prior one.

### 5 — Data Sources Are IPs (`IntegrationProcedures`, plural)

IBX FlexCards bind to `PRM_*` Integration Procedures via `DataSourceConfig` with `dataSource.type = 'IntegrationProcedures'`. Verify the referenced IP exists and is the **active** version before binding (graph-check first).

### 6 — Hosting Surfaces

IBX FlexCards are embedded in flexipages, launched from OmniScripts, and embedded as child cards (e.g., the `*FlowsFlexCard` cards drive credentialing/provider-management launch tiles). Confirm the host surface and the OmniScript Type/SubType that action buttons launch.

### 7 — Graph-First Dependency Checks

Before tracing which IPs a FlexCard consumes or which OmniScripts it launches, use the **code-review-graph MCP** tools first; fall back to `analyzing-omnistudio-dependencies` only if the graph returns nothing.

### 8 — IBX Review Checklist

- [ ] Asset edited as `.ouc-meta.xml` source and deployed with `sf project deploy start -m OmniUiCard:` (no REST record creation)
- [ ] `PRM<Card>_<SubType>_<Version>` naming
- [ ] Change targets the **active** version (verified)
- [ ] Data sources reference active `PRM_*` IPs (`IntegrationProcedures` type); merge syntax matches IP response
- [ ] SLDS tokens (no hardcoded colors); accessibility attributes present; empty/error states configured
- [ ] Child-card nesting ≤ 2 levels; action-button OmniScript Type/SubType verified
