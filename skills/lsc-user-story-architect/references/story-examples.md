# Exemplar LSC User Stories

These stories demonstrate the expected quality, depth, and format for the **LSC
User Story Solution Architect** (v1.0 contract). Every example conforms to the
contract in `SKILL.md`:

- **Concrete LSC business persona** — the field/medical/office role, never
  "user", "business user", or "HCP" (HCP/HCO are subjects, not the login user).
- **Acceptance Criteria in business language** using the five-pattern library
  (A behavioural GWT, B field/object/metadata, C permission set/FLS, D field
  update rules, E record & field specification). No Apex class names, IP
  version/step numbers, SOQL, or API field names inside a Pattern-A GWT.
- A concise **`## Technical Implementation (high-level)`** section after the ACs.
- A **`## Definition of done`** checklist and an **`## Estimated Effort`** table.

## Contents

- Example 1 — Sample Inventory Dashboard (Pattern A, Veeva→LSC migration)
- Example 2 — Record a sample drop with signature (Pattern A + Pattern E)
- Example 3 — New sample-eligibility field + permission sets (Pattern B + C)
- Key Patterns to Follow

---

## Example 1 — Sample Inventory Dashboard (Pattern A, Veeva→LSC migration)

# USER STORY 1: Sample Inventory Dashboard for field reps

**Persona:** Field Sales Representative
**Priority:** P0
**LSC Sub-domain:** Commercial
**OmniScript:** N/A (FlexCard + LWC dashboard) — Proposed (greenfield)
**Integration Procedures:** N/A
**Relevant Requirements:** Veeva Sample Management migration
**Veeva Source:** Sample Management / Sample Inventory

---

## Story

**As a** Field Sales Representative,
**I want** a Sample Inventory Dashboard in the Life Sciences Commercial app to
view and manage my on-hand sample batches,
**So that** I can maintain accurate inventory levels and ensure PDMA compliance.

**Why it matters:** Reps are personally accountable for sample stock. Without a
consolidated on-hand view they over/under-order and risk PDMA reconciliation
failures during audits.

---

## Acceptance Criteria

**AC-1 — On-hand sample lots are shown for the rep's location**

**Given** a Field Sales Representative is logged into the LSC Commercial app,
**When** they open the Sample Inventory Dashboard,
**Then** a filtered list of their active sample lots is displayed with lot
number, product, on-hand quantity, and expiration date,
**And** only lots linked to their own location are shown.

**AC-2 — Quick actions are available from the inventory timeline**

**Given** the rep is viewing their Sample Inventory Dashboard,
**When** they interact with the Inventory Timeline,
**Then** they can launch quick actions to acknowledge a shipment or initiate a
product request.

**AC-3 — Expired lots are visually flagged (edge case)**

**Given** the rep has a sample lot whose expiration date has passed,
**When** the dashboard loads,
**Then** that lot is flagged as expired and excluded from the disbursable
on-hand total.

---

## Technical Implementation (high-level)

| Component | Type | Change | Notes |
|---|---|---|---|
| `lscSampleInventoryCard` | New FlexCard/LWC | Render on-hand lots for the running user's location | Drives AC-1 |
| `lscInventoryTimeline` | New LWC | Timeline with Action Launcher quick actions | Drives AC-2 |
| Product Item / Production Batch Item | Standard LSC objects | Source of on-hand qty, lot, expiry (verify via salesforce-docs) | Drives AC-1, AC-3 |
| Action Launcher config | Config | Expose "Acknowledge Shipment" + "Product Request" actions | Drives AC-2 |

---

## Definition of done

- [ ] Dashboard shows only the running user's active lots with lot/qty/expiry
- [ ] Expired lots flagged and excluded from disbursable total
- [ ] Quick actions launch from the timeline
- [ ] FLS applied so reps see only permitted inventory fields

---

## Estimated Effort

| Component | Change Type | Effort | Notes |
|---|---|---|---|
| Inventory FlexCard/LWC | LWC | XL | On-hand rollup + filtering |
| Inventory Timeline + Action Launcher | LWC/Config | L | Quick actions |

**Total Estimated Effort:** ~XL (AI-estimated — validate with team)

---

## Example 2 — Record a sample drop with signature (Pattern A + Pattern E)

# USER STORY 2: Record a sample drop during a visit

**Persona:** Field Sales Representative
**Priority:** P0
**LSC Sub-domain:** Commercial
**OmniScript:** LSC_RecordSampleDrop_English — Proposed (greenfield)
**Integration Procedures:** LSC_SampleDropParent — Proposed
**Relevant Requirements:** Veeva Sample Transaction migration
**Veeva Source:** Sample Transaction / Disbursement

---

## Story

**As a** Field Sales Representative,
**I want** to record a sample drop to an HCP during a visit and capture their
signature,
**So that** disbursements are compliant and my on-hand inventory stays accurate.

**Why it matters:** Signed sample disbursements are a PDMA requirement; manual
paper capture causes reconciliation gaps and audit findings.

---

## Acceptance Criteria

**AC-1 — A licensed HCP can receive a sample drop**

**Given** a Field Sales Representative is on a visit with an HCP who has an active
license eligible for the product,
**When** they record a sample drop for a product lot they have on hand,
**Then** the disbursed quantity is deducted from their on-hand balance for that
lot,
**And** the HCP's signature is captured against the disbursement.

**AC-2 — Over-disbursement is blocked (edge case)**

**Given** a Field Sales Representative tries to disburse more units than their
on-hand balance for a lot,
**When** they attempt to submit the sample drop,
**Then** the submission is blocked with a clear on-hand-exceeded message and no
inventory or disbursement record is changed.

**AC-3 — Ineligible HCP is blocked (edge case)**

**Given** the HCP's license is expired or not eligible for the product in their
state,
**When** the rep tries to record a sample drop,
**Then** the disbursement is blocked and the rep is told the HCP is not eligible.

**AC-4 — Records created/updated on Submit (outcome = successful drop)**

**Given** a valid, eligible sample drop,
**When** the rep submits it,
**Then** the following records are created/updated exactly as specified:

**Sample Transaction — Create**

| Field | Value | Notes |
|---|---|---|
| Record Type | Disbursement | |
| Status | Submitted | |
| Account (HCP) | {Visited HCP} | lookup |
| Visit | {Current Visit} | lookup |
| Product | {Selected Product} | lookup |
| Production Batch Item (Lot) | {Selected Lot} | lookup |
| Quantity | {Disbursed Qty} | |
| Disbursement Date | {TODAY} | |
| Signature Captured | true | |
| Signed By | {HCP Name} | |

**Product Item (Inventory) — Update**

| Field | Value | Notes |
|---|---|---|
| On-Hand Quantity | {current On-Hand} − {Disbursed Qty} | never below 0 |

---

## Technical Implementation (high-level)

| Component | Type | Change | Notes |
|---|---|---|---|
| `LSC_RecordSampleDrop_English` | New OmniScript | Guided flow: select HCP, product, lot, qty, signature | Drives AC-1 |
| `LSC_SampleAccountabilityService` | New Apex | Eligibility + on-hand validation + inventory decrement | Drives AC-1, AC-2, AC-3 |
| Sample Transaction (standard LSC) | Object write | Create disbursement record per Pattern E | Drives AC-4 |
| Product Item (standard LSC) | Object update | Decrement on-hand per Pattern E | Drives AC-4 |

Fields: verify `Quantity`, on-hand, lot, and signature API names via
`salesforce-docs` before build; mark proposed if the LSC package isn't installed.

---

## Definition of done

- [ ] Valid drop deducts on-hand and records a signed disbursement (AC-1, AC-4)
- [ ] Over-disbursement blocked with no record change (AC-2)
- [ ] Ineligible HCP blocked (AC-3)
- [ ] >= 85% Apex coverage incl. bulk + negative paths
- [ ] FLS applied on new/changed fields

---

## Estimated Effort

| Component | Change Type | Effort | Notes |
|---|---|---|---|
| Sample drop OmniScript | OmniScript | XL | Multi-step + signature |
| Accountability service | Apex | XL | Eligibility + inventory logic |

**Total Estimated Effort:** ~XXL (AI-estimated — validate with team)

---

## Example 3 — New sample-eligibility field + permission sets (Pattern B + C)

> A field-creation story. ACs are structured bullets, not GWT — Pattern B/C are
> technical-spec by nature.

# USER STORY 3: Track sample eligibility on the HCP account

**Persona:** Compliance Specialist
**Priority:** P1
**LSC Sub-domain:** Commercial
**OmniScript:** N/A
**Integration Procedures:** N/A
**Relevant Requirements:** Sample accountability compliance

---

## Story

**As a** Compliance Specialist,
**I want** each HCP account to store its current sample eligibility and the date
it was last evaluated,
**So that** I can audit that reps only sampled eligible providers.

**Why it matters:** PDMA audits require proof of eligibility at the time of each
disbursement; today eligibility is recomputed ad hoc and not stored.

---

## Acceptance Criteria

**AC-1 — Create the following fields on Account (HCP)**

- **API Name:** LSC_SampleEligibility__c
  - **Object:** Account
  - **Type:** Picklist (Eligible, Not Eligible, Needs Review)
  - **Label:** Sample Eligibility
  - **Track History:** true
  - **Required:** false
- **API Name:** LSC_EligibilityEvaluatedOn__c
  - **Object:** Account
  - **Type:** Date
  - **Label:** Eligibility Evaluated On
  - **Track History:** true
  - **Required:** false

**AC-2 — Field Access & Permission Sets**

- **LSC_CommercialAdmin:**
  - Object level: Read, Create, Edit, View All Records
  - Field level: Read and Edit on both new fields
- **LSC_FieldSales:**
  - Object level: Read, Create, Edit
  - Field level: Read on both new fields
- **LSC_ComplianceReadOnly:**
  - Object level: Read, View All Records
  - Field level: Read on both new fields

---

## Technical Implementation (high-level)

- Two new custom fields on `Account` with history tracking.
- FLS granted per the permission-set matrix in AC-2 (no profile edits).
- A follow-up story wires eligibility evaluation into the sample-drop flow.

---

## Definition of done

- [ ] Both fields deployed with history tracking enabled
- [ ] FLS applied per AC-2 on all three permission sets
- [ ] Fields visible on the HCP account layout for eligible roles

---

## Estimated Effort

| Component | Change Type | Effort | Notes |
|---|---|---|---|
| 2 custom fields | Config | S | Picklist + Date |
| Permission sets | Config | S | 3 perm sets |

**Total Estimated Effort:** ~S (AI-estimated — validate with team)

---

## Key Patterns to Follow

1. **Persona is a concrete LSC role** (Field Sales Rep, MSL, KAM, Market Access
   Manager, Compliance Specialist). HCP/HCO/KOL/DOL are subjects, never the login
   persona (unless a genuine HCP portal story).
2. **Acceptance Criteria are business language.** Pattern A ACs contain no Apex
   class names, IP version/step numbers, SOQL, or API field names.
3. **Pair every "records created/updated" outcome with Pattern E** enumerating
   every object and field (no "etc.").
4. **One `When` per Pattern-A AC.** Edge/negative paths get their own AC.
5. **Every story has `## Technical Implementation (high-level)`** cross-refing ACs.
6. **Verify names** — custom via `code-review-graph`, standard LSC via
   `salesforce-docs`; mark greenfield components *proposed*, never invent.
7. **Migration stories** translate all Veeva terms to LSC-native in the body;
   keep the Veeva term only in the `Veeva Source` header.
