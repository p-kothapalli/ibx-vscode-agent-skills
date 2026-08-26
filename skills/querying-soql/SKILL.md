---
name: querying-soql
description: 'SOQL query generation, optimization, and analysis with 100-point scoring. Use
  this skill when the user needs SOQL/SOSL authoring or optimization: natural-language-to-query
  generation, relationship queries, aggregates, query-plan analysis, and performance or safety
  improvements for Salesforce queries. TRIGGER when: user writes, optimizes, or debugs SOQL/SOSL
  queries, touches .soql files, or asks about relationship queries, aggregates, or query performance.
  DO NOT TRIGGER when: bulk data operations (use handling-sf-data), Apex DML logic (use generating-apex),
  or report/dashboard queries.'
metadata:
  version: 1.1-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/querying-soql
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
argument-hint: '[object or question the query should answer]'
---

# querying-soql: Salesforce SOQL Query Expert

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/querying-soql` if it does not auto-load.


Use this skill when the user needs **SOQL/SOSL authoring or optimization**: natural-language-to-query generation, relationship queries, aggregates, query-plan analysis, and performance/safety improvements for Salesforce queries.

## When This Skill Owns the Task

Use `querying-soql` when the work involves: `.soql` files, query generation from natural language, relationship/aggregate queries, query optimization and selectivity analysis, SOQL/SOSL syntax and governor-aware design.

Delegate elsewhere when the user is performing bulk data operations (`handling-sf-data`), embedding query logic inside broader Apex (`generating-apex`), or debugging via logs (`debugging-apex-logs`).

---

## Required Context to Gather First

- target object(s)
- fields needed
- filter criteria
- sort / limit requirements
- whether the query is for display, automation, reporting-like analysis, or Apex usage
- whether performance / selectivity is already a concern

---

## Recommended Workflow

### 1. Generate the simplest correct query
Prefer only needed fields, clear WHERE criteria, reasonable LIMIT, relationship depth only as deep as necessary.

### 2. Choose the right query shape
| Need | Default pattern |
|---|---|
| parent data from child | child-to-parent traversal |
| child rows from parent | subquery |
| counts / rollups | aggregate query |
| records with / without related rows | semi-join / anti-join |
| text search across objects | SOSL |

### 3. Optimize for selectivity and safety
Check indexed/selective filters, no unnecessary fields, no avoidable wildcard/scan-heavy patterns, security enforcement expectations.

### 4. Validate execution path if needed
Hand off execution to `handling-sf-data`.

---

## High-Signal Rules

- never use `SELECT *` style thinking; query only required fields
- do not query inside loops in Apex contexts
- prefer filtering in SOQL rather than post-filtering in Apex
- use aggregates for counts and grouped summaries
- evaluate wildcard usage carefully; leading wildcards often defeat indexes
- account for security mode / field access requirements when queries move into Apex

---

## Output Format

1. **Query purpose**
2. **Final SOQL/SOSL**
3. **Why this shape was chosen**
4. **Optimization or security notes**
5. **Execution suggestion if needed**

---

## Score Guide

| Score | Meaning |
|---|---|
| 90+ | production-optimized query |
| 80–89 | good query with minor improvements possible |
| 70–79 | functional but performance concerns remain |
| < 70 | needs revision before production use |

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win.

### 1 — MANDATORY: Archive Every SOQL Query (project rule)

Per the workspace rule `soql-queries-archive`, **every** SOQL query you produce for the user (or that the user could run) MUST also be saved to the persistent knowledge base:

- Folder: `requirements/SOQL/` (create if missing)
- Filename: `YYYY-MM-DD_<TopicInPascalCase>.md` (append to today's topic file if it exists)
- Required block structure per query:

```markdown
## Query N — <short purpose>

**Object:** `MyObject` (or `MyObjectHistory`, etc.)
**Use case:** What this query answers in plain English.

\`\`\`sql
SELECT ...
FROM ...
WHERE ...
\`\`\`

**Sample result / row count (if known):**
**Notes / gotchas:**
```

Correct a query block in-place (don't leave broken queries). **Do not skip this even for "simple" queries.** Exception: pure schema/describe exploration and queries used only for your own internal Grep/Read do not go in the archive.

### 2 — Security: `WITH USER_MODE` for Apex-Embedded SOQL

When a query will be embedded in Apex, default to **`WITH USER_MODE`** (the IBX Apex standard) so FLS/CRUD are enforced. Use `WITH SECURITY_ENFORCED` only where `USER_MODE` is unavailable. Embed via the `generating-apex` selector/service patterns; classes are `PRM_*` and `with sharing`.

### 3 — OmniStudio Object Queries (frequent in this org)

This org runs OmniStudio (Core/`omnistudio`). Common inventory queries:

```sql
-- OmniScripts vs Integration Procedures share OmniProcess — ALWAYS filter on IsIntegrationProcedure
SELECT Id, Type, SubType, Language, IsActive, VersionNumber
FROM OmniProcess
WHERE IsIntegrationProcedure = false AND IsActive = true

-- Integration Procedures
SELECT Id, Type, SubType, IsActive, VersionNumber
FROM OmniProcess
WHERE IsIntegrationProcedure = true AND IsActive = true

-- FlexCards (DataSourceConfig, NOT Definition)
SELECT Id, Name, IsActive, VersionNumber FROM OmniUiCard WHERE IsActive = true

-- Data Mappers + items (FK is OmniDataTransformationId — full word)
SELECT Id, Name, Type, IsActive FROM OmniDataTransform
SELECT Id, OmniDataTransformationId, InputObjectName, OutputObjectName FROM OmniDataTransformItem
```

Filter to `IsActive = true` to reflect runtime (assets have many versions).

### 4 — Domain Objects & Selectivity

Core domain objects are credentialing-centric (Account, Case, Practitioner/Provider records, Practice Location, Adverse Action, QC). Filter on indexed fields (Id, Name, RecordTypeId, external IDs/NPI/TIN, CreatedDate/LastModifiedDate). For RecordType-scoped queries prefer filtering by `RecordType.DeveloperName`. For history analysis use the `*History` objects (and watch the wrong-FK gotchas noted in `requirements/SOQL/`).

### 5 — Graph-First for "where is this query used"

To find where a query/field/selector is used in the codebase, use the **code-review-graph MCP** tools before Grep.

### 6 — IBX SOQL Checklist

- [ ] Query saved to `requirements/SOQL/YYYY-MM-DD_<Topic>.md` with the required block
- [ ] Only required fields; selective/indexed WHERE; reasonable LIMIT
- [ ] `WITH USER_MODE` if Apex-embedded; no SOQL in loops
- [ ] `IsIntegrationProcedure` filter on `OmniProcess`; `IsActive=true` where runtime matters
- [ ] Execution delegated to `handling-sf-data` if the user needs to run it
