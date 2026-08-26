---
name: running-code-analyzer
description: 'Run Salesforce Code Analyzer to scan code for security, performance, best practice,
  and code style violations. Supports all engines (PMD, ESLint, CPD, RetireJS, Flow, SFGE,
  ApexGuru), targets (files, folders, git diff), categories, and severities. Also handles
  post-scan exploration: filtering results by engine/severity/category/file, and explaining
  rules. TRIGGER when: user says ''scan my code'', ''check for security issues'', ''run PMD/ESLint'',
  ''find duplicates'', ''analyze Flows'', ''static analysis'', ''code quality'', ''show only
  security violations'', ''what is this rule''. DO NOT TRIGGER when: user wants to fix code
  without scanning, or asks ONLY about installation/configuration (use configuring-code-analyzer).'
metadata:
  version: 1.0-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/running-code-analyzer
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
argument-hint: '[path under force-app/]'
---

# Running Code Analyzer

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/running-code-analyzer` if it does not auto-load.


Translate natural-language requests ("scan for security issues", "check my changes") into the correct `sf code-analyzer run` command, execute scans, and present actionable results.

## Command Syntax Rules (ABSOLUTE)

1. Command is **`sf code-analyzer run`** — NOT `sf scanner run` (deprecated v3).
2. **No `--format` flag.** Use `--output-file`; the extension determines the format.
3. **Always** pass `--output-file` with a timestamped name (e.g. `./code-analyzer-results-20260621-143022.json`).
4. **Foreground only**; timeout 1200000ms for large scans.
5. Invalid v3 flags that error: `--format`, `--engine`, `--category`, `--json`. Use `--rule-selector` + `--output-file`.

## Rule-Selector Syntax

`:` = AND, `,` = OR, `()` = grouping.
- Engine only: `pmd` · Engine+category: `pmd:Security` · Engine+severity: `pmd:2`
- Complex: `(pmd,eslint):Security:(1,2)` · Specific rule: `pmd:ApexCRUDViolation` · Everything: `all` · Default: `Recommended`

## Quick Patterns

| User says | Rule selector | Notes |
|-----------|---------------|-------|
| "scan my code" | `Recommended` | Curated set |
| "security review" | `all:Security:(1,2)` | Critical+High |
| "scan my changes" | (git diff) | filter to scannable types → `--target` |
| "run PMD" / "check Apex" | `pmd` | `.cls`/`.trigger` |
| "lint my LWC" | `eslint` | JS/TS/LWC |
| "find duplicates" | `cpd` | clones |
| "data flow analysis" | `sfge` | Java 11+, 10–20 min, `--workspace "force-app"` |
| "performance / governor" | `apexguru` | authenticated org |
| "analyze Flows" | `flow` | `--target **/*.flow-meta.xml` |

## Full Command Shape

```bash
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
sf code-analyzer run \
  --rule-selector <selector> \
  --target <targets> \                                       # optional; omit = whole workspace
  --output-file "./code-analyzer-results-${TIMESTAMP}.json" \
  --include-fixes 2>&1 | tee "./code-analyzer-results-${TIMESTAMP}.log"
```
Always pass `--include-fixes` (enables engine auto-fixes). After scanning, parse and present (severity counts, top issues, top rules, top files). For engine-provided fixes: discover → present → **wait for user confirmation** → apply → summarize. Never apply fixes without a fresh confirmation.

## Prerequisites / Failure

Needs `sf` CLI, `@salesforce/plugin-code-analyzer` (v5+), Java 11+ (PMD/CPD/SFGE), Node 18+ (ESLint/RetireJS), Python 3 (Flow), authenticated org (ApexGuru). If a scan fails on setup/engine startup, **delegate to `configuring-code-analyzer`**, then return and re-run.

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win.

### 1 — This Project Uses Code Analyzer v5

The IBX `generating-apex` skill **requires** a Code Analyzer pass in its validate phase, and `deploying-metadata` references Code Analyzer v5. `sf code-analyzer --help` should succeed; if not, hand off to `configuring-code-analyzer`.

### 2 — Default Scan Scope = `force-app`

IBX custom code lives under `force-app/main/default`. Scope scans to it to avoid noise from `vlocity_export/`, `metadata-export/`, scripts, and docs:

```bash
sf code-analyzer run --rule-selector Recommended \
  --target "force-app/main/default" \
  --output-file "./code-analyzer-results-$(date +%Y%m%d-%H%M%S).json" --include-fixes
```

### 3 — Ignore OmniStudio-Managed & Generated Artifacts

Do **not** flag the `omnistudio` managed package or generated OmniStudio metadata as fixable code. OmniStudio assets (`*.oip-meta.xml`, `*.rpt-meta.xml`, `*.os-meta.xml`, `*.ouc-meta.xml`) are authored via the OmniStudio skills, not via analyzer auto-fixes. Apply auto-fixes only to `PRM_*` Apex/LWC source. Persisted excludes belong in `code-analyzer.yml` (see `configuring-code-analyzer`).

### 4 — Pre-Deploy / Pre-PR Diff Scan

Before a deploy or PR, scan only what changed (matches the IBX deploy workflow):

```bash
git diff --name-only main...HEAD | grep -E '\.(cls|trigger|js)$'   # filter scannable types
sf code-analyzer run --rule-selector "Recommended" --target <those files> \
  --output-file "./code-analyzer-results-$(date +%Y%m%d-%H%M%S).json" --include-fixes
```

### 5 — Security Rules Map to IBX Conventions

`ApexCRUDViolation` / FLS findings should be resolved using IBX patterns (`WITH USER_MODE`, `AccessLevel.USER_MODE`, `with sharing`) per `generating-apex` — not by suppressing the rule. Suppress only with an explicit, documented reason in `code-analyzer.yml`.

### 6 — Hand-offs

Setup/config/CI gates → `configuring-code-analyzer`. Implementing a fix → `generating-apex`. Deploying after a clean scan → `deploying-metadata`.
