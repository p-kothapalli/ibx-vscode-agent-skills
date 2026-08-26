---
name: deploying-metadata
description: 'Salesforce DevOps automation using sf CLI v2. TRIGGER when: user deploys metadata,
  creates/manages scratch orgs or sandboxes, sets up CI/CD pipelines, or troubleshoots deployment
  errors with sf project deploy. DO NOT TRIGGER when: writing Apex code (use generating-apex),
  building LWC components (use generating-lwc-components), creating metadata definitions (use
  generating-custom-object or generating-custom-field), or querying org data (use handling-sf-data).'
metadata:
  version: 1.1-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/deploying-metadata
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
argument-hint: '[metadata type or source path]'
---

# deploying-metadata: Comprehensive Salesforce DevOps Automation

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/deploying-metadata` if it does not auto-load.


Use this skill when the user needs **deployment orchestration**: dry-run validation, targeted or manifest-based deploys, CI/CD workflow advice, scratch-org management, failure triage, or safe rollout sequencing for Salesforce metadata.

## When This Skill Owns the Task

Use `deploying-metadata` when the work involves:
- `sf project deploy start`, `quick`, `report`, or retrieval workflows
- release sequencing across objects, permission sets, Apex, and Flows
- CI/CD gates, test-level selection, or deployment reports
- troubleshooting deployment failures and dependency ordering

Delegate elsewhere when the user is authoring Apex (`generating-apex`), LWC (`generating-lwc-components`), custom objects/fields, Flows, or doing org data operations.

---

## Critical Operating Rules

- Use **`sf` CLI v2 only**.
- On non-source-tracking orgs, deploy/retrieve commands require an explicit scope such as `--source-dir`, `--metadata`, or `--manifest`.
- Prefer **`--dry-run` first** before real deploys.
- For Flows, deploy safely and activate only after validation.

### Default deployment order
| Phase | Metadata |
|---|---|
| 1 | Custom objects / fields |
| 2 | Permission sets |
| 3 | Apex |
| 4 | Flows as Draft |
| 5 | Flow activation / post-verify |

This ordering prevents many dependency and FLS failures.

---

## Required Context to Gather First

- target org alias and environment type
- deployment scope: source-dir, metadata list, or manifest
- whether this is validate-only, deploy, quick deploy, retrieve, or CI/CD guidance
- required test level and rollback expectations
- whether special metadata types are involved (Flow, permission sets, agents, packages)

Preflight:
```bash
sf --version
sf org list
sf org display --target-org <alias> --json
test -f sfdx-project.json
```

---

## Recommended Workflow

```bash
# 1. Validate first (dry-run)
sf project deploy start --dry-run --source-dir force-app --target-org <alias> --wait 30 --json

# 2. Deploy the smallest correct scope
sf project deploy start --source-dir force-app --target-org <alias> --wait 30 --json
sf project deploy start --manifest manifest/package.xml --target-org <alias> --test-level RunLocalTests --wait 30 --json

# 3. Quick deploy after successful validation
sf project deploy quick --job-id <validation-job-id> --target-org <alias> --json

# 4. Verify
sf project deploy report --job-id <job-id> --target-org <alias> --json
```

---

## High-Signal Failure Patterns

| Error / symptom | Likely cause | Default fix direction |
|---|---|---|
| `FIELD_CUSTOM_VALIDATION_EXCEPTION` | validation rule or bad test data | adjust data or rule timing |
| `INVALID_CROSS_REFERENCE_KEY` | missing dependency | include referenced metadata first |
| `CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY` | trigger / Flow / validation side effect | inspect automation stack |
| tests fail during deploy | broken code or fragile tests | run targeted tests, fix root cause, revalidate |
| field/object not found in permset | wrong order | deploy objects/fields before permission sets |
| Flow invalid / version conflict | dependency or activation problem | deploy as Draft, verify, then activate |

---

## CI/CD Guidance

Default pipeline: authenticate → validate repo/org state → static analysis → dry-run deploy → tests + coverage gates → deploy → verify + notify. Static analysis uses **Code Analyzer v5** (`sf code-analyzer`), not retired `sf scanner`.

---

## Completion Format

```text
Deployment goal: <validate / deploy / retrieve / pipeline>
Target org: <alias>
Scope: <source-dir / metadata / manifest>
Result: <passed / failed / partial>
Key findings: <errors, ordering, tests, skipped items>
Next step: <safe follow-up action>
```

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win.

### 1 — Default Org Alias & Scripts (verified)

- The default target org alias is **`qa-sandbox`** (used by `TEST_DEPLOYMENT_COMMANDS.sh`, `ORG_ALIAS="qa-sandbox"`).
- Prefer the repo's **wrapper scripts** for routine work — they bundle preflight checks, deploy, test, and verify:
  - `./TEST_DEPLOYMENT_COMMANDS.sh` — guided deploy (validation → deploy → tests → verify) for the Address & Group Manager component set.
  - `./RETRIEVE_COMPONENTS_FROM_QA.sh` — guided retrieval (ALL / Apex / LWC / OmniStudio / Phase 5 scopes).
  - `./remove.sh qa-sandbox` — remove components after testing.
- Always `sf org display --target-org qa-sandbox` first to confirm auth.

### 2 — Source API Version & Namespace

- `sfdx-project.json`: default package `force-app`, **`sourceApiVersion: 66.0`**, **empty namespace** (unmanaged custom assets; `PRM` prefix, not namespace prefixes).

### 3 — Non-Source-Tracking Orgs (common here)

Production and some sandboxes lack source tracking. Always scope explicitly:
```bash
sf project deploy start -m ApexClass -m LightningComponentBundle --target-org qa-sandbox
sf project retrieve start -x manifest/package.xml --target-org qa-sandbox
```
Check tracking via `sf org display`. The full manifest lives at `manifest/package.xml`; `.forceignore` controls exclusions.

### 4 — OmniStudio Metadata Deploys (project-specific)

OmniStudio assets are SFDX source and deploy via the Metadata API (NOT REST record creation, NOT DataPacks for single edits):
```bash
sf project deploy start -m OmniScript:PRM_<Form>_English_<v> -o qa-sandbox --wait 10
sf project deploy start -m OmniIntegrationProcedure:PRM_<Name>_Procedure_<v> -o qa-sandbox --wait 10
sf project deploy start -m OmniDataTransform:<Name>_<v> -o qa-sandbox --wait 10
sf project deploy start -m OmniUiCard:<Name>_<SubType>_<v> -o qa-sandbox --wait 10
```
For cross-org migration of OmniStudio, use **Vlocity DataPacks** instead — see `deploying-omnistudio-datapacks`. After deploy, confirm the intended **version is active** (only one active version per asset).

### 5 — Test Level & Coverage

- Default to **`--test-level RunLocalTests`** for Apex-bearing deploys to QA (the org has many managed-package tests; RunLocalTests avoids them).
- IBX test classes are `PRM_*Test`; project coverage target is **≥ 85%** (see `generating-apex-test`). Use `PRM_TestDataFactory` for data.

### 6 — Trigger Deployment Safety

Triggers carry the `PRM_TriggerBypassPermission` guard. When deploying trigger changes, verify the bypass permission/automation behavior in the target org (see `generating-apex` IBX overrides) before activating dependent automation.

### 7 — Repo Note (IBXEnhancements)

In the `IBXEnhancements` skills repo, `scripts/` and `force-app/main/default/` are **git-ignored** (kept local). Do not assume metadata source is pushed there — deploys run from the local `force-app` working tree against `qa-sandbox`.

### 8 — Default deployment order (IBX-extended)

| Phase | Metadata |
|---|---|
| 1 | Custom objects / fields |
| 2 | Permission sets (incl. `PRM_CredentialingUser`) |
| 3 | Apex (classes + triggers) |
| 4 | OmniStudio Data Mappers → IPs → OmniScripts → FlexCards (dependency order) |
| 5 | LWC / Aura / FlexiPages |
| 6 | Flow activation / post-verify + activate intended OmniStudio versions |

### 9 — IBX Deploy Checklist

- [ ] `sf org display --target-org qa-sandbox` confirms auth
- [ ] Used wrapper script (`TEST_DEPLOYMENT_COMMANDS.sh`) or scoped `sf project deploy start`
- [ ] `--dry-run` validated before real deploy
- [ ] Explicit scope on non-source-tracking orgs (`-m`/`-x`/`--source-dir`)
- [ ] `--test-level RunLocalTests`; `PRM_*Test` pass; coverage ≥ 85%
- [ ] OmniStudio deployed in dependency order; **active version** confirmed post-deploy
- [ ] Code Analyzer v5 (`sf code-analyzer`) clean on changed Apex/LWC
