---
name: generating-flexipage
description: Use this skill when users need to create, generate, modify, or validate Salesforce
  Lightning pages (FlexiPages). Trigger when users mention RecordPage, AppPage, HomePage,
  Lightning pages, adding components to pages, or page customization, or work with *.flexipage-meta.xml
  files and need help with components, regions, or deployment errors.
metadata:
  version: 1.0-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/generating-flexipage
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
---

# generating-flexipage

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/generating-flexipage` if it does not auto-load.


Generate Lightning pages (RecordPage, AppPage, HomePage) via CLI bootstrapping, then deploy.

## Workflow

1. **Bootstrap NEW pages with the CLI** (mandatory — never hand-author from scratch):
```bash
sf template generate flexipage --name <PageName> --template <RecordPage|AppPage|HomePage> \
  --sobject <SObject> --primary-field <F1> --secondary-fields <F2,F3> \
  --detail-fields <...> --output-dir force-app/main/default/flexipages
```
If it fails: `sf plugins install templates`, retry. Validate fields exist first; prefer compound fields (`Name`, `BillingAddress`); include required fields in `--detail-fields`.

2. **Dry-run deploy** to validate:
```bash
sf project deploy start --dry-run -d "force-app/main/default" --test-level NoTestRun --wait 10 --json
```

## Critical XML Rules

- **Property value encoding** (in order): `&`→`&amp;`, then `<`,`>`,`"`,`'`. (Most common error.)
- **Field references** always `Record.{FieldApiName}`, never `Object.Field`.
- **Region vs Facet**: template region names → `Region`; component slots → `Facet`.
- **fieldInstance**: each in its own `itemInstances`, with `fieldInstanceProperties`/`uiBehavior`.
- **Unique identifiers/region names** across the whole file; combine multiple components in ONE region rather than duplicating a name.
- No `__c` suffix in page names; no `mode` tags on standard regions.

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win.

### 1 — FlexiPages Frequently Host OmniStudio

IBX has ~100 FlexiPages and OmniStudio is the dominant UI surface. Record/App pages commonly embed **FlexCards** (`PRM<Card>_IBX_<v>`, type `OmniUiCard`) and **OmniScripts** (`PRM_<Form>_English_<v>`) as components, plus custom **`prm*` LWCs**. When adding these:
- Reference the **active version** of the OmniStudio asset (active-version rule) — see `building-omnistudio-flexcard` / `building-omnistudio-omniscript`.
- Confirm the LWC is `isExposed=true` and FlexCard/OmniScript targets allow Lightning page placement.

### 2 — Naming & Domain

New pages target IBX provider-credentialing objects (`PRM_*__c`, `Account`, `Contact`). Use clear, domain-aligned `masterLabel`s; no `__c` in the page API name. Read a sibling FlexiPage in `force-app/main/default/flexipages/` first to match the project's component/region conventions.

### 3 — Validate Fields/Components via Graph or Describe

Before referencing fields or `prm*`/`PRM*` components, confirm they exist using **`code-review-graph` MCP** (`semantic_search_nodes`) or `sf sobject describe` — IBX's large schema makes typo'd `Record.<Field>` a common deploy failure.

### 4 — Activation Is via App/Profile/PS Assignment

The FlexiPage XML defines the page; assignment to apps/record types is separate metadata. Coordinate visibility with the relevant **`PRM_*` permission set / app** (see `generating-permission-set`) rather than assuming org-default activation.

### 5 — Deploy

```bash
sf project deploy start \
  --source-dir force-app/main/default/flexipages/<PageName>.flexipage-meta.xml \
  --target-org qa-sandbox --wait 10
```
Default alias `qa-sandbox`. For OmniStudio-hosting pages, ensure the referenced IP/DataRaptor/FlexCard/OmniScript are already deployed (dependency order in `deploying-metadata`).
