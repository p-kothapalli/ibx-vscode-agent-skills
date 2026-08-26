---
name: generating-lwc-components
description: 'Lightning Web Components with PICKLES methodology and 165-point scoring. Use
  this skill when the user creates or edits LWC components, builds wire service patterns,
  or writes Jest tests for LWC. TRIGGER when: user creates/edits LWC components, touches lwc/**/*.js,
  .html, .css, .js-meta.xml files, or asks about wire service, SLDS, or Jest LWC tests. DO
  NOT TRIGGER when: Apex classes (use generating-apex), Aura components, or Visualforce.'
metadata:
  version: 1.1-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/generating-lwc-components
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
argument-hint: '[component name or OmniScript LWC]'
---

# generating-lwc-components: Lightning Web Components Development

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/generating-lwc-components` if it does not auto-load.


Use this skill when the user needs **Lightning Web Components**: LWC bundles, wire patterns, Apex/GraphQL integration, SLDS 2 styling, accessibility, performance work, or Jest unit tests.

## When This Skill Owns the Task

Use `generating-lwc-components` when the work involves:
- `lwc/**/*.js`, `.html`, `.css`, `.js-meta.xml`
- component scaffolding and bundle design
- wire service, Apex integration, GraphQL integration
- SLDS 2, dark mode, and accessibility work
- Jest unit tests for LWC

Delegate elsewhere when the user is:
- writing Apex controllers or business logic first → [generating-apex](../generating-apex/SKILL.md)
- building Flow XML rather than an LWC screen component → [generating-flow](../generating-flow/SKILL.md)
- deploying metadata → [deploying-metadata](../deploying-metadata/SKILL.md)

---

## Required Context to Gather First

Ask for or infer:
- component purpose and target surface
- data source: LDS, Apex, GraphQL, LMS, or external system via Apex
- whether the user needs tests
- whether the component must run in Flow, App Builder, Experience Cloud, or dashboard contexts
- accessibility and styling expectations

---

## Recommended Workflow

### 1. Choose the right architecture
Use the **PICKLES** mindset:
- prototype
- integrate the right data source
- compose component boundaries
- define interaction model
- use platform libraries
- optimize execution
- enforce security

### 2. Choose the right data access pattern
| Need | Default pattern |
|---|---|
| single-record UI | LDS / `getRecord` |
| simple CRUD form | base record form components |
| complex server query | Apex `@AuraEnabled(cacheable=true)` |
| related graph data | GraphQL wire adapter |
| cross-DOM communication | Lightning Message Service |

### 3. Start from an asset when useful
Use provided assets for:
- basic component bundles
- datatables
- modal patterns
- Flow screen components
- GraphQL components
- LMS message channels
- Jest tests
- TypeScript-enabled components

### 4. Validate for frontend quality
Check:
- accessibility
- SLDS 2 / dark mode compliance
- event contracts
- performance / rerender safety
- Jest coverage when required

### 5. Hand off supporting backend or deploy work
Use:
- [generating-apex](../generating-apex/SKILL.md) for controllers / services
- [deploying-metadata](../deploying-metadata/SKILL.md) for deployment
- [running-apex-tests](../running-apex-tests/SKILL.md) only for Apex-side test loops, not Jest

---

## High-Signal Rules

- prefer platform base components over reinventing controls
- use `@wire` for reactive read-only use cases; imperative calls for explicit actions and DML paths
- do not introduce inaccessible custom UI
- avoid hardcoded colors; use SLDS 2-compatible styling hooks / variables
- avoid rerender loops in `renderedCallback()`
- keep component communication patterns explicit and minimal

---

## Output Format

When finishing, report in this order:
1. **Component(s) created or updated**
2. **Data access pattern chosen**
3. **Files changed**
4. **Accessibility / styling / testing notes**
5. **Next implementation or deploy step**

Suggested shape:

```text
LWC work: <summary>
Pattern: <wire / apex / graphql / lms / flow-screen>
Files: <paths>
Quality: <a11y, SLDS2, dark mode, Jest>
Next step: <deploy, add controller, or run tests>
```

---

## Local Development Server

Preview LWC components locally with hot reload — no deployment needed. Run the commands in `scripts/local-dev-preview.sh` to start a local dev session for a component, app, or Experience Cloud site.

Local Dev commands install just-in-time on first run. They are long-running processes that open a browser with live preview. Changes to `.js`, `.html`, and `.css` files auto-reload instantly. Requires an active org connection for data and Apex callouts.

---

## Cross-Skill Integration

| Need | Delegate to | Reason |
|---|---|---|
| Apex controller or service | [generating-apex](../generating-apex/SKILL.md) | backend logic |
| embed in Flow screens | [generating-flow](../generating-flow/SKILL.md) | declarative orchestration |
| deploy component bundle | [deploying-metadata](../deploying-metadata/SKILL.md) | org rollout |
| create supporting metadata (message channels, objects) | [deploying-metadata](../deploying-metadata/SKILL.md) | metadata deployment |

---

## Reference File Index

### Start here
- [references/component-patterns.md](references/component-patterns.md) — component architecture patterns and bundle design
- [references/slds-design-guide.md](references/slds-design-guide.md) — SLDS 2 styling, dark mode, CSS hooks
- [references/lwc-best-practices.md](references/lwc-best-practices.md) — high-signal rules and anti-patterns
- [references/scoring-and-testing.md](references/scoring-and-testing.md) — 165-point scoring rubric across 8 categories
- [references/jest-testing.md](references/jest-testing.md) — Jest unit test patterns and async rendering helpers
- [references/slds-blueprints.json](references/slds-blueprints.json) — machine-readable SLDS component blueprints
- [references/cli-commands.md](references/cli-commands.md) — SF CLI commands for LWC development

### Accessibility / performance / state
- [references/accessibility-guide.md](references/accessibility-guide.md) — WCAG, ARIA, keyboard navigation patterns
- [references/performance-guide.md](references/performance-guide.md) — lazy loading, debouncing, rerender safety
- [references/state-management.md](references/state-management.md) — reactive state patterns and LMS
- [references/template-anti-patterns.md](references/template-anti-patterns.md) — common HTML template mistakes to avoid

### Integration / advanced features
- [references/lms-guide.md](references/lms-guide.md) — Lightning Message Service patterns
- [references/flow-integration-guide.md](references/flow-integration-guide.md) — Flow screen component design
- [references/advanced-features.md](references/advanced-features.md) — Spring '26 features: TypeScript, lwc:on, GraphQL mutations
- [references/async-notification-patterns.md](references/async-notification-patterns.md) — toast, notifications, async flows
- [references/triangle-pattern.md](references/triangle-pattern.md) — parent-child-sibling communication triangle

### Asset templates
- [assets/basic-component/basicComponent.js](assets/basic-component/basicComponent.js) — wire service, error/loading states, event dispatching
- [assets/datatable-component/datatableComponent.js](assets/datatable-component/datatableComponent.js) — datatable with inline editing
- [assets/flow-screen-component/flowScreenComponent.js](assets/flow-screen-component/flowScreenComponent.js) — Flow screen with input/output properties
- [assets/form-component/formComponent.js](assets/form-component/formComponent.js) — form validation and DML patterns
- [assets/graphql-component/graphqlComponent.js](assets/graphql-component/graphqlComponent.js) — GraphQL wire adapter with cursor-based pagination
- [assets/jest-test/componentName.test.js.example](assets/jest-test/componentName.test.js.example) — Jest test template (copy and rename, remove `.example` suffix)
- [assets/message-channel/lmsPublisher.js](assets/message-channel/lmsPublisher.js) — LMS publisher pattern
- [assets/message-channel/lmsSubscriber.js](assets/message-channel/lmsSubscriber.js) — LMS subscriber pattern
- [assets/modal-component/modalComponent.js](assets/modal-component/modalComponent.js) — modal with focus trap and ESC handling
- [assets/record-picker/recordPicker.js](assets/record-picker/recordPicker.js) — record picker with search
- [assets/state-store/store.js](assets/state-store/store.js) — reactive state store for cross-component state
- [assets/typescript-component/typescriptComponent.ts](assets/typescript-component/typescriptComponent.ts) — TypeScript-enabled component (Spring '26)
- [assets/workspace-api/workspaceComponent.js](assets/workspace-api/workspaceComponent.js) — workspace API for tab and focus management
- [assets/apex-controller/LwcController.cls](assets/apex-controller/LwcController.cls) — Apex controller with `@AuraEnabled(cacheable=true)` patterns

### Scripts
- [scripts/local-dev-preview.sh](scripts/local-dev-preview.sh) — local dev server commands for component, app, and site preview

---

## Score Guide

| Score | Meaning |
|---|---|
| 150+ | production-ready LWC bundle |
| 125–149 | strong component with minor polish left |
| 100–124 | functional but review recommended |
| < 100 | needs significant improvement |

---

## IBX Overrides & Additions

> These rules are IBX-project-specific and **override or extend** the upstream rules above.
> When there is a conflict, IBX rules win. They are grounded in the existing
> `force-app/main/default/lwc/` bundle set (~165 components), the majority of which
> are **OmniScript custom LWCs**, not standalone App Builder components.

### 1 — Naming: `prm` camelCase Prefix

- All new LWC bundles use the **`prm` camelCase prefix** — e.g. `prmAddressGroupManager`, `prmCaseManagerHistory`, `prmProviderLocationSearch`.
- The folder name, the `.js`/`.html`/`.css`/`.js-meta.xml` base name, and the exported class (`PascalCase`, e.g. `PrmAddressGroupManager`) must all match the bundle name.
- Legacy variants exist (`prm_TextElementOverrideGeneric`, `pRMNotLastAndPncDelegated`) — **do not rename them**; use clean `prm` camelCase for all new work.

### 2 — OmniScript Custom LWC Pattern (the dominant pattern here)

Most IBX LWCs are **custom OmniScript elements / step overrides**, not generic UI. They extend OmniStudio base classes via `OmniscriptBaseMixin`. This pattern is the default unless the component is a standalone App Builder / record-page component.

```js
import { OmniscriptBaseMixin } from "omnistudio/omniscriptBaseMixin";
import OmniscriptSetValues from "omnistudio/omniscriptSetValues";

export default class PrmSetValueNext extends OmniscriptBaseMixin(OmniscriptSetValues) {
    execute(event) {
        try {
            return Promise.resolve(
                super.execute(event)
                    .then(() => {
                        super.omniNextStep();
                    })
                    .catch((err) => {
                        // surface error to the user; do not swallow silently
                        return err;
                    })
            );
        } catch (err) {
            // log/handle; never leave the OmniScript in a stuck state
        }
    }
}
```

Key OmniScript LWC APIs (provided by the mixin/base — do **not** reinvent):
- **Read data:** `this.omniJsonData`, `this.omniScriptHeaderDef`, `this.omniJsonDataStr`
- **Write data:** `this.omniUpdateDataJson(data)` (merges into the OmniScript data JSON)
- **Navigation:** `super.omniNextStep()`, `super.omniPrevStep()`, `super.omniJumpToStep(stepName)`
- **Save / actions:** `super.omniSaveForLater()`, `super.omniApplyCallResp(resp)`
- **Validation:** `super.omniValidate()`

Rules:
- Prefer **overriding the standard OmniStudio base element** (e.g. `omniscriptSetValues`, `omniscriptText`, `omniscriptTypeahead`) over building a from-scratch component, so native behavior is preserved.
- Always call `super.execute(event)` (or the relevant base method) before adding custom behavior, unless you are intentionally fully replacing it.
- Never mutate `this.omniJsonData` directly — go through `this.omniUpdateDataJson(...)` so the OmniScript engine tracks the change.
- Handle promise rejections; never leave the OmniScript stuck on a step.

### 3 — meta.xml for OmniScript LWCs

OmniScript custom LWCs must declare the OmniStudio runtime namespace and be exposed:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>59.0</apiVersion>
    <isExposed>true</isExposed>
    <runtimeNamespace>omnistudio</runtimeNamespace>
</LightningComponentBundle>
```

- `<runtimeNamespace>omnistudio</runtimeNamespace>` is **required** for the component to be selectable inside an OmniScript.
- Match the API version used by the surrounding OmniScript LWCs (currently `59.0` for this set) rather than defaulting to 66 — bumping it in isolation can break OmniStudio runtime compatibility. Confirm before changing.
- Standalone (non-OmniScript) components follow the normal pattern (no `runtimeNamespace`, add `<targets>` such as `lightning__RecordPage`, `lightning__AppPage`, `lightning__FlowScreen`).

### 4 — Cross-Component Communication

- Within OmniScripts, coordinate via the OmniScript data JSON and the shared utilities **`prmPubSubUtil`** / **`prmOmniUtils`** (the established pub/sub pattern here) rather than introducing LMS.
- Reuse these existing utility bundles instead of writing new event plumbing.
- Reserve LMS for genuinely cross-DOM, non-OmniScript scenarios (e.g. utility-bar ↔ record-page).

### 5 — Apex Integration

- LWC Apex controllers follow the `generating-apex` IBX rules: `PRM_` prefix, `with sharing`, `WITH USER_MODE` in SOQL, `@AuraEnabled(cacheable=true)` only for read-only methods, and errors rethrown as `AuraHandledException`.
- Many IBX components instead receive data through the OmniScript engine (DataRaptors / Integration Procedures) — when the data already flows through the OmniScript, read it from `this.omniJsonData` rather than adding a redundant `@wire`/imperative Apex call.

### 6 — Jest Testing (OmniStudio-aware)

Reality check: only a small fraction of the 165 bundles currently have Jest tests — increasing coverage is encouraged, but OmniScript LWCs need special handling.

- OmniScript LWCs import from the `omnistudio/*` namespace, which **`sfdx-lwc-jest` cannot resolve out of the box**. You must mock those modules (via `moduleNameMapper` in the Jest config or a manual `__mocks__/` stub) before such a component can be unit tested.
- For OmniScript element overrides, test the **custom behavior you added** (e.g. that `omniNextStep` is invoked after `execute`), mocking the base mixin/element rather than trying to exercise the real OmniStudio runtime.
- Standalone components follow the normal upstream Jest guidance (render, async settle, assert DOM/events).
- Place tests under the bundle's `__tests__/` folder as `{bundleName}.test.js` (matches the existing `prmCaseManagerHistory/__tests__/` convention).
- Local dev preview (`sf lightning dev component`) likewise will not render `runtimeNamespace=omnistudio` components — preview those inside an OmniScript in the org instead.

### 7 — Quick Review Checklist (IBX)

Before marking any LWC work complete, verify every item:

- [ ] Bundle, files, and exported class all use the `prm` camelCase name (PascalCase class)
- [ ] OmniScript LWCs extend `OmniscriptBaseMixin(<base element>)` and call `super.<base method>` appropriately
- [ ] Data written via `this.omniUpdateDataJson(...)`; `this.omniJsonData` never mutated directly
- [ ] meta.xml has `runtimeNamespace=omnistudio` + `isExposed=true` for OmniScript LWCs; matching API version
- [ ] Cross-component coordination uses OmniScript data JSON / `prmPubSubUtil` / `prmOmniUtils`, not ad-hoc events
- [ ] Apex controllers honor `generating-apex` rules (PRM_ prefix, `WITH USER_MODE`, `AuraHandledException`)
- [ ] No swallowed promise rejections; OmniScript never left stuck on a step
- [ ] SLDS styling hooks (no hardcoded colors); accessible markup; no `renderedCallback` rerender loops
- [ ] Jest tests under `__tests__/` mock `omnistudio/*` imports where present
