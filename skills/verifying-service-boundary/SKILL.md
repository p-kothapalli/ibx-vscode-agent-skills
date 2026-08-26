---
name: verifying-service-boundary
description: Build-verification specialist (Agent 6, Service-Boundary) that enforces prm-service-class-boundaries
  on a delivered PRM_*Service — a service is a generic transformer; the batch supplies all
  context. TRIGGER when verifying an Epic-E service class (or when verifying-practitioner-build
  routes service-boundary). DO NOT TRIGGER when authoring the class.
metadata:
  version: 1.0-ibx
  family: build-verification
  spec: docs/build-verification/01_Agent_Catalog.md
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
---

# verifying-service-boundary — Service-Boundary (Agent 6)

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/verifying-service-boundary` if it does not auto-load.


Enforce the existing [`prm-service-class-boundaries`](../../rules/prm-service-class-boundaries.mdc) rule on
a delivered service: a `PRM_*Service` is a generic, reusable transformer; the batch supplies all required
context.

## Inputs

Delivered `PRM_*Service`; the rule.

## Checks

- **No SOQL / selector / describe-for-context** inside the service to fetch inputs.
- **No cross-object correlation** (e.g. CaseManager → Account → NPI) inside the service.
- Reads every dependency from `params`; builds in memory; one bulk DML per object type; returns a generic
  response map; `extends PRM_ServiceBase` implementing `execute(Map<String,Object>) : Map<String,Object>`.

## Verdict

**NEEDS-FIX** on any self-context SOQL or flow/source-specific branching that belongs in the batch/intake.
**PASS** otherwise.

## Append to State

`boundary_findings[]` = `{check, expected, actual, status}`; one `reasoning_chain` line.
