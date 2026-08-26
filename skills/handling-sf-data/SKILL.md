---
name: handling-sf-data
description: 'Salesforce data operations with 130-point scoring. Use this skill to create,
  update, delete, bulk import/export, generate test data, and clean up org records using sf
  CLI and anonymous Apex. TRIGGER when: user creates test data, performs bulk import/export,
  uses sf data CLI commands, needs data factory patterns for Apex tests, or needs to seed/clean
  records. DO NOT TRIGGER when: SOQL query writing only (use querying-soql), Apex test execution
  (use running-apex-tests), or metadata deployment (use deploying-metadata).'
metadata:
  version: 1.1-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/handling-sf-data
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
---

# Salesforce Data Operations Expert (handling-sf-data)

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/handling-sf-data` if it does not auto-load.


Use for **data work**: record CRUD, bulk import/export, test data generation, cleanup scripts, data factory patterns.

## Mode Decision

Confirm: **Script generation** (reusable `.apex`/CSV/JSON, no org touched) vs **Remote execution** (records changed in a real org now). Don't assume remote.

## Core Rules

- Objects/fields must already exist (else hand off to `generating-custom-object`/`generating-custom-field` + `deploying-metadata`).
- Describe-first when schema is uncertain (`sf sobject describe`): required fields, createable fields, picklist values, relationships.
- Choose smallest correct mechanism: small CRUD → `sf data` single-record; large → Bulk API 2.0 (`sf data ... bulk`); parent-child → tree import/export; reusable → factory/anonymous Apex; reversible → cleanup/savepoint.
- For automation-sensitive behavior prefer **251+ records**. Use synthetic, non-PII data. Plan cleanup before creating noisy datasets.

## Common Failures

`INVALID_FIELD` (API/FLS) · `REQUIRED_FIELD_MISSING` · `INVALID_CROSS_REFERENCE_KEY` (bad parent) · `FIELD_CUSTOM_VALIDATION_EXCEPTION` (validation rule) · invalid picklist · non-writeable field · bulk limits. Bounded retry: try → retry once corrected → re-describe → pivot. Never loop the same failing command.

## Output

Operation, objects+counts, target org/path, record IDs/files, verification, **cleanup instructions**.

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win.

### 1 — Two Distinct IBX Data Contexts

- **Apex test data** → use the existing **`PRM_TestDataFactory`** (with the `Boolean doInsert` param and bulk helpers). Do NOT scaffold a new factory; extend it. See `generating-apex-test`.
- **Org data ops / migration / one-off fixes** → `sf data` CLI or anonymous Apex against **`qa-sandbox`**.

### 2 — IBX Runs Many Anonymous-Apex Data Scripts

This project relies on anonymous-Apex export/seed/cleanup scripts (the `scripts/` folder is local-only and git-ignored). When generating such a script:
- Target `PRM_*__c` objects and `__c` fields; describe-first against the real schema.
- Run with `sf apex run --file <script>.apex --target-org qa-sandbox`.
- Keep PII synthetic; provide an explicit cleanup/rollback (delete-by-pattern or `Database.setSavepoint()`).

### 3 — Bypass Automation for Bulk Loads

IBX bulk operations should skip triggers/flows by running as a user with **`PRM_TriggerBypassPermission`** (Apex triggers) and **`PRM_TriggerFlowBypassPermission`** (Flows). Note this in any seed/migration script so large loads don't fire credentialing automation per-record. Grant via the integration/data permission set (`generating-permission-set`).

### 4 — Respect Validation Rules & Integrations

New/active validation rules and the integration callouts (`PRM_Precisely_API`, `PRM_CAQH_API`, `NPPES_API`, `PRM_SDSApi`) can block or alter inserts. Use describe-backed valid values; for address/provider data, mirror what the Precisely/CAQH/NPPES paths expect, or use the bypass user.

### 5 — Archive Any SOQL You Use

Per the project's `soql-queries-archive` rule, **every SOQL query** you run for a data op must also be saved to `requirements/SOQL/YYYY-MM-DD_<Topic>.md`. For query authoring/optimization, hand off to `querying-soql`.

### 6 — CLI Examples (default `qa-sandbox`)

```bash
# Describe-first
sf sobject describe --sobject PRM_AdverseActionLog__c --target-org qa-sandbox

# Small CRUD
sf data create record --sobject PRM_CaseDataManager__c --values "Name='Test'" --target-org qa-sandbox

# Bulk export / import
sf data export bulk --query "SELECT Id, Name FROM PRM_AdverseActionLog__c" --output-file out.csv --target-org qa-sandbox --wait 10
sf data import bulk --sobject PRM_AdverseActionLog__c --file in.csv --target-org qa-sandbox --wait 10
```

### 7 — Hand-offs

Missing schema → `generating-custom-object`/`generating-custom-field` → `deploying-metadata`. Bulk-sensitive validation → `running-apex-tests`. Production logic consuming data → `generating-apex`. Query writing → `querying-soql`.
