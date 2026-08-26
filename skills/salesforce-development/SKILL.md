---
name: salesforce-development
description: Apply Salesforce best practices and this org's conventions when writing or reviewing
  Apex, triggers, SOQL/DML, async jobs (Queueable/Batch/Schedulable), test classes, LWC, or
  Salesforce metadata. Use whenever editing files under force-app/ or working with .cls, .trigger,
  .lwc, objects, or OmniStudio IPs/DataRaptors.
metadata:
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
---

# Salesforce Development

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/salesforce-development` if it does not auto-load.


Guidance for building governor-safe, secure, testable Salesforce code in this org. The agent already knows Apex syntax — this captures **conventions and non-obvious rules** to follow here.

## Golden rules (Apex)

- **Bulkify everything.** No SOQL or DML **inside loops**. Build collections, then one bulk operation.
- **One bulk DML per object type** per transaction; resolve FKs by inserting parents first, then children.
- **`with sharing`** by default; use `without sharing` only with a documented reason.
- **Enforce CRUD/FLS** — query with `WITH USER_MODE` (or `WITH SECURITY_ENFORCED`) and/or `Security.stripInaccessible(...)`; never trust client input for object/field access.
- **No hardcoded Ids** (record types, users, queues). Resolve at runtime; store config in Custom Metadata / Custom Labels.
- **Mind governor limits**: ≤100 SOQL, ≤150 DML, ≤50k query rows, CPU < 10s sync. Offload heavy/bulk work to async.

## Layered architecture

- **Trigger → Handler**: one trigger per object, no logic in the trigger body — delegate to a handler class.
- **Selector**: all SOQL lives in `*Selector` classes — read-only, typed lists, bulk-safe, zero DML.
- **Service**: business logic; builds records in memory and does its own bulk DML.
- Keep classes single-responsibility; pass state via typed objects or `Map<String,Object>`, not globals.

## Async

- **Queueable** (`implements Queueable`) for chainable async + callouts (`Database.AllowsCallouts`); chain with `System.enqueueJob`.
- **Batchable** (`Database.Batchable<SObject>`, optionally `Database.Stateful`) for large volumes; `Schedulable` for cron.
- Don't call `Database.executeBatch` directly from a trigger context — start it from a one-shot Queueable.
- Prefer Queueable/Batch over `@future` (typed args, chaining, monitoring).

## Tests

- Aim **≥ 85%** coverage (deploy gate is 75%); cover **bulk (200)**, single, empty, and negative/rollback paths.
- Wrap the code under test in **`Test.startTest()` / `Test.stopTest()`**; assert async completes after `stopTest`.
- **Never `@isTest(SeeAllData=true)`** — create data with a test-data factory.
- Assert **outcomes** (`System.assertEquals`), not just "no exception". Use `Test.isRunningTest()` only where unavoidable.

## Metadata / SFDX

- Source format under `force-app/main/default`; deploy with `sf project deploy start`.
- Config → Custom Metadata Types / Custom Settings / Custom Labels (not hardcoded).
- For OmniStudio (IPs / DataRaptors): there are **many versions** per asset — only the one with **`<isActive>true</isActive>`** is live; always ground against the active version.

## This org's conventions (grounded)

- **`PRM_` prefix** on all custom objects, fields, and Apex classes; PascalCase classes, camelCase methods/vars.
- **Trigger pattern** (honors the bypass permission):
  ```apex
  trigger PRM_XxxTrigger on Xxx (after insert) {
      if (FeatureManagement.checkPermission('PRM_TriggerBypassPermission') == false) {
          new PRM_XxxTriggerHandler().execute();
      }
  }
  ```
- **Error logging**: reuse **`PRM_ExceptionLogger.logException(...)` / `logExceptionReturnId(...)`** — don't build a new logger.
- **Record types**: resolve by DeveloperName via cached describe (`Schema.SObjectType.X.getRecordTypeInfosByDeveloperName()`), **not** SOQL on `RecordType`.
- Test class naming: `<Class>Test` (often referenced as `@TestClassName` in the class header).

## Quick review checklist

- [ ] No SOQL/DML in loops; one bulk DML per object type
- [ ] `with sharing` + CRUD/FLS enforced
- [ ] No hardcoded Ids; config in metadata
- [ ] Async used for heavy/bulk work; correct Queueable/Batch choice
- [ ] Tests: bulk + negative paths, `Test.startTest/stopTest`, no `SeeAllData`, real assertions
- [ ] Follows org conventions (PRM_ prefix, trigger bypass, PRM_ExceptionLogger, RT-by-describe)
