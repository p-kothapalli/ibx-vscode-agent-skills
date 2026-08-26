# PNM Object Model Reference

## Contents

- Core Objects: IndividualApplication (Case Manager), Account (Vendor/Practitioner), HealthcareFacility, HealthcarePractitionerFacility (PPL), HealthcareFacilityNetwork, Address, BusinessLicense, Identifier
- Custom Metadata (incl. `PRM_AsyncJobConfig__mdt`)
- Async Framework Objects (PRM High-Volume Modernization)
- Ancillary Assessment Objects
- Key Relationships Diagram
- Credentialing Flow Types
- Validation & Duplicate Check Patterns

---

## Core Objects

### IndividualApplication (Case Manager)

The central object for credentialing lifecycle. Each practitioner application
creates one IndividualApplication record that tracks the case from submission
through committee decision.

| Field | API Name | Type | Description |
|-------|----------|------|-------------|
| Status | `Status` | Picklist | Pending, In Progress, Pending Closure, Denied, Case Complete |
| Stage | `PRM_Stage__c` | Picklist | Tracks position in credentialing pipeline |
| Decision Date | `PRM_Decision_Date__c` | Date | When committee/QC made final decision |
| Denial Reason | `PRM_DenialReason__c` | Text | Reason for denial (if applicable) |
| PNC | `PRM_PNC__c` | Checkbox | Participating Network Contractor flag |
| Conversion Flag | `PRM_ReCredToInitialCredConversion__c` | Checkbox | ReCred to Initial Cred conversion |
| Record Type | `RecordType` | Reference | PRM_PractitionerParticipationRequest, PRM_OffCycleCredentialing, PRM_Recredentialing, PRM_Ancillary |

**Key Relationships:**
- `Account` (Practitioner) — via lookup
- `Case` — child Cases for each stage (Application Review, PSV, QC, etc.)

---

### Account (Vendor / Practitioner)

Dual-purpose: represents both Vendor (group practice) and Practitioner (individual).

| Field | API Name | Type | Description |
|-------|----------|------|-------------|
| PNC | `PRM_PNC__c` | Checkbox | Participating Network Contractor |
| Participation Status | `PRM_ParticipationStatus__c` | Picklist | Active, Termed, Pending |
| Credentialing Status | `PRM_CredentialingStatus__c` | Picklist | Credentialing In-progress, Credentialed, Denied |
| Doing Business As | `PRM_DoingBusinessAsName__c` | Text | DBA name |
| Pending | `PRM_Pending__c` | Checkbox | Record is in pending state |

**Record Types:** PRM_Vendor, PRM_Practitioner

---

### HealthcareFacility (Practice Location)

Represents a physical practice location where providers deliver services.

| Field | API Name | Type | Description |
|-------|----------|------|-------------|
| Account | `AccountId` | Lookup(Account) | Vendor/Group this location belongs to |
| Location | `LocationId` | Lookup(Location) | Standard Location record |
| Practice Name | `PRM_PracticeName__c` | Text | Display name |
| DBA Name | `PRM_DoingBusinessAsName__c` | Text | Doing business as |
| PL Number | `PRM_IdentifierHealthcareFacility__r.Name` | Lookup(Identifier) | Practice Location Number |
| NPI | `PRM_NpiId__r.Npi` | Lookup | Facility NPI |
| Primary | `PRM_Primary__c` | Checkbox | Is primary location |
| Active | `PRM_Active__c` | Checkbox | Is active |
| PNC | `PRM_PNC__c` | Checkbox | Participating Network Contractor |
| Pending | `PRM_Pending__c` | Checkbox | In pending state |
| Practice Classification | `PRM_PracticeClassification__c` | Picklist | Facility, Non-Facility |
| Practitioner Role | `PRM_PractitionerRole__c` | Lookup | Link to practitioner |

---

### HealthcarePractitionerFacility (PPL — Practitioner-Practice Location)

Junction object linking a Practitioner to a Practice Location.

| Field | API Name | Type | Description |
|-------|----------|------|-------------|
| Practitioner | `PractitionerId` | Lookup(Account) | Practitioner account |
| Facility | `HealthcareFacilityId` | Lookup(HealthcareFacility) | Practice location |
| Pending | `PRM_Pending__c` | Checkbox | In pending state |

---

### HealthcareFacilityNetwork (Taxonomy)

Links a practice location to a taxonomy (specialty).

| Field | API Name | Type | Description |
|-------|----------|------|-------------|
| Facility | `HealthcareFacilityId` | Lookup(HealthcareFacility) | Practice location |
| Taxonomy | `PRM_Taxonomy__r.Name` | Lookup | Specialty/taxonomy name |
| Pending | `PRM_Pending__c` | Checkbox | In pending state |

---

### Address (Schema.Address)

Physical addresses for locations.

| Field | API Name | Type | Description |
|-------|----------|------|-------------|
| Parent | `ParentId` | Lookup(Location) | Parent Location record |
| Address Type | `PRM_AddressType__c` | Picklist | Primary, Mailing, Billing |
| Address Line 1 | `PRM_AddressLine1__c` | Text | Street address |
| City | `PRM_City__c` | Text | City |
| State | `PRM_State__c` | Picklist | State (PA, NJ, DE, MD, GA, etc.) |
| Zip | `PRM_Zip__c` | Text | ZIP code |
| Phone | `PRM_Phone__c` | Phone | Location phone |
| Pending | `PRM_Pending__c` | Checkbox | In pending state |

---

### BusinessLicense

Stores licensure information for ancillary facilities.

| Field | API Name | Type | Description |
|-------|----------|------|-------------|
| License Number | `LicenseNumber` | Text | License identifier |
| License State | `PRM_LicenseState__c` | Picklist | Issuing state |
| Effective Date | `PRM_ProviderLicenseEffectiveDate__c` | Date | When license became effective |
| Expiration Date | `PRM_ProviderLicenseExpirationDate__c` | Date | When license expires |
| Status | `PRM_Status__c` | Picklist | Active, Expired, Pending |
| Verified On | `PRM_VerifiedOn__c` | Date | PSV verification date |
| License Class | `PRM_LicenseClass__c` | Picklist | Class of license |
| Healthcare Facility | `PRM_HealthcareFacility__c` | Lookup(HealthcareFacility) | Facility this license belongs to |

---

### Identifier

NPI, Tax ID, and other provider identifiers.

| Field | API Name | Type | Description |
|-------|----------|------|-------------|
| Name | `Name` | Text | Identifier value (NPI number, Tax ID, PL Number) |
| Type | `PRM_IdentifierType__c` | Picklist | NPI, TaxId, PLNumber |
| Pending | `PRM_Pending__c` | Checkbox | In pending state |

---

### Custom Metadata

| Metadata Type | Purpose | Key Fields |
|--------------|---------|-----------|
| `PRM_Quick_Links__mdt` | Quick link URLs for PSV flows | `PRM_URLLink__c`, `PRM_NameIfURLNotPresent__c` |
| `PRM_SendgridTemplateIds__c` | Email template IDs | `PRM_TemplateId__c` |
| `PRM_AsyncJobConfig__mdt` | Async framework routing (one row per batch step) | `PRM_ProcessName__c`, `PRM_ServiceClassName__c` (batch class), `PRM_Mode__c`, `PRM_BatchSize__c`, `PRM_Sequence__c` |

---

## Async Framework Objects (PRM High-Volume Modernization)

> Source: `CLAUDE.md` / `docs/implementation-plan/Epic_A_Environment_Setup.md`.
> These support the async-only Practitioner Creation re-platform. **Verify
> against live org metadata before writing field-level code** — some are new and
> may not yet exist under `force-app/`.

### PRM_AsyncJob__c (process run — parent)

| Field | API Name | Type | Description |
|-------|----------|------|-------------|
| Process Name | `PRM_ProcessName__c` | Picklist | `Practitioner Creation`, `PAR` — routing key |
| Status | `PRM_Status__c` | Picklist | Queued, Running, Completed, Failed |

Auto Number `AJ-{0000000}`. Two Master-Detail children (siblings): Records +
Details. No `PRM_CaseManager__c` on the parent (a run spans many Case Managers).

### PRM_AsyncJobRecords__c (per Case Manager)

| Field | API Name | Type | Description |
|-------|----------|------|-------------|
| Async Job | `PRM_AsyncJob__c` | Master-Detail(PRM_AsyncJob__c) | Cascade delete |
| Case Manager | `PRM_CaseManager__c` | Lookup(IndividualApplication) | The IA (= Case Manager) for one practitioner |

One row per Case Manager, seeded at intake; the CM↔Job correlation the LWC/DLQ
join on. Auto Number `AJR-{0000000}`.

### PRM_AsyncJobDetails__c (per batch step)

| Field | API Name | Type | Description |
|-------|----------|------|-------------|
| Async Job | `PRM_AsyncJob__c` | Master-Detail(PRM_AsyncJob__c) | Cascade delete |
| Process Name | `PRM_ProcessName__c` | Text(255) | Routing key |
| Mode | `PRM_Mode__c` | Picklist | Queueable, Batch |
| Batch Size | `PRM_BatchSize__c` | Number(4,0) | Default 200 |
| Sequence | `PRM_Sequence__c` | Number(3,0) | Step order (chaining, halt-on-failure) |
| Status | `PRM_Status__c` | Picklist | Queued, Running, Completed, Failed |
| Retry Count | `PRM_RetryCount__c` | Number(2,0) | Manual/uncapped retry |

Auto Number `AJD-{0000000}`. One per MDT step (e.g., 5 per job).

### PRM_FailedRecordStaging__c (Dead-Letter Queue — existing, reused)

| Field | API Name | Notes |
|-------|----------|-------|
| Status | `PRM_Status__c` | DLQ status |
| Retry Count | `PRM_RetryCount__c` | |
| Request Payload | `PRM_RequestPayload__c` | |
| Error Message | `PRM_ErrorMessage__c` | |
| Exception Log | `PRM_ExceptionLog__c` | Link to `PRM_ExceptionLog__c` |
| Parent Record Id | `PRM_ParentRecordId__c` | |
| Target Object | `PRM_TargetObject__c` | |
| Source Flow | `PRM_SourceFlow__c` | |
| Case Manager | `PRM_CaseManager__c` | Lookup(IndividualApplication) |
| Async Job Details | `PRM_AsyncJobDetails__c` | Lookup (added for the framework) |

---

## Ancillary Assessment Objects

> Heavily used across the Ancillary Assessment / Re-Assessment / Add Sub-Service
> flows (see `requirements/AncillaryAssessment_*`). Confirm exact field API names
> against live metadata (`code-review-graph` `semantic_search_nodes` or a
> describe) before writing field-level ACs.

| Object | Purpose | Notable Fields (verify) |
|--------|---------|-------------------------|
| `PRM_AncillaryAssessment__c` | The ancillary assessment record | `PRM_Status__c`, `PRM_BillingType__c`, `PRM_PracticeClassification__c`, Case Manager lookup |
| Sub-service records | Sub-services added under an assessment | Effective From/To, provider type/service, active/pending flags |

For Ancillary credentialing, the facility side reuses the core objects above:
`Account` (Vendor), `HealthcareFacility` (practice location), `BusinessLicense`,
`HealthcareProviderNpi`/`Identifier` (NPI, Tax ID), `HealthcareFacilityNetwork`
(taxonomy), and `IndividualApplication` (Case Manager, RecordType `PRM_Ancillary`).

---

## Key Relationships Diagram

```
Account (Vendor/Group)
  └── HealthcareFacility (Practice Location)
        ├── HealthcarePractitionerFacility (PPL) → Account (Practitioner)
        ├── HealthcareFacilityNetwork → Taxonomy
        ├── Address (via Location)
        ├── BusinessLicense
        └── Identifier (PL Number, NPI)

Account (Practitioner)
  ├── IndividualApplication (Case Manager)
  │     └── Case (per stage: App Review, PSV, QC, Committee)
  ├── HealthcareProvider
  │     ├── HealthcareProviderNpi
  │     └── HealthcareProviderTaxonomy
  └── HealthcarePractitionerFacility → HealthcareFacility
```

---

## Credentialing Flow Types

| Flow Type | Record Type | OmniScript Pattern | Description |
|-----------|------------|-------------------|-------------|
| **PAR (Initial Cred)** | PRM_PractitionerParticipationRequest | `PRM_PractitionerParticipationForm_English` | New practitioner application |
| **Off Cycle** | PRM_OffCycleCredentialing | `PRM_OffCycleCredentialing_English` | Mid-cycle credentialing |
| **Recredentialing** | PRM_Recredentialing | `PRM_RecredQC_English` | Periodic renewal |
| **Ancillary** | PRM_Ancillary | `PRM_AncillaryPSVForm_English` | Facility credentialing |
| **Provider Change** | — | `PRM_ProviderChangeForm_English` | Address/info updates |
| **PDM Manual Update** | — | `PRM_PDMManualUpdate_English` | Manual data corrections |
| **Close Case** | — | `PRM_CloseCaseGuidedFlow_English` | Case denial/closure |

---

## Validation & Duplicate Check Patterns

| Validation | Apex / IP | When Used |
|-----------|----------|-----------|
| Duplicate NPI | `PRMDRCheckExistingGroupNPI` | PAR, Off Cycle group selection |
| Termed/Duplicate Account | `PRM_ExistingAccountService.extractExistingAccount` | PAR form |
| Duplicate Address | `PRM_DuplicateAddCheck` IP | PAR, Off Cycle, Add PL |
| Address Verification | `PRM_PreciselyAPIForPARForm`, `PRM_OffCyclePreciselyAPI` | New address entry |
| Overlapping Address | `PRM_AddressTriggerHandler` | Address save |
| Practice Location Validation | `IPValidatePracticeLocation` | PSV Service Area |
| Case Manager Denial Utility | `PRM_CaseManagerDenialUtility` | Close Case |
