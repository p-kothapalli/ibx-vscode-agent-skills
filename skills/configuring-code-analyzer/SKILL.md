---
name: configuring-code-analyzer
description: 'Set up, configure, and troubleshoot Salesforce Code Analyzer for any project.
  Handles installation, prerequisite checks, diagnosing broken setups, creating and editing
  code-analyzer.yml overrides, engine-specific settings, ignore patterns, severity overrides,
  and CI/CD pipeline setup. TRIGGER when: user says ''set up code analyzer'', ''configure
  code analyzer'', ''install code analyzer'', ''code analyzer not working'', ''scan is failing'',
  ''enable/disable engine'', ''exclude files'', ''change severity'', ''set up CI/CD'', ''quality
  gate'', ''code-analyzer.yml''. DO NOT TRIGGER when: user wants to run a scan (use running-code-analyzer).'
metadata:
  version: 1.0-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/configuring-code-analyzer
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
---

# Configuring Code Analyzer

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/configuring-code-analyzer` if it does not auto-load.


Manage the `code-analyzer.yml` configuration file — the single source of truth for how Code Analyzer behaves in a project. All customization (engines, rules, ignores, suppressions) is done by creating/editing this file.

## Core Principle: YAML Only When Customizing

Code Analyzer works out of the box with NO config file. Create `code-analyzer.yml` **only** when the user requests a customization; place it at **project root** (where `sfdx-project.json` lives); write **only overrides**, never duplicate defaults. The CLI auto-discovers it from CWD — no `--config-file` needed.

## `code-analyzer.yml` Structure

```yaml
config_root: .
log_folder: <path>
log_level: <1-5>
ignores:
  files: [<glob patterns>]
engines:
  <engine_name>:
    disable_engine: <bool>
    <engine_specific_keys>: ...
rules:
  <engine_name>:
    <rule_name>:
      severity: <1-5>
      tags: [<strings>]
      disabled: <bool>
suppressions:
  "<file_or_folder_path>":
    - rule_selector: "<selector>"
      reason: "<why>"
```

## Prerequisites

```bash
sf --version
sf plugins --core | grep -i code-analyzer
java -version          # Java 11+ (PMD, CPD, SFGE)
node --version         # Node 18+ (ESLint, RetireJS)
python3 --version      # Python 3 (Flow)
```
Install (ask first): `sf plugins install @salesforce/plugin-code-analyzer`.

## Common Requests → Config

| User says | YAML |
|-----------|------|
| "ignore test files" | `ignores: files: ["**/__tests__/**","**/*.test.js"]` |
| "only Apex, no JS" | `engines: eslint: disable_engine: true` + `retire-js: disable_engine: true` |
| "make CRUD critical" | `rules: pmd: ApexCRUDViolation: severity: 1` |
| "increase SFGE memory" | `engines: sfge: java_max_heap_size: "8g"` |
| "use my ESLint config" | `engines: eslint: auto_discover_eslint_config: true` |

⚠️ Resolve fuzzy rule names to exact names (`sf code-analyzer rules --rule-selector all | grep -i <kw>`) BEFORE writing YAML — a misspelled rule is silently ignored. Validate after every change with `sf code-analyzer config`.

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win.

### 1 — Recommended IBX Baseline `code-analyzer.yml`

When the user first asks to configure the analyzer for IBX, propose this minimal root config (it only excludes generated/managed/vendor artifacts — no default duplication):

```yaml
ignores:
  files:
    - "**/node_modules/**"
    - "**/.sfdx/**"
    - "**/.sf/**"
    - "vlocity_export/**"          # Vlocity DataPack export staging
    - "metadata-export/**"         # non-source-tracking retrieval dumps
    - "**/staticresources/**"
    - "**/*.min.js"
    - "**/__tests__/**"            # LWC Jest specs (lint via npm run lint instead)
```
SFGE heap: IBX has 1,200+ Apex classes, so use `"6g"` or `"8g"`:
```yaml
engines:
  sfge:
    java_max_heap_size: "8g"
```

### 2 — Do NOT Scan OmniStudio Metadata as Source

OmniStudio assets (`*.oip-meta.xml`, `*.rpt-meta.xml`, `*.os-meta.xml`, `*.ouc-meta.xml`) and the `omnistudio` managed package are **not** lint targets. Keep the analyzer focused on `PRM_*` Apex/LWC. If they generate noise, add their folders to `ignores.files` with a documented reason.

### 3 — Severity Should Reinforce IBX Security Conventions

Promote FLS/CRUD/security rules (e.g. `ApexCRUDViolation`) rather than demote them — IBX requires `WITH USER_MODE` / `AccessLevel.USER_MODE` / `with sharing` (see `generating-apex`). Use `suppressions` (with a `reason`) only for legacy `PRM_*` classes that can't yet be remediated; never blanket-disable security rules.

### 4 — Place the File Where IBX Runs Scans

Project root is `/Users/.../IBXQA/IBXQA` (where `sfdx-project.json`, API 66.0, empty namespace live). The file must sit there so `running-code-analyzer` picks it up.

### 5 — CI/CD Gate

If/when a pipeline is added, use `--severity-threshold 2` as the quality gate and emit SARIF (`--output-file results.sarif`) for code scanning. Keep this consistent with the repo deploy scripts (`TEST_DEPLOYMENT_COMMANDS.sh`) and `--test-level RunLocalTests`.

### 6 — Hand-off

After config succeeds, hand back to **`running-code-analyzer`** to actually scan.
