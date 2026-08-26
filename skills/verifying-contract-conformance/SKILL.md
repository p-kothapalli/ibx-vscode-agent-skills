---
name: verifying-contract-conformance
description: 'Build-verification specialist (Agent 3) that proves a delivered PractitionerCreationPayloadValidator,
  IP wrapper, or prm* intake artifact conforms to the request/response contract AND enforces
  every eligibility / ''must / can-only'' rule from the Validation/Eligibility Rule Ledger
  with a server-side check + a negative test. TRIGGER when: verifying an Epic-F payload validator
  or intake LWC, or when the verifying-practitioner-build orchestrator routes contract conformance.
  DO NOT TRIGGER when: authoring the validator (use generating-apex), or for service/batch
  parity (use verifying-parity).'
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

# verifying-contract-conformance — Contract & Eligibility Conformance (Agent 3)

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/verifying-contract-conformance` if it does not auto-load.


Prove the request payload model + response shape conform to the contract, and that **every eligibility
rule that lives in the OmniScript UI today has been ported server-side** for the async model. An unported
duplicate/already-credentialed gate is the highest-risk miss in the whole rebuild.

## Inputs (ground truth)

- **[`02b_Validation_Rule_Ledger.md`](../../../docs/build-verification/02b_Validation_Rule_Ledger.md)** —
  the eligibility-rule ground truth, including **§2.1** (the resolved DataRaptor/Apex condition logic and
  the exact SOQL each rule must re-implement).
- F1 typed payload model; the JSON contracts + sample responses in
  [`PRM_PractitionerCreation_Apex_Service_Flow.md`](../../../docs/reference/PRM_PractitionerCreation_Apex_Service_Flow.md)
  §"Sample Input JSON contracts"; fixtures in
  [`docs/sampleInputs/PractitionerCreation/`](../../../docs/sampleInputs/PractitionerCreation/).

## Checks

1. **Round-trip.** The payload model deserializes every sample fixture losslessly (serialize → compare).
2. **Required keys per branch** — `practitionerCreationType`, `practitioner.npi`, `caseInfo`, `group`
   (Delegated), `locationsToUpsert`, … — present and typed.
3. **Eligibility / "must / can-only" rules (the core check).** For every rule in `02b` §2–§4 (R-E*, R-D*,
   R-F*), assert the delivered validator has **(a) a server-side check** and **(b) a negative test** that
   proves the rejection. Use §2.1 to confirm the check queries the *right* objects/fields:
   - **R-E2** (NPI already a practitioner): query `HealthcareProviderNpi` (`Npi`, `NpiType='Individual'`)
     join `Account` RT `PRM_Practitioner`; reject when `PractitionerId` is non-blank.
   - **R-E3** (currently being credentialed): `Account.PRM_CredentialingStatus__c == 'Credentialing In
     Progress'` AND NPI `IsActive == false`; plus the `Credentialed` + non-PNC/non-delegated gate.
   - **R-E4/E5** (group NPI valid): `HealthcareProviderNpi` (`NpiType='GroupNPI'`,
     `PRM_NPIEffectiveToday__c=true`).
   - **R-E6** (group resolves): `Identifier` EIN (`PRM_Type__c='EIN'`, active, effective-today) →
     `HealthcareFacility` by `PRM_NpiId__r.Npi` (the `getUniqueAccountForNPITaxId` logic).
   - **R-E7** (delegated practice location with **delegated info code**): `HealthcareFacility`
     (`PRM_Active__c=true`) under the group whose NPI matches, gated by `PRM_InfoCodeAssignment__c`
     (`PRM_Active__c=true`) with `PRM_InfoCode__r.PRM_Type__c='Delegated'` (delegated flow) or
     `PRM_Code__c='IBX'` (IBC flow) — the `checkDelegatedPracLoc` logic.
   - **R-D\*** effective-date rules already exist in `PRM_PractitionerCreationValidator.cls`; confirm reuse,
     not re-implementation (CL-9).
4. **Response contract.** The new intake returns `{ success, AsyncJobId }` immediately and defers heavy
   creation. Verify this is the *intended* new contract (not legacy synchronous `PractitionerScreenRecordIds`)
   and that consumers/null-guards account for the async deferral. Legacy IBC responses were already sparse —
   that asymmetry is expected, not a regression.

## Verdict

- **PASS** — lossless round-trip, all required keys typed, every `02b` rule has a server-side check + a
  negative test querying the correct objects/fields, response deferral documented.
- **NEEDS-FIX** — a lossy round-trip, a missing/mistyped required key, an eligibility rule with no
  server-side check or no negative test, a check querying the wrong field, or a dropped response field a
  consumer depends on without documenting the async deferral.
- **BLOCKED** — an **R-E1–R-E3** duplicate / already-being-credentialed gate is **absent** (it prevents
  bad data, not just a noisy field). Name the owner.

## Append to State

`contract_findings[]` = `{rule_id, expected (02b citation §/line), actual (file:line), status}`;
add commands/outputs to `evidence[]`; one `reasoning_chain` line per rule cluster checked.
