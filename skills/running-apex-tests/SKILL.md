---
name: running-apex-tests
description: 'Apex test execution, coverage analysis, and test-fix loops with 120-point scoring.
  Use when the user needs to run Apex tests, check code coverage, fix failing tests, or work
  with *Test.cls / *_Test.cls files. TRIGGER when: user runs Apex tests, checks code coverage,
  fixes failing tests, or touches *Test.cls / *_Test.cls files. DO NOT TRIGGER when: writing
  Apex production code (use generating-apex), Agentforce agent testing (use testing-agentforce),
  or Jest/LWC tests (use generating-lwc-components).'
metadata:
  version: 1.1-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/running-apex-tests
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
argument-hint: '[test class or --tests list]'
---

# running-apex-tests: Salesforce Test Execution & Coverage Analysis

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/running-apex-tests` if it does not auto-load.


Use this skill when the user needs **Apex test execution and failure analysis**: running tests, checking coverage, interpreting failures, improving coverage, and managing a disciplined test-fix loop.

## When This Skill Owns the Task

Use `running-apex-tests` for: `sf apex run test` workflows, Apex unit-test failures, code coverage analysis, identifying uncovered lines, structured test-fix loops.

Delegate elsewhere when: writing/refactoring production Apex (`generating-apex`), testing Agentforce agents (`testing-agentforce`), Jest/LWC tests (`generating-lwc-components`).

---

## Recommended Workflow

1. **Discover test scope** — existing test classes, target production classes, data factories.
2. **Run the smallest useful test set first** — start narrow when debugging; widen after the fix is stable.
3. **Analyze results** — failing methods, exception types/stack traces, uncovered lines, and whether failures indicate bad test data, brittle assertions, or broken production logic.
4. **Run a disciplined fix loop** — delegate code fixes to `generating-apex`; add/improve tests; rerun focused tests before regression.
5. **Improve coverage intentionally** — positive, negative/exception, bulk (251+), callout/async paths.

---

## High-Signal Rules

| Rule | Rationale |
|------|-----------|
| Default to `SeeAllData=false` | Test isolation; no reliance on org data |
| Every test must assert meaningful outcomes | No-assertion tests prove nothing |
| Test bulk behavior with 251+ records | Triggers process in batches of 200 |
| Use factories / `@TestSetup` | Consistent, rolled-back data |
| Pair `Test.startTest()` / `Test.stopTest()` for async | Async completes before assertions |
| Do not hide flaky org dependencies in tests | Prevents intermittent failures |

---

## Gotchas

| Issue | Resolution |
|-------|------------|
| Passes locally, fails in CI org | Check `SeeAllData=true` or undeclared org dependencies |
| Coverage drops after refactor | Run focused class tests, then widen to `RunLocalTests` |
| "Uncommitted work pending" in callout test | Wrap callout in `Test.startTest()`; don't mix DML + callout |
| Mock not taking effect | Call `Test.setMock()` before the code under test |
| `@TestSetup` data missing | It's committed per method — re-query; don't store in statics |

---

## Output Format

```text
Test run: <scope>
Org: <alias>
Result: <passed / partial / failed>
Coverage: <percent / key classes>
Issues: <highest-signal failures>
Next step: <fix class, add test, rerun scope, or widen regression>
```

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win.

### 1 — Commands & Default Org

```bash
# Run a single PRM_ test class against qa-sandbox
sf apex run test --class-names PRM_AddressManagementServiceTest --target-org qa-sandbox --result-format human --code-coverage --wait 10

# Local test suite (used for deploy gates)
sf apex run test --test-level RunLocalTests --target-org qa-sandbox --code-coverage --wait 30

# Watch logs after a failure
sf apex tail log --target-org qa-sandbox
```
Also available via npm: `npm run test:unit` (Jest/LWC), but Apex tests run through `sf apex run test`. Default alias is **`qa-sandbox`**.

### 2 — Coverage Target (project standard)

Deploy gate is **75%**, but the IBX project target is **≥ 85%** per class. When fixing coverage, cover bulk (251+), single, empty, and negative/rollback paths — not just the happy path.

### 3 — Test Naming & Data

- Test classes are **`PRM_<Class>Test`** (no double `PRM_`).
- Use **`PRM_TestDataFactory`** for data (with the `Boolean doInsert` parameter); do **not** create a new factory. See `generating-apex-test`.

### 4 — Triggers Run by Default

IBX triggers run during tests unless intentionally bypassed via the **`PRM_TriggerBypassPermission`** custom permission (set through a permission set + `System.runAs`). Don't blanket-bypass triggers; only bypass when the test's intent requires it. Flows are bypassed via **`PRM_TriggerFlowBypassPermission`**.

### 5 — Exercise `PRM_ExceptionLogger`

Negative tests should drive failures so the `PRM_ExceptionLogger` paths execute (don't mock the logger away). Assert the logged outcome where practical.

### 6 — OmniStudio Callable Apex

For `PRM_*` classes implementing `Callable` / `VlocityOpenInterface2`, run/verify tests for each `methodName`, the unknown-method branch, and the exception branch (see `building-omnistudio-callable-apex`).

### 7 — Failure Triage

For deep runtime failures, hand off to **`debugging-apex-logs`**; for missing/edge test data, hand off to **`handling-sf-data`**; for deploys, **`deploying-metadata`**.

### 8 — IBX Test-Run Checklist

- [ ] Ran narrowest `PRM_*Test` first against `qa-sandbox` with `--code-coverage`
- [ ] Coverage ≥ 85% on changed classes; bulk + negative paths covered
- [ ] Used `PRM_TestDataFactory`; no `SeeAllData=true`; real assertions
- [ ] Trigger bypass only where intended (`PRM_TriggerBypassPermission`)
- [ ] Deep failures triaged via `debugging-apex-logs`
