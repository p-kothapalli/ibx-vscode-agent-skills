---
name: building-omnistudio-callable-apex
description: 'Salesforce Industries Common Core (OmniStudio/Vlocity) Apex callable generation
  and review skill with 120-point scoring. Use when creating, reviewing, or migrating Industries
  callable Apex implementations. TRIGGER when: user creates or reviews System.Callable classes,
  migrates VlocityOpenInterface or VlocityOpenInterface2, or builds Industries callable extensions
  used by OmniStudio, Integration Procedures, or DataRaptors. DO NOT TRIGGER when: generic
  Apex classes or triggers (use generating-apex), building Integration Procedures (use building-omnistudio-integration-procedure),
  authoring OmniScripts (use building-omnistudio-omniscript), configuring Data Mappers (use
  building-omnistudio-datamapper), or analyzing namespace/dependency issues (use analyzing-omnistudio-dependencies).'
metadata:
  version: 1.0-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/building-omnistudio-callable-apex
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
---

# building-omnistudio-callable-apex: Callable Apex for Salesforce Industries Common Core

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/building-omnistudio-callable-apex` if it does not auto-load.


Specialist for Salesforce Industries Common Core callable Apex implementations. Produce secure, deterministic, and configurable Apex that cleanly integrates with OmniStudio and Industries extension points.

## Scope

- **In scope**: Creating `System.Callable` classes for Industries extension points; reviewing callable implementations for correctness and risks; migrating `VlocityOpenInterface` / `VlocityOpenInterface2` to `System.Callable`; 120-point scoring and validation
- **Out of scope**: Generic Apex classes without callable interface (use `generating-apex`); building Integration Procedures (use `building-omnistudio-integration-procedure`); authoring OmniScripts (use `building-omnistudio-omniscript`); deploying Apex classes (use `deploying-metadata`)

---

## Core Responsibilities

1. **Callable Generation**: Build `System.Callable` classes with safe action dispatch
2. **Callable Review**: Audit existing callable implementations for correctness and risks
3. **Validation & Scoring**: Evaluate against the 120-point rubric
4. **Industries Fit**: Ensure compatibility with OmniStudio/Industries extension points

---

## Workflow (4-Phase Pattern)

### Phase 1: Requirements Gathering

Ask for: entry point (OmniScript, IP, DataRaptor, or other hook), action names (strings passed into `call`), input/output contract, data access needs (CRUD/FLS), side effects (DML, callouts, async).

Then: scan for existing callable classes (`Glob: **/*Callable*.cls`), identify shared utilities/base classes, create a task list.

### Phase 2: Design & Contract Definition

**Define the callable contract**: action list (explicit, versioned strings), input schema (required keys + types), output schema (consistent response envelope).

**Recommended response envelope**:
```
{ "success": true|false, "data": {...}, "errors": [ { "code": "...", "message": "..." } ] }
```

**Action dispatch rules**: use `switch on action`; default case throws a typed exception; no dynamic method invocation or reflection.

**VlocityOpenInterface / VlocityOpenInterface2 contract mapping**:
```
invokeMethod(String methodName, Map<String, Object> inputMap, Map<String, Object> outputMap, Map<String, Object> options)
```

| Parameter | Role | Callable equivalent |
|-----------|------|---------------------|
| `methodName` | Action selector | `action` in `call(action, args)` |
| `inputMap` | Primary input data | `args.get('inputMap')` |
| `outputMap` | Mutable map where results are written | Return value; Callable returns envelope |
| `options` | Additional context | `args.get('options')` |

### Phase 3: Implementation Pattern

**Implementation rules**:
1. Keep `call()` thin; delegate to private methods or service classes
2. Validate and coerce input types early (null-safe)
3. Enforce CRUD/FLS and sharing (`with sharing`, `Security.stripInaccessible()`)
4. Bulkify when args include record collections
5. Use `WITH USER_MODE` for SOQL when appropriate
6. **Namespace handling**: `System.Callable` is a standard interface (no namespace prefix); `omnistudio.VlocityOpenInterface2` uses the managed `omnistudio` package namespace — always qualify it.

**VlocityOpenInterface2 signature**:
```apex
global Boolean invokeMethod(String methodName, Map<String, Object> inputMap,
                           Map<String, Object> outputMap, Map<String, Object> options)
```

Open Interface rules: write results into `outputMap`; return `true` for success, `false` for unsupported/failed actions; share internal private methods with the Callable entry point; populate `outputMap` with the same envelope shape.

### Phase 4: Testing & Validation

Minimum tests: **Positive** (supported action), **Negative** (unsupported action throws), **Contract** (missing/invalid inputs return error envelope), **Bulk** (list inputs without hitting limits).

---

## Migration: VlocityOpenInterface to System.Callable

- Preserve action names (`methodName`) as `action` strings in `call()`
- Pass `inputMap` and `options` as keys in `args`
- Return a consistent response envelope instead of mutating `outMap`
- Keep `call()` thin; delegate to the same internal methods
- Add tests for each action and unsupported action

---

## Best Practices (120-Point Scoring)

| Category | Points | Key Rules |
|----------|--------|-----------|
| **Contract & Dispatch** | 20 | Explicit action list; `switch on`; versioned action strings |
| **Input Validation** | 20 | Required keys validated; types coerced safely; null guards |
| **Security** | 20 | `with sharing`; CRUD/FLS checks; `Security.stripInaccessible()` |
| **Error Handling** | 15 | Typed exceptions; consistent error envelope; no empty catch |
| **Bulkification & Limits** | 20 | No SOQL/DML in loops; supports list inputs |
| **Testing** | 15 | Positive/negative/contract/bulk tests |
| **Documentation** | 10 | ApexDoc for class and action methods |

**Thresholds**: 90+ (Ready) | 70-89 (Review) | <70 (Block)

---

## Guardrails (Mandatory)

Stop and ask the user if any of these would be introduced:
- Dynamic method execution based on user input (no reflection)
- SOQL/DML inside loops
- `without sharing` on callable classes
- Silent failures (empty catch, swallowed exceptions)
- Inconsistent response shapes across actions

---

## Common Anti-Patterns

- `call()` contains business logic instead of delegating
- Action names are unversioned or not documented
- Input maps assumed to have keys without checks
- Mixed response types (sometimes Map, sometimes String)
- No tests for unsupported actions

---

## Reference Skill

Use the core Apex standards, testing patterns, and guardrails in [generating-apex](../generating-apex/SKILL.md).

---

## Output Expectations

- `.cls` — Callable class implementing `System.Callable` with `switch on action` dispatch
- `Test.cls` — Test class with positive, negative, contract, and bulk methods
- `IndustriesCallableException.cls` — Custom exception class (if not already present)

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win. Grounded in the many `PRM_*` classes that
> implement `Callable` / `omnistudio.VlocityOpenInterface2` and are invoked from
> Integration Procedures and OmniScript Remote Actions.

### 1 — IBX Hybrid Pattern: `implements Callable` + `invokeMethod` Router (verified)

The established IBX pattern is a **hybrid**: the class `implements Callable`, and `call()` unpacks the args and delegates to a `methodName`-routed `invokeMethod`. Follow this shape for new IP/OmniScript-callable Apex:

```apex
/**
 * @description Callable utility invoked from Integration Procedures / OmniScript Remote Actions.
 */
global with sharing class PRM_MyIPUtility implements Callable {

    global Object call(String action, Map<String, Object> args) {
        Map<String, Object> input   = (Map<String, Object>) args.get('input');
        Map<String, Object> output  = (Map<String, Object>) args.get('output');
        Map<String, Object> options = (Map<String, Object>) args.get('options');
        return invokeMethod(action, input, output, options);
    }

    global Object invokeMethod(String methodName, Map<String, Object> inputMap,
                               Map<String, Object> outMap, Map<String, Object> options) {
        try {
            if (methodName == 'doSomething') {
                doSomething(inputMap, outMap);
            } else {
                outMap.put('error', 'Unknown method: ' + methodName);
                return false;
            }
            return true;
        } catch (Exception e) {
            PRM_ExceptionLogger.logException(e, 'PRM_MyIPUtility', methodName);
            outMap.put('error', e.getMessage());
            return false;
        }
    }

    private void doSomething(Map<String, Object> inputMap, Map<String, Object> outMap) {
        // Bulkified business logic; read inputMap, write results into outMap
    }
}
```

(Reference implementation in the repo: `PRM_IPUtility.cls` — `implements Callable`, `call()` → `invokeMethod()` routing on `methodName`.)

### 2 — Mandatory IBX Rules (from `generating-apex`)

- `PRM_` class prefix; `global with sharing`.
- Route by `methodName` string; unknown method → set `outMap.put('error', ...)` and return `false` (do not throw out of `invokeMethod`).
- **Log every caught exception via `PRM_ExceptionLogger.logException(e, '<Class>', methodName)`** — never bare `System.debug`, never swallow.
- `WITH USER_MODE` on SOQL; `AccessLevel.USER_MODE` on DML; no SOQL/DML in loops.
- No hardcoded Salesforce IDs; record types via `getRecordTypeInfosByDeveloperName()`.

### 3 — Namespace

- Use `implements Callable` (standard, no prefix) OR `implements omnistudio.VlocityOpenInterface2` (qualify with the `omnistudio` managed-package namespace). Both exist in the codebase; **prefer `Callable`** for new classes (namespace-independent and matches `PRM_IPUtility`).

### 4 — Wiring & Versions

- These classes are invoked from **active** `PRM_*` Integration Procedures (Remote Action element: `remoteClass` = the Apex class, `remoteMethod` = the `methodName`). Confirm the IP's active version references the correct class/method (graph-check first via code-review-graph MCP).

### 5 — Testing (delegate to `generating-apex-test`)

- Test `invokeMethod`/`call` for **each** `methodName`, the **unknown-method** branch (assert `outMap.get('error')` set and `false` returned), and the **exception** branch (drive a failure so `PRM_ExceptionLogger` runs).
- Use `PRM_TestDataFactory`; `PRM_<Class>Test` naming; ≥ 85% coverage. See `generating-apex-test`.

### 6 — IBX Review Checklist

- [ ] `global with sharing class PRM_* implements Callable` with `call()` → `invokeMethod()` router
- [ ] Routes by `methodName`; unknown method returns `false` + `outMap` error (no throw)
- [ ] Every catch logs via `PRM_ExceptionLogger`; no swallowed exceptions
- [ ] `WITH USER_MODE` / `AccessLevel.USER_MODE`; no SOQL/DML in loops; no hardcoded IDs
- [ ] Invoking IP active version references the right class + method (graph-checked)
- [ ] Tests cover each method + unknown-method + exception branches (`generating-apex-test`, ≥85%)
