---
applyTo: "force-app/**"
---

# IBX Salesforce development conventions

Apply these rules whenever editing Apex, LWC, OmniStudio, or other metadata under `force-app/`.

- **`PRM_` naming** on custom Apex, objects, fields; LWC uses `prm`; FlexCards use `PRM<Name>_IBX_<v>`.
- **Bulkify** — no SOQL/DML in loops; one bulk DML per object type; parents before children.
- **`with sharing`** by default; CRUD/FLS via `WITH USER_MODE` and/or `Security.stripInaccessible`.
- **No hardcoded Ids** — record types via cached describe (`getRecordTypeInfosByDeveloperName()`).
- **Error logging** — reuse `PRM_ExceptionLogger`; do not create a new logger.
- **Trigger bypass** — `FeatureManagement.checkPermission('PRM_TriggerBypassPermission')` before handler logic. Flows honor `PRM_TriggerFlowBypassPermission`.
- **Tests** — ≥ 85% coverage; reuse/extend `PRM_TestDataFactory`; never `SeeAllData=true`; wrap in `Test.startTest` / `Test.stopTest`.
- **OmniStudio** — many versions exist; only `<isActive>true</isActive>` is live. Assets are SFDX metadata (`.os-meta.xml` / `.oip-meta.xml` / `.rpt-meta.xml` / `.ouc-meta.xml`), deployed with `sf project deploy start -m …`, not REST record creates.
- **Graph-first** — if `code-review-graph` MCP is available, use it before workspace search.
- Load the matching agent skill (`generating-apex`, `generating-lwc-components`, `building-omnistudio-*`, …) for the task.
