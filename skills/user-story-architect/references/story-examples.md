# Exemplar User Stories

These stories demonstrate the expected quality, depth, and format for the
**User Story Solution Architect** (v1.7 contract). Every example below already
conforms to the contract in `SKILL.md`:

- **Concrete business persona** — never "user", "business user", "developer",
  or "system".
- **Acceptance Criteria in business language** using the four-pattern library
  (A = Given/When/Then behavioural, B = field/object/metadata creation,
  C = permission set / FLS, D = field update rules). No Apex class names, IP
  version numbers, IP step numbers, SOQL, or API field names inside a
  Pattern-A Given/When/Then.
- A concise **`## Technical Implementation (high-level)`** section after the
  ACs — this is where all the API/class/IP detail lives.
- A **`## Definition of done`** checklist and an **`## Estimated Effort`** table.

When generating a new story, match this level of specificity and this
separation of business language (ACs) from implementation detail (Technical
Implementation section).

## Contents

- Example 1 — OmniScript element change (Pattern A)
- Example 2 — Integration Procedure + DataRaptor change (Pattern A)
- Example 3 — New custom fields (Pattern B) + permission sets (Pattern C)
- Example 4 — Field update rules (Pattern D)
- Key Patterns to Follow

---

## Example 1 — OmniScript element change (Pattern A)

> Scenario: adding a state + counties to a credentialing form.

# USER STORY 1: Capture Georgia providers on the Practitioner Participation Form

**Persona:** Credentialing Specialist
**Priority:** P0
**OmniScript:** PRM_PractitionerParticipationForm_English
**Integration Procedures:** N/A
**Relevant Requirements:** FHN-04, FHN-05 (Portal); PIE-02 (License State)

---

## Story

**As a** Credentialing Specialist,
**I want** to select Georgia (and its target counties) when I enter license and
primary-address information for a provider,
**So that** I can credential AmeriHealth Georgia (AHGA) network providers without
having to work around a form that only offers the tri-state region.

**Why it matters:** GA providers now submit through the AHGA participation
process. Until the form offers Georgia, specialists cannot capture these
applications at all, blocking the entire AHGA launch.

---

## Acceptance Criteria

**AC-1 — Georgia is selectable as a license and address state**

**Given** a Credentialing Specialist is entering license or primary-address
information for a Georgia provider on the Practitioner Participation Form,
**When** they open the state selector,
**Then** Georgia is available as a selectable option alongside the existing
states,
**And** selecting Georgia does not clear or invalidate any data already entered
on the form.

**AC-2 — Target Georgia counties are offered once Georgia is chosen**

**Given** a Credentialing Specialist has selected Georgia as the state,
**When** they open the county selector,
**Then** the five target counties (Fulton, Cobb, Clayton, DeKalb, Gwinnett) are
available for selection.

**AC-3 — Non-Georgia states are unaffected (regression guard)**

**Given** a Credentialing Specialist is credentialing a provider in an existing
tri-state region,
**When** they complete the state and county selectors,
**Then** the previously available states and counties behave exactly as before,
**And** no Georgia-only options appear for those states.

---

## Technical Implementation (high-level)

| Component | Type | Change | Notes |
|---|---|---|---|
| `PRM_PractitionerParticipationForm_English` — `PractitionerState` element | Modified OmniScript element | Add Georgia to the option set (or ensure the `optionSource` picklist includes it) | Drives AC-1 |
| `Address.PRM_State__c` | Salesforce picklist | Add Georgia value if `PractitionerState` uses `optionSource` | Drives AC-1 |
| County picklist / county dependency | Salesforce picklist / dependency | Add Fulton, Cobb, Clayton, DeKalb, Gwinnett under Georgia | Drives AC-2 |
| Primary-address state/county elements | Modified OmniScript element | Mirror the state/county option changes on the address block | Drives AC-1, AC-2 |

---

## Definition of done

- [ ] Georgia + 5 counties selectable on license and primary-address blocks
- [ ] Existing states/counties verified unchanged (regression)
- [ ] Picklist + dependency deployed to the target org
- [ ] QA validated with a Georgia test provider end-to-end

---

## Estimated Effort

| Component | Change Type | Effort | Notes |
|---|---|---|---|
| State picklist value | Config | S | Add GA |
| County picklist + dependency | Config | M | 5 counties + dependency |
| OmniScript element updates | OmniScript element | M | State + address blocks |

**Total Estimated Effort:** ~M (AI-estimated — validate with team)

---

## Example 2 — Integration Procedure + DataRaptor change (Pattern A)

> Scenario: surfacing business licenses on a PSV step and allowing new ones.

# USER STORY 2: Verify and add business licenses on the Ancillary PSV step

**Persona:** Ancillary Cred Specialist
**Priority:** P1
**OmniScript:** PRM_AncillaryPSVForm_English, PRM_AncillaryReassessmentPSV_English
**Integration Procedures:** PRM_AncillaryPSVFormDataRetrievalIP, PRM_FetchAncillaryReassessmentPSV
**Relevant Requirements:** Ancillary PSV licensure verification

---

## Story

**As an** Ancillary Cred Specialist,
**I want** to see every business license on file for an ancillary facility while
I verify licensure, and add a missing license without creating a duplicate,
**So that** I can complete primary source verification confidently and keep the
facility's licensure record clean.

**Why it matters:** Business licenses are required for ancillary credentialing.
When existing licenses are not shown, specialists re-enter them, creating
duplicates that later corrupt reporting and rework the PSV step.

---

## Scope

| Flow | OmniScript | Affected Step | Data Source |
|------|------------|--------------|-------------|
| Ancillary PSV (Initial) | PRM_AncillaryPSVForm_English | Verify Licensure | PSV data-retrieval IP |
| Ancillary Reassessment | PRM_AncillaryReassessmentPSV_English | Verify Licensure | Reassessment fetch IP |

---

## Acceptance Criteria

**AC-1 — Existing licenses are displayed on the Verify Licensure step**

**Given** an Ancillary Cred Specialist opens the Ancillary PSV form for a
facility that already has one or more business licenses on file,
**When** they navigate to the Verify Licensure step,
**Then** every business license for that facility is displayed with its number,
state, class, effective/expiration dates, and status.

**AC-2 — A new license can be added against a specific practice location**

**Given** an Ancillary Cred Specialist is on the Verify Licensure step,
**When** they choose to add a new license and select the practice location it
belongs to,
**Then** the new license is captured against that practice location and appears
in the licensure list.

**AC-3 — Duplicate licenses are blocked**

**Given** an Ancillary Cred Specialist is adding a new license,
**When** the license state, number, and class match a license that already
exists for the same practice location,
**Then** the specialist is shown a duplicate error and the license is not saved.

**AC-4 — Reassessment PSV behaves identically**

**Given** an Ancillary Cred Specialist is completing a reassessment PSV,
**When** they reach the Verify Licensure step,
**Then** existing licenses display and the add/duplicate rules behave exactly as
on the initial PSV form.

---

## Technical Implementation (high-level)

| Component | Type | Change | Notes |
|---|---|---|---|
| `PRM_AncillaryPSVFormDataRetrievalIP` | Modified IP | Add business-license extraction and map it into the Verify Licensure response | Drives AC-1 |
| `PRMDRExtractCaseRelatedDataforAncillaryPSVForm` | Modified DataRaptor Extract | Output business-license records linked to the facility via `PRM_HealthcareFacility__c` | Drives AC-1 |
| `VerifyLicensureBusinessLicense` Edit Block | Modified OmniScript element | Target `BusinessLicense`, map licensure fields, `allowNew: true` | Drives AC-2 |
| Duplicate check | Apex / IP / DR | Reject on same License State + Number + Class + Practice Location | Drives AC-3 |
| `PRM_FetchAncillaryReassessmentPSV` | Existing IP (parity) | Confirm reassessment path returns the same license shape | Drives AC-4 |

Business-license fields surfaced: `LicenseNumber`, `PRM_LicenseState__c`,
`PRM_LicenseClass__c`, `PRM_ProviderLicenseEffectiveDate__c`,
`PRM_ProviderLicenseExpirationDate__c`, `PRM_Status__c`, `PRM_VerifiedOn__c`.

---

## Definition of done

- [ ] Existing licenses display on both PSV forms
- [ ] Add-new persists against the chosen practice location
- [ ] Duplicate rule enforced (state + number + class + location)
- [ ] Initial and reassessment PSV verified for parity
- [ ] ≥ 85% Apex coverage on the duplicate-check logic (if Apex is used)

---

## Estimated Effort

| Component | Change Type | Effort | Notes |
|---|---|---|---|
| IP mapping | IP | M | Add license extraction + response map |
| DataRaptor output | DataRaptor | M | Add license output node |
| Edit Block config | OmniScript | L | Add-new + field mapping |
| Duplicate check | Apex/IP | L | Cross-field rule |

**Total Estimated Effort:** ~L (AI-estimated — validate with team)

---

## Example 3 — New custom fields (Pattern B)

> Scenario: a field-creation story. Note the ACs are structured bullets, not
> Given/When/Then — Pattern B is technical-spec by nature.

# USER STORY 3: Add re-assessment tracking fields to the Ancillary Assessment object

**Persona:** Ancillary Cred Specialist (acting as data steward)
**Priority:** P1
**OmniScript:** N/A
**Integration Procedures:** N/A
**Relevant Requirements:** Re-assessment reporting

---

## Story

**As an** Ancillary Cred Specialist,
**I want** the assessment record to store when a re-assessment was last completed
and by whom,
**So that** I can report on re-assessment cadence and prove compliance without
manually reconstructing history.

**Why it matters:** Re-assessment compliance is audited. Today the completion
date lives only in notes, so reporting is manual and error-prone.

---

## Acceptance Criteria

**AC-1 — Create the following fields on Ancillary Assessment**

- **API Name:** PRM_LastReassessmentDate__c
  - **Object:** PRM_AncillaryAssessment__c
  - **Type:** Date
  - **Label:** Last Reassessment Date
  - **Help text:** The date the most recent re-assessment was completed.
  - **Track History:** true
  - **Required:** false

- **API Name:** PRM_LastReassessmentBy__c
  - **Object:** PRM_AncillaryAssessment__c
  - **Type:** Lookup(User)
  - **Label:** Last Reassessed By
  - **Help text:** The specialist who completed the most recent re-assessment.
  - **Track History:** true
  - **Required:** false

**AC-2 — Field Access & Permission Sets**

- **PRM_DataModifyAll:**
  - Object level: Read, Create, Edit, View All Records
  - Field level: Read and Edit on both new fields
- **PRM_DataViewAll, PRM_NetworkManagementQC:**
  - Object level: Read, View All Records
  - Field level: Read on both new fields
- **PRM_CredentialingUser:**
  - Object level: Read, Create, Edit
  - Field level: Read and Edit on both new fields

---

## Technical Implementation (high-level)

- Two new custom fields on `PRM_AncillaryAssessment__c` with history tracking.
- FLS granted per the permission-set matrix in AC-2 (no profile edits).
- No OmniScript/IP change in this story; a follow-up story wires the fields into
  the re-assessment guided flow.

---

## Definition of done

- [ ] Both fields deployed with history tracking enabled
- [ ] FLS applied per AC-2 on all four permission sets
- [ ] Fields visible on the Ancillary Assessment page layout for eligible roles

---

## Estimated Effort

| Component | Change Type | Effort | Notes |
|---|---|---|---|
| 2 custom fields | Config | S | Date + User lookup |
| History tracking | Config | S | Enable on both |
| Permission sets | Config | S | 4 perm sets |

**Total Estimated Effort:** ~S (AI-estimated — validate with team)

---

## Example 4 — Field update rules (Pattern D)

> Scenario: a computed-value AC with many conditional branches. Pattern D keeps
> the branching legible instead of cramming it into a single Then.

# USER STORY 4: Recalculate network effective dates when a location is reactivated

**Persona:** PDM Specialist
**Priority:** P1
**OmniScript:** PRM_PDMManualUpdate_English
**Integration Procedures:** PRM_PDMRecordsCreation
**Relevant Requirements:** Network effective-date accuracy

---

## Story

**As a** PDM Specialist,
**I want** the network effective dates to be recalculated correctly when I change
a practice location's status or dates,
**So that** downstream network participation reflects the true effective window
without manual correction.

**Why it matters:** Incorrect effective dates cause claims and participation
errors. The rules are conditional and currently applied inconsistently by hand.

---

## Acceptance Criteria

**AC-1 — System auto-recalculates effective dates on save**

**Given** a PDM Specialist changes a practice location's activation status or
effective dates,
**When** they save the change,
**Then** the location's effective window is recalculated per the rules in AC-2,
**And** the specialist is never asked to compute the dates manually.

**AC-2 — Effective-date update rules**

**Given** a practice-location change is being saved,
**When** the effective window is recalculated,
**Then** the following fields are set per the rules below:

- **Effective From =**
  - When the location is Inactive -> {Effective Date of Change}
  - When Active AND {new Effective Date of Change} < current Effective From -> {Effective Date of Change}
  - Else -> current Effective From
- **Effective To =**
  - If an Effective To was entered in the guided flow AND the location is Inactive -> {new Effective To}
  - If an Effective To was entered AND the location is Active AND {new Effective To} > current Effective To -> {new Effective To}
  - If no Effective To was entered in the guided flow -> NULL
- **Active =**
  - If Effective From <= TODAY AND Effective To > TODAY -> Active
  - If Effective To = NULL -> (Effective From <= TODAY -> Active; else Inactive)
- **Pending = FALSE**

---

## Technical Implementation (high-level)

| Component | Type | Change | Notes |
|---|---|---|---|
| `PRM_PDMRecordsCreation` | Modified IP | Apply the effective-date rule set before the load step | Drives AC-1, AC-2 |
| Network effective-date fields | DataRaptor Load / Apex | Set Effective From/To, Active, Pending per the rules | Drives AC-2 |

---

## Definition of done

- [ ] All rule branches in AC-2 implemented and unit-tested
- [ ] Reactivation, forward-dating, and open-ended (NULL To) paths covered
- [ ] No manual date entry required for the happy path

---

## Estimated Effort

| Component | Change Type | Effort | Notes |
|---|---|---|---|
| Rule logic | Apex/IP | L | Multi-branch calculation |
| Field load | DataRaptor | M | Map computed values |

**Total Estimated Effort:** ~L (AI-estimated — validate with team)

---

## Key Patterns to Follow

1. **Persona is always a concrete business role** (Credentialing Specialist,
   Ancillary Cred Specialist, PDM Specialist, Network Management QC Specialist).
   Never "user", "business user", "developer", or "system".
2. **Acceptance Criteria are business language.** Pattern A ACs contain no Apex
   class names, IP version/step numbers, SOQL, or API field names — those live
   in the Technical Implementation section.
3. **Pick the right AC pattern:** A (behavioural GWT) is the default; B
   (field/object/metadata creation) and C (permission set / FLS) use structured
   bullets; D (field update rules) uses a nested rules block under the Then.
4. **One `When` per Pattern-A AC.** Edge cases and negative paths get their own
   AC — never merged into a happy-path Then.
5. **Every story has `## Technical Implementation (high-level)`** — a concise
   table naming components, change type, and the AC each row implements. It is
   not a re-spec of the ACs.
6. **Verify component names against the codebase first** using the
   `code-review-graph` MCP tools (`semantic_search_nodes`, `query_graph`),
   falling back to Grep/Read only when the graph returns nothing. Never invent
   `*__c` field names or component names.
7. **Every story includes** a Definition of done checklist and an Estimated
   Effort table; label effort "AI-estimated — validate with team".
