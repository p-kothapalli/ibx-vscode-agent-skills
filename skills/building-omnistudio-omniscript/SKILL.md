---
name: building-omnistudio-omniscript
description: 'OmniStudio OmniScript creation and validation with 120-point scoring. Use when
  building guided digital experiences, multi-step forms, or interactive processes that orchestrate
  Integration Procedures and Data Mappers. TRIGGER when: user creates OmniScripts, designs
  step flows, configures element types, or reviews existing OmniScript configurations. DO
  NOT TRIGGER when: building FlexCards (use building-omnistudio-flexcard), creating Integration
  Procedures directly (use building-omnistudio-integration-procedure), or analyzing dependencies
  (use analyzing-omnistudio-dependencies).'
metadata:
  version: 1.0-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/building-omnistudio-omniscript
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
argument-hint: '[form or OmniScript name]'
---

# building-omnistudio-omniscript: OmniStudio OmniScript Creation and Validation

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/building-omnistudio-omniscript` if it does not auto-load.


Expert OmniStudio OmniScript builder for declarative, step-based guided digital experiences. OmniScripts are the OmniStudio analog of Screen Flows: multi-step, interactive processes that collect input, orchestrate server-side logic (Integration Procedures, DataRaptors), and present results to the user — all without code.

## Quick Reference

**Scoring**: 120 points across 6 categories. **Thresholds**: 90+ (Deploy) | 67-89 (Review) | <67 (Block - fix required)

---

## Scope

- **In scope**: Creating OmniScripts from requirements, element selection and PropertySetConfig design, dependency analysis (Integration Procedures, DataRaptors), data flow tracing, 120-point validation scoring, deployment and activation
- **Out of scope**: Building FlexCards (use `building-omnistudio-flexcard`), creating Integration Procedures directly (use `building-omnistudio-integration-procedure`), mapping full dependency trees (use `analyzing-omnistudio-dependencies`), deploying metadata to org (use `deploying-metadata`)

---

## Required Inputs

| Input | Description | Default |
|-------|-------------|---------|
| **Type** | Process category (e.g., `ServiceRequest`, `Enrollment`) | None — required |
| **SubType** | Specific variation (e.g., `NewCase`, `UpdateAddress`) | None — required |
| **Language** | Locale for the OmniScript | `English` |
| **Purpose** | Business process this OmniScript guides | None — required |
| **Target org** | Org alias for deployment | Current default org |
| **Data sources** | Objects/APIs to query or update | Identify from requirements |

---

## CRITICAL: Orchestration Order

**analyzing-omnistudio-dependencies → building-omnistudio-datamapper → building-omnistudio-integration-procedure → building-omnistudio-omniscript → building-omnistudio-flexcard** (you are here: building-omnistudio-omniscript)

OmniScripts consume Integration Procedures and DataRaptors. Build those FIRST. FlexCards may launch OmniScripts — build FlexCards AFTER. Use analyzing-omnistudio-dependencies to map the full dependency tree before starting.

---

## Key Insights

| Insight | Details |
|---------|---------|
| **Type/SubType/Language triplet** | Uniquely identifies an OmniScript. All three are required and form the composite key. |
| **PropertySetConfig** | JSON blob containing all element configuration — layout, data binding, validation, conditional visibility. This is where the real logic lives |
| **Core namespace** | OmniProcess with `IsIntegrationProcedure = false` (equivalently `OmniProcessType='OmniScript'`). Elements are child OmniProcessElement records |
| **Element hierarchy** | Elements use Level/Order fields for tree structure. Level 0 = Steps, Level 1+ = elements within steps |
| **Version management** | Multiple versions can exist; only one can be active per Type/SubType/Language triplet. Activate via `IsActive` |
| **Data JSON** | OmniScripts pass a single JSON data structure through all steps. Elements read/write this shared JSON via merge field syntax |

---

## Workflow Design (5-Phase Pattern)

### Phase 1: Requirements Gathering

**Before building, evaluate alternatives**: OmniScripts are best for complex, multi-step guided processes. For simple single-screen data entry, consider Screen Flows. For data display without interaction, consider FlexCards.

**Ask the user**: Type, SubType, Language, Purpose, Target org, Data sources.

**Then**: Check existing OmniScripts to avoid duplication, identify reusable IPs/DataRaptors, and map the dependency chain.

### Phase 2: Design & Element Selection

Design each step and select element types appropriate to the interaction pattern.

**Container Elements**: Step, Conditional Block, Loop Block, Edit Block.
**Input Elements**: Text, Text Area, Number, Date, Date/Time, Checkbox, Radio, Select, Multi-select, Type Ahead, Signature, File, Currency, Email, Telephone, URL, Password, Range, Time.
**Display Elements**: Text Block, Headline, Aggregate, Disclosure, Image, Chart.
**Action Elements**: DataRaptor Extract Action, DataRaptor Load Action, Integration Procedure Action, Remote Action, Navigate Action, DocuSign Envelope Action, Email Action.
**Logic Elements**: Set Values, Validation, Formula, Submit Action.

(See `references/element-types.md` upstream for per-element PropertySetConfig keys.)

### Phase 3: Generation & Validation

**Build the OmniScript**:
1. Create the OmniProcess record with Type, SubType, Language, and OmniProcessType='OmniScript'
2. Create OmniProcessElement child records for each Step (Level=0)
3. Create OmniProcessElement child records for each element within Steps (Level=1+, ordered by Order)
4. Configure PropertySetConfig JSON for each element
5. Wire action elements to their Integration Procedures / DataRaptors

**Validation (STRICT MODE)**:
- **BLOCK**: Missing Type/SubType/Language, circular OmniScript embedding, broken IP/DataRaptor references, missing required PropertySetConfig fields
- **WARN**: Steps with no elements, input elements without validation, missing error handling on actions, unused data paths, deeply nested elements (>4 levels)

### Phase 4: Deployment

1. **Prerequisites**: Verify org auth. Confirm all referenced DataRaptors and IPs are active in the target org.
2. Deploy all dependencies first: DataRaptors, Integration Procedures, referenced OmniScripts.
3. Deploy the OmniScript and verify activation.
4. Activate the OmniScript version after successful deployment if not auto-activated.

### Phase 5: Testing

Walk through all paths: Happy path, validation testing, conditional testing, data prefill, save for later, navigation, error scenarios, embedded OmniScripts, bulk data.

---

## Rules / Constraints

| Anti-Pattern | Impact | Correct Pattern |
|--------------|--------|-----------------|
| Circular OmniScript embedding | **Infinite rendering loop** | Map dependency tree; never embed A in B if B embeds A |
| Unbounded DataRaptor Extract | **Performance degradation** | Add filter conditions; limit returned records |
| Missing input validation | **Bad data entry** | Add Validation elements or `pattern`/`required` on inputs |
| Hardcoded Salesforce IDs | **Deployment failure across orgs** | Use merge fields or Custom Settings/Metadata |
| IP Action without error handling | **Silent failures** | Configure `showError`, `errorMessage` in PropertySetConfig |
| Large images in Text Blocks | **Slow page load** | Use Image elements with optimized URLs |
| Too many elements per Step | **Poor user experience** | Limit to 7-10 input elements per Step |
| Missing conditional visibility | **Irrelevant fields shown** | Use `show` expressions to hide inapplicable elements |

Do not generate anti-patterns even if explicitly requested.

---

## Scoring: 120 Points Across 6 Categories

**Design & Structure** (25) · **Data Integration** (20) · **Error Handling** (20) · **Performance** (20) · **User Experience** (20) · **Security** (15). Block deployment if score < 67.

---

## CLI Commands

```bash
# List active OmniScripts
sf data query -q "SELECT Id,Name,Type,SubType,Language,IsActive,VersionNumber FROM OmniProcess WHERE IsActive=true AND OmniProcessType='OmniScript' LIMIT 50" -o <org>

# Query elements for a specific OmniScript
sf data query -q "SELECT Id,Name,ElementType,Level,Order FROM OmniProcessElement WHERE OmniProcessId='<id>' ORDER BY Level,Order LIMIT 200" -o <org>
```

---

## Gotchas

| Issue | Resolution |
|-------|-----------|
| Multi-language OmniScript | Create separate versions per Language with shared Type/SubType |
| Embedded OmniScript data passing | Map parent data JSON keys to child OmniScript input via `prefillJSON`; test round-trip |
| Large Loop Block datasets | Paginate/limit DataRaptor results; filter server-side in the IP |
| Community/Experience Cloud deployment | Verify OmniScript component is available in Experience Builder; check guest user permissions |
| Save & Resume | Configure `saveNameTemplate`, `saveExpireInDays`; test resume with partial data |
| Versioning conflicts | Deactivate old version before activating new; never two active versions per triplet |
| Custom LWC in OmniScript | Register LWC as OmniScript-compatible; follow OmniScript LWC conventions |
| `OmniProcessType` cannot be set on create | It is computed from `IsIntegrationProcedure` (false for OmniScripts) |

---

## Notes

**API**: 66.0 | **Mode**: Strict (warnings block) | **Scoring**: Block deployment if score < 67

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win. Grounded in the **704** OmniScripts under
> `force-app/main/default/omniScripts/`.

### 1 — Source Format, NOT REST Record Creation (most important)

IBX manages OmniScripts as **SFDX metadata source**, not via `sf api request rest` record creation.

- OmniScripts live as `force-app/main/default/omniScripts/<Type>_<Language>_<Version>.os-meta.xml`.
- Edit the source (or author in OmniStudio Designer and retrieve), then deploy via the Metadata API:

```bash
sf project retrieve start -m OmniScript:PRM_PractitionerParticipationForm_English_98 -o qa-sandbox
sf project deploy start  -m OmniScript:PRM_PractitionerParticipationForm_English_98 -o qa-sandbox --wait 10
```

- For cross-org migration, IBX also uses **Vlocity Build datapacks** (`export-omnistudio.yaml`) — see `deploying-omnistudio-datapacks`.

### 2 — Namespace = `omnistudio` Managed Package

- Metadata type is the Core-style `OmniScript` (not `vlocity_cmt__OmniScript__c`). `sfdx-project.json` namespace is empty; custom assets are not namespace-prefixed.

### 3 — Naming Convention (verified)

OmniScripts follow `PRM_<FormName>_<Language>_<Version>`:
- `PRM_PractitionerParticipationForm_English_98`
- `PRM_AttestationFlow_English_19`
- `PRM_AncillaryProviderForm_English_42`
- `PRM_PDMManualChanges_English_14`

Rules: `PRM_` prefix mandatory; Type = `PRM_<PascalCaseFormName>`; Language usually `English`; trailing integer is the **version**. Major forms: Practitioner Participation, Provider Change, PDM Manual, Off-Cycle, Ancillary Provider, RecredQC, PNC/PNCReview.

### 4 — Active-Version Rule (critical)

Forms have **many** versions (e.g., `PRM_PractitionerParticipationForm_English_96/97/98`). Only `<isActive>true</isActive>` is live.

- **Always ground edits against the active version** — identify it before editing. With ~100 versions on some forms, editing the wrong one is the most common mistake.
- Activating a new version deactivates the prior one (one active per Type/SubType/Language).

### 5 — Custom LWC Overrides Are the Norm

Many IBX OmniScripts embed **custom OmniScript LWCs** (`prm*`, `runtimeNamespace=omnistudio`) that extend `OmniscriptBaseMixin`. When a step uses a custom LWC element, coordinate changes with the `generating-lwc-components` skill (OmniScript LWC section) — e.g. `prmSetValueNext`, `prmReviewScreen*Template`, `prmTextElemOveride*`.

### 6 — Graph-First Dependency Checks

Before tracing which IPs/DataRaptors/LWCs an OmniScript uses (or which FlexCards launch it), use the **code-review-graph MCP** tools first; fall back to `analyzing-omnistudio-dependencies` / Glob only if the graph returns nothing.

### 7 — IBX Review Checklist

- [ ] Asset edited as `.os-meta.xml` source and deployed with `sf project deploy start -m OmniScript:` (no REST record creation)
- [ ] `PRM_<Form>_<Language>_<Version>` naming
- [ ] Change targets the **active** version (verified — beware high version counts)
- [ ] Referenced IPs / DataRaptors / custom LWCs exist and are active (graph-checked)
- [ ] Action elements have `showError`/`errorMessage`; no hardcoded Salesforce IDs
- [ ] Extracts bounded; ≤7-10 inputs per Step; conditional visibility used
- [ ] Custom LWC element changes coordinated with `generating-lwc-components`
