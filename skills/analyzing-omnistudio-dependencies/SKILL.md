---
name: analyzing-omnistudio-dependencies
description: 'Cross-cutting OmniStudio analysis skill for namespace detection, dependency
  visualization, and impact analysis across OmniScripts, FlexCards, Integration Procedures,
  and Data Mappers. TRIGGER when: user asks about OmniStudio dependencies, wants namespace
  detection (Core vs vlocity_cmt vs vlocity_ins), needs impact analysis, requests dependency
  graphs or Mermaid diagrams, or asks which components are affected by a change. DO NOT TRIGGER
  when: authoring OmniScripts (use building-omnistudio-omniscript), building FlexCards (use
  building-omnistudio-flexcard), creating Integration Procedures (use building-omnistudio-integration-procedure),
  or configuring Data Mappers (use building-omnistudio-datamapper).'
metadata:
  version: 1.0-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/analyzing-omnistudio-dependencies
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
---

# analyzing-omnistudio-dependencies: OmniStudio Cross-Component Analysis

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/analyzing-omnistudio-dependencies` if it does not auto-load.


Expert OmniStudio analyst specializing in namespace detection, dependency mapping, and impact analysis across the full OmniStudio component suite. Performs org-wide inventory of OmniScripts, FlexCards, Integration Procedures, and Data Mappers with automated dependency graph construction and Mermaid visualization.

---

## Scope

- **In scope**: Namespace detection (Core / vlocity_cmt / vlocity_ins), org-wide component inventory, dependency graph construction, impact analysis, Mermaid diagram generation
- **Out of scope**: Authoring or modifying OmniScripts/FlexCards/IPs/Data Mappers (use the `building-omnistudio-*` skills)

---

## Core Responsibilities

1. **Namespace Detection**: Identify whether an org uses Core (Industries), vlocity_cmt, or vlocity_ins namespace
2. **Dependency Analysis**: Build directed graphs of cross-component dependencies using BFS traversal with circular reference detection
3. **Impact Analysis**: Determine which components are affected when a given OmniScript, IP, FlexCard, or Data Mapper changes
4. **Mermaid Visualization**: Generate dependency diagrams in Mermaid syntax
5. **Org-Wide Inventory**: Catalog all OmniStudio components by type, status, language, and version

---

> **CRITICAL: Orchestration Order**
> `analyzing-omnistudio-dependencies` → `building-omnistudio-datamapper` → `building-omnistudio-integration-procedure` → `building-omnistudio-omniscript` → `building-omnistudio-flexcard`
> This skill runs first to establish namespace context and dependency maps that downstream skills consume.

---

## Key Insights

| Insight | Detail |
|---------|--------|
| Three namespaces coexist | Core (OmniProcess), vlocity_cmt (vlocity_cmt__OmniScript__c), vlocity_ins (vlocity_ins__OmniScript__c) |
| Dependencies are stored in JSON | PropertySetConfig (elements), DataSourceConfig (FlexCards), InputObjectName/OutputObjectName (Data Mappers) |
| Circular references are possible | OmniScript A → IP B → OmniScript A via embedded call |
| FlexCard data sources are typed | `dataSource.type === 'IntegrationProcedures'` (plural) in DataSourceConfig JSON |
| Active vs Draft matters | Only active components participate in runtime dependency chains |

---

## Workflow (4-Phase Pattern)

### Phase 1: Namespace Detection

Probe objects in order until a successful COUNT() returns:
```bash
sf data query --query "SELECT COUNT() FROM OmniProcess" --target-org myorg --json 2>/dev/null            # Core
sf data query --query "SELECT COUNT() FROM vlocity_cmt__OmniScript__c" --target-org myorg --json 2>/dev/null  # vlocity_cmt
sf data query --query "SELECT COUNT() FROM vlocity_ins__OmniScript__c" --target-org myorg --json 2>/dev/null  # vlocity_ins
```
If none succeed, OmniStudio is not installed.

### Phase 2: Component Discovery

Query each component type using the detected namespace:
```soql
-- OmniScripts (Core)
SELECT Id, Type, SubType, Language, IsActive, VersionNumber, PropertySetConfig FROM OmniProcess WHERE IsIntegrationProcedure = false ORDER BY Type, SubType, Language, VersionNumber DESC LIMIT 200
-- Integration Procedures (Core)
SELECT Id, Type, SubType, Language, IsActive, VersionNumber, PropertySetConfig FROM OmniProcess WHERE IsIntegrationProcedure = true ORDER BY Type, SubType, Language, VersionNumber DESC LIMIT 200
-- FlexCards (Core) — use DataSourceConfig, NOT Definition
SELECT Id, Name, IsActive, DataSourceConfig, PropertySetConfig FROM OmniUiCard ORDER BY Name LIMIT 200
-- Data Mappers (Core)
SELECT Id, Name, IsActive, Type FROM OmniDataTransform ORDER BY Name LIMIT 200
-- Data Mapper Items — FK is OmniDataTransformationId (full word)
SELECT Id, OmniDataTransformationId, InputObjectName, OutputObjectName FROM OmniDataTransformItem
```

### Phase 3: Dependency Analysis (BFS with circular detection)

Parse `PropertySetConfig` on each `OmniProcessElement` to extract dependencies:

| Element Type | JSON Path | Dependency Target |
|-------------|-----------|-------------------|
| DataRaptor Transform/Turbo Action | `bundle`, `bundleName` | Data Mapper (by name) |
| Remote Action | `remoteClass`, `remoteMethod` | Apex Class.Method |
| Integration Procedure Action | `integrationProcedureKey` | IP (Type_SubType) |
| OmniScript Action | `omniScriptKey` or `Type/SubType` | OmniScript (Type_SubType) |
| HTTP Action | `httpUrl`, `httpMethod` | External endpoint |

FlexCard data sources live in `DataSourceConfig` (type `IntegrationProcedures`, plural). Data Mapper object deps come from `InputObjectName`/`OutputObjectName`.

### Phase 4: Visualization & Reporting

Produce: Mermaid `graph LR` diagram (color-coded by component type), JSON summary (namespace + components + dependencies + impactAnalysis), and a human-readable report (inventory counts, edge count, circular refs, most-depended components).

---

## Gotchas

| Scenario | Handling |
|----------|---------|
| Mixed namespace org | Probe all three; report if multiple return results |
| Inactive components with dependencies | Include but mark inactive; warn if active depends on inactive |
| Large orgs (1000+ components) | SOQL pagination (LIMIT/OFFSET); batches of 200 |
| PropertySetConfig exceeds SOQL field length | Use Tooling/REST API to fetch full JSON |
| Circular dependency | Log cycle path (A → B → C → A); continue traversal |
| Version conflicts (multiple active) | Only highest active version participates at runtime |

---

## Notes

- `IsIntegrationProcedure` is the discriminator on `OmniProcess`. `DataSourceConfig` (not `Definition`) for FlexCards. FK to Data Mapper parent is `OmniDataTransformationId`.

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win.

### 1 — Namespace Is Known: Core/`omnistudio`, Metadata-Driven (skip probing)

The IBX org uses the **`omnistudio` managed package with Core-style metadata** — `OmniProcess` / `OmniUiCard` / `OmniDataTransform`, `IsIntegrationProcedure` boolean, `DataSourceConfig` field. It is **not** vlocity_cmt or vlocity_ins. You can skip the namespace-detection probe and assume Core/`omnistudio`.

### 2 — Graph-First (MANDATORY per project rules)

Before running org SOQL or parsing PropertySetConfig, use the **code-review-graph MCP** tools — they already model this repo's structure and are faster/cheaper:
- `semantic_search_nodes("<asset name>")` to locate a component
- `query_graph(pattern="callers_of"/"callees_of", node=...)` to trace dependents/dependencies
- `get_impact_radius("<component>")` for blast radius
- `get_affected_flows(...)` for impacted execution paths

Fall back to org queries / Grep only when the graph returns nothing or you need **runtime/active-version** truth from the org.

### 3 — Source-of-Truth Is the Repo Metadata

Dependencies can be analyzed **offline** from the committed SFDX source without an org:
- IPs: `force-app/main/default/omniIntegrationProcedures/*.oip-meta.xml` (1,483)
- DataRaptors: `force-app/main/default/omniDataTransforms/*.rpt-meta.xml` (1,409)
- OmniScripts: `force-app/main/default/omniScripts/*.os-meta.xml` (704)
- FlexCards: `force-app/main/default/omniUiCard/*.ouc-meta.xml` (37)
Prefer repo analysis for design-time impact; query the org only to confirm which version is **active**.

### 4 — Active-Version Filtering Is Essential Here

With up to ~100 versions per asset (e.g. `PRM_PractitionerParticipationForm_English_1..98`), naive name matching produces huge false graphs. Always reduce to `<isActive>true</isActive>` (or `IsActive=true` in the org) before reporting dependents/impact.

### 5 — Naming Map for Reference Resolution

When resolving references found in PropertySetConfig/DataSourceConfig to repo files:
- IP keys `PRM_<Name>_Procedure` → `omniIntegrationProcedures/PRM_<Name>_Procedure_<v>.oip-meta.xml`
- DataRaptor `bundle` names → `omniDataTransforms/<PRMDR…|PRM…|DR…>_<v>.rpt-meta.xml`
- `remoteClass` → `classes/PRM_*.cls` (often `implements Callable`; `remoteMethod` = the `methodName`)
- FlexCard IP data sources → active `PRM_*` IP

### 6 — Mermaid Output

Diagrams are welcome (the project encourages diagrams). Use the upstream color scheme; consider also using the `diagrams` skill for consistent rendering. Keep nodes to **active** versions only.

### 7 — IBX Analysis Checklist

- [ ] Used code-review-graph MCP first (semantic_search / query_graph / get_impact_radius)
- [ ] Reduced to **active** versions before reporting
- [ ] Resolved IP/DR/Apex/FlexCard references to repo file paths using the naming map
- [ ] Flagged circular references and broken/inactive references
- [ ] Produced Mermaid + impact summary scoped to active runtime chain
