# Life Sciences Cloud (LSC) Data Model & Domain Reference

Grounding for LSC stories: acronyms, the object model by sub-domain, and the
compliance concerns that drive non-functional requirements. **Standard LSC
objects/fields must be verified via the `salesforce-docs` MCP** before you assert
an exact API name — this file is a naming/starting-point aid, not a substitute
for verification. This workspace (IBXQA) is a PNM org, so LSC objects are often
**not deployed here** — treat unverifiable components as *proposed*.

## Contents

- Acronym glossary
- Compliance & regulatory drivers
- Commercial (Sales) object model
- Medical (MSL) object model
- Market Access object model
- Cross-domain / platform objects

---

## Acronym glossary (verbatim from the LSC reference)

| Acronym | Expansion |
|---|---|
| **HCP** | Health Care Provider |
| **HCO** | Health Care Organization |
| **KAM** | Key Account Manager |
| **DC** | Data Cloud |
| **KOL** | Key Opinion Leader |
| **DOL** | Digital Opinion Leader |
| **LSC** | Life Science Cloud |
| **OOB / OOTB** | Out Of the Box |
| **MSL** | Medical Science Liaison |

Additional terms used across LSC stories: **PDMA** (Prescription Drug Marketing
Act — sample accountability), **CLM** (Closed Loop Marketing), **DAM** (Digital
Asset Management), **Open Payments / Sunshine Act** (spend transparency).

---

## Compliance & regulatory drivers (feed Phase-2 Q6 non-functional requirements)

| Concern | When it applies | Story implication |
|---|---|---|
| **Sample accountability (PDMA)** | Any sample/product disbursement to HCPs | On-hand reconciliation, signatures, lot/expiry tracking, eligibility by license |
| **Consent management** | Contacting HCPs (email, calls, channels) | Capture/enforce consent before engagement |
| **Open Payments / Sunshine Act** | Spend / transfers of value to HCPs | Capture spend, meals, honoraria for reporting |
| **GxP / validation** | Regulated data + audited workflows | Field history, audit trail, validated changes |
| **HCP licensure** | Sampling, prescribing-related actions | Validate active license + state eligibility |
| **Expense / spend integrity** | Visit expenses synced to SAP Concur | Sync-status tracking, edit locks while syncing/submitted, attachment limits — see `concur-integration.md` |

---

## Commercial (Sales) object model

> Field sales to HCPs/HCOs. Verify exact API names via `salesforce-docs`.

| Object (business term) | Purpose | Notes |
|---|---|---|
| **Account** (HCP = Person Account; HCO = Business Account) | The provider/organization being engaged | Person Accounts for individual HCPs |
| **Address / Location** | Where an account can be visited / sampled | An HCP may have many addresses |
| **Visit** (formerly Veeva "Call") | A field interaction with an account | Parent of visit tasks/details |
| **Visit Task / Call Objective** | Planned activities within a visit | e.g. present product, drop sample |
| **Call Report / Interaction** | The recorded outcome of a visit | |
| **Product** (Product2) | The marketed product/brand | |
| **Product Item** | On-hand inventory of a product at a location | LSC inventory unit |
| **Production Batch / Production Batch Item** | Manufactured lot + lot line for samples | Lot number, expiration |
| **Sample Order / Sample Request** | Request to replenish samples | |
| **Sample Transaction / Disbursement** | Sample given to an HCP | Signature, quantity, lot |
| **Inventory / Inventory Count / Reconciliation** | Periodic physical count vs. system | Discrepancy handling |
| **Product Transfer** | Move stock between locations/reps | |
| **Territory / Alignment** | Which accounts a rep owns | |
| **MC Cycle Plan / Call Plan / Target** | Planned reach & frequency per account | |
| **Action Launcher** | Guided quick actions on a record | Launches OmniScripts/flows |
| **Event / Meeting (Managed Event)** | Parent record for an event/meeting | Event Expenses component; actual + estimated expenses |
| **Expense** (`ExpenseEntry`) | An expense line (meal, travel, honoraria) | Created under a Visit or Event; syncs to SAP Concur |
| **Expense Type** | Classifies an expense | Holds the estimated-allocation Distribution Type |
| **Expense Report** | Grouping of expenses submitted together | 1:1 mapping to a Concur report |
| **Expense Report Entry** | **Junction** linking an Expense to an Expense Report | The link is a junction record, not a lookup field on Expense |
| **Expense Participant** | Attendee/participant allocation of an expense | Attendees, Speakers, Colleagues, Write-Ins, Non-Profiled Attendees |
| **IntegrationJobRun** | Stores each MuleSoft sync job run | Job name, timestamp, status, processed count |

> **Concur expense integration:** the Visit/Event → Expense → Expense Report Entry
> → Expense Report model and its bidirectional SAP Concur sync (MuleSoft connector,
> `ExpenseSystemIntegrationStatus` field, edit/delink matrix, actual-vs-estimated
> expenses, estimated allocation to participants, business rules) is documented in
> full in `references/concur-integration.md` — read it for any expense/Concur story.

## Medical (MSL) object model

| Object (business term) | Purpose | Notes |
|---|---|---|
| **Account** (HCP/HCO, KOL/DOL flagged) | Scientific stakeholders | KOL/DOL scoring/tiering |
| **Scientific Interaction / Engagement** | MSL touchpoint with a KOL | Non-promotional |
| **Medical Inquiry / Medical Information Request** | HCP question routed to Medical | SLA, response tracking |
| **Assessment / Assessment Task** | Structured evaluations (e.g. KOL profiling) | Uses Assessment framework |
| **Consent** | Permission to engage on channels | |
| **Adverse Event (intake)** | Safety signal capture during interactions | Routed to PV |

## Market Access object model

| Object (business term) | Purpose | Notes |
|---|---|---|
| **Payer Account** (HCO subtype) | Insurers/PBMs | |
| **Formulary / Coverage** | Product coverage status by payer | |
| **Contract / Agreement** | Access & pricing agreements | |
| **Program / Access Program** | Patient/access support programs | |

## Cross-domain / platform objects

| Object (business term) | Purpose |
|---|---|
| **Account (HCP/HCO)**, **Contact**, **Address/Location** | Shared master data |
| **Consent**, **Communication Subscription** | Channel/consent management |
| **Data Cloud (DC)** entities | Unified profile, segmentation, activation |
| **Territory Management / Alignment** | Ownership & rollups |
| **Content / DAM / Approved Documents** | Approved content for engagement (CLM/Engage) |

---

## Notes for greenfield LSC in this workspace

- The IBXQA org is PNM-focused; LSC OmniScripts/objects likely aren't present.
- Do NOT assert an LSC component exists after a failed `code-review-graph` lookup.
  Instead mark it *proposed* and add a Clarification Question about whether the
  LSC managed package / data model is installed in the target org.
- Prefer standard LSC objects over new custom objects; only propose `LSC_*`
  custom objects/fields when a standard object cannot carry the requirement.
