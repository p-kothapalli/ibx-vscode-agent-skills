---
name: deploying-omnistudio-datapacks
description: 'Salesforce Industries DataPack deployment automation using Vlocity Build. TRIGGER
  when: user deploys or validates OmniStudio/Vlocity DataPacks with vlocity commands (packDeploy/packRetry/packExport/packGetDiffs),
  sets up DataPack CI/CD pipelines, or troubleshoots DataPack migration errors. DO NOT TRIGGER
  when: deploying Salesforce metadata with sf project deploy (use deploying-metadata), authoring
  OmniStudio artifacts (use building-omnistudio-*), or writing Apex/LWC business logic (use
  generating-apex/generating-lwc-components).'
metadata:
  version: 1.0-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/deploying-omnistudio-datapacks
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
---

# deploying-omnistudio-datapacks: Vlocity Build DataPack Deployment

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/deploying-omnistudio-datapacks` if it does not auto-load.


Use this skill when the user needs **Vlocity DataPack deployment orchestration**: export/deploy workflow, manifest-driven deploys, failure triage, and CI/CD sequencing for OmniStudio/Industries DataPacks.

---

## Scope

Use `deploying-omnistudio-datapacks` when work involves:
- `vlocity packDeploy`, `packRetry`, `packContinue`, `packExport`, `packGetDiffs`, `validateLocalData`
- DataPack job-file design (`projectPath`, `expansionPath`, `manifest`, `queries`)
- org-to-org DataPack migration and retry loops
- troubleshooting DataPack dependency, matching-key, and GlobalKey issues

Delegate elsewhere when the user is:
- deploying standard metadata with `sf project deploy` -> [deploying-metadata](../deploying-metadata/SKILL.md)
- building OmniScripts, FlexCards, IPs, or Data Mappers -> `building-omnistudio-*`
- writing Apex/LWC code -> `generating-apex`, `generating-lwc-components`

---

## Critical Operating Rules

- Use **Vlocity Build (`vlocity`)** commands for DataPacks, not `sf project deploy`.
- Prefer Salesforce CLI auth integration (`-sfdx.username `) over username/password files when available.
- Always run a **pre-deploy quality gate** before full deploy:
  1. `validateLocalData`
  2. optional `packGetDiffs`
  3. then `packDeploy`
- Use `packRetry` repeatedly when error counts are dropping; stop when retries no longer improve results.
- Keep matching-key strategy and GlobalKey integrity consistent across source and target orgs.

---

## Required Context to Gather First

- source org and target org aliases
- job file path and DataPack project path
- deployment scope (full project, manifest subset, or specific `-key`)
- whether this is export, deploy, retry, continue, or diff-only
- namespace model (`%vlocity_namespace%`, `vlocity_cmt`, or core)
- known constraints (new sandbox bootstrap, trigger behavior, matching key customizations)

Preflight:
```bash
vlocity help
sf org list
sf org display --target-org <alias> --json
test -f <job-file>.yaml
```

---

## Recommended Workflow

```bash
# 1. Ensure tool readiness
npm install --global vlocity && vlocity help

# 2. Validate project data locally
vlocity -sfdx.username <source-alias> -job <job-file>.yaml validateLocalData

# 3. Export from source (when needed)
vlocity -sfdx.username <source-alias> -job <job-file>.yaml packExport
vlocity -sfdx.username <source-alias> -job <job-file>.yaml packRetry

# 4. Deploy to target
vlocity -sfdx.username <target-alias> -job <job-file>.yaml packDeploy
vlocity -sfdx.username <target-alias> -job <job-file>.yaml packRetry

# 5. Continue interrupted jobs
vlocity -sfdx.username <target-alias> -job <job-file>.yaml packContinue

# 6. Verify post-deploy parity
vlocity -sfdx.username <target-alias> -job <job-file>.yaml packGetDiffs
```

---

## Gotchas

| Error / symptom | Likely cause | Default fix direction |
|---|---|---|
| `No match found for ...` | missing dependency in target org | include missing DataPack key and redeploy |
| `Duplicate Results found for ... GlobalKey` | duplicate records in target | clean duplicates and re-run deploy |
| `Multiple Imported Records ... same Salesforce Record` | source duplicate matching-key records | remove duplicates in source and re-export |
| `No Configuration Found` | outdated DataPack settings | run `packUpdateSettings` or enable `autoUpdateSettings` |
| `Some records were not processed` | settings mismatch / partial dependency state | refresh settings both orgs, then retry |
| SASS / template compile failures | missing referenced UI template assets | export/deploy referenced template dependencies first |

---

## CI/CD Guidance

Default pipeline: authenticate orgs → `validateLocalData` → export changed scope → `packDeploy` → `packRetry` loop until stable → `packGetDiffs` and publish report. For incremental deploys: `gitCheck: true`, `gitCheckKey`, and `manifest` for deterministic scope.

---

## Output Expectations

```text
DataPack goal: <export / deploy / retry / diff / ci-cd>
Source org: <alias or N/A>
Target org: <alias or N/A>
Scope: <job file + manifest/key/full>
Result: <passed / failed / partial>
Key findings: <errors, dependencies, retries, diffs>
Next step: <safe follow-up action>
```

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win.

### 1 — When to Use DataPacks vs `sf project deploy` (decision rule)

IBX commits OmniStudio as **SFDX metadata source** (`.os-meta.xml`, `.oip-meta.xml`, `.rpt-meta.xml`, `.ouc-meta.xml`) and the **default deploy path is the Metadata API** (`sf project deploy start -m OmniScript:/OmniIntegrationProcedure:/OmniDataTransform:/OmniUiCard:` — see `deploying-metadata`).

Use **Vlocity DataPacks only** for:
- **Cross-org migration** (e.g., dev → QA → staging) where matching keys / GlobalKeys must be reconciled and the Metadata API path is insufficient.
- **Bulk export/refresh** of OmniStudio assets into the repo from an org.

For day-to-day single-asset edits, prefer `deploying-metadata`, not DataPacks.

### 2 — The IBX Job File (verified)

The repo's Vlocity job file is `export-omnistudio.yaml` at the project root:

```yaml
projectPath: ./vlocity_export
queries:
  - OmniScript
  - IntegrationProcedure
  - DataRaptor
  - FlexCard
```

- `projectPath: ./vlocity_export` is the DataPack expansion directory (distinct from `force-app` SFDX source). Vlocity logs land in `vlocity-temp/logs/` and `VlocityBuildLog.yaml`.
- The `queries` list scopes export to the four OmniStudio types IBX uses. Extend this list (or add a `manifest:`) to scope a targeted export/deploy.

### 3 — Namespace = `omnistudio` (Core)

Use the core/`omnistudio` namespace model in job files (not `vlocity_cmt`/`vlocity_ins`). `%vlocity_namespace%` resolves to the installed `omnistudio` package.

### 4 — Auth via Existing Aliases

Use the project's authenticated CLI aliases (e.g., `qa-sandbox`) with `-sfdx.username`:

```bash
# Export OmniStudio assets from QA into ./vlocity_export
vlocity -sfdx.username qa-sandbox -job export-omnistudio.yaml packExport

# Deploy the exported DataPacks to a target org
vlocity -sfdx.username <target-alias> -job export-omnistudio.yaml packDeploy
vlocity -sfdx.username <target-alias> -job export-omnistudio.yaml packRetry
```

Never put credentials in the repo; rely on `sf` CLI auth. (`vlocity_export/` and logs are build artifacts — keep them out of committed source where possible.)

### 5 — Keep Repo Source as the Source of Truth

After a DataPack **export**, reconcile changes back into the committed `force-app` SFDX source so the repo metadata (`.oip-meta.xml`, etc.) stays authoritative. Do not let `vlocity_export/` silently diverge from `force-app/main/default/omni*`.

### 6 — IBX Datapack Checklist

- [ ] Confirmed DataPacks are the right tool (cross-org migration / bulk export) — else use `deploying-metadata`
- [ ] Used `export-omnistudio.yaml` (extend `queries`/`manifest` to scope)
- [ ] Auth via `-sfdx.username <alias>` (e.g., `qa-sandbox`); no credentials in repo
- [ ] `validateLocalData` → `packExport`/`packDeploy` → `packRetry` until stable → `packGetDiffs`
- [ ] Reconciled exported assets back into `force-app` SFDX source
- [ ] Verified **active** versions post-deploy
