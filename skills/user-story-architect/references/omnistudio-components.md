# OmniStudio Component Reference

## Contents

- Component Types (OmniScript, FlexCard, DataRaptor, IP, DataMapper, Decision Matrix)
- OmniScript Element Types
- OmniScript JSON Structure
- DataRaptor Patterns (Extract / Transform / Load / Turbo)
- Integration Procedure Patterns + IP element types
- Naming Conventions by Vertical (PNM, HLS, Insurance)

---

## Component Types

| Component | What It Is | When to Use | Runtime |
|-----------|-----------|-------------|---------|
| **OmniScript** | Multi-step guided UI flow | User-facing data collection, wizards, guided processes | Client-side (LWC) |
| **FlexCard** | Data display component (card/tile/layout) | Record display, dashboards, summary views, embedded in OmniScript | Client-side (LWC) |
| **DataRaptor Extract** | Read data from Salesforce objects | Fetch records for display in OmniScript/FlexCard | Server-side |
| **DataRaptor Transform** | Reshape JSON data | Transform data between components without DML | Server-side |
| **DataRaptor Load** | Write data to Salesforce objects | Create/Update/Upsert records from OmniScript or IP | Server-side |
| **Integration Procedure (IP)** | Server-side orchestration engine | Chain DataRaptors, Apex, HTTP callouts, matrices | Server-side |
| **DataMapper** | Declarative field-to-field transformation | Map fields between source/target schemas | Server-side |
| **Decision Matrix** | Lookup/rule table | Business rules, pricing, conditional routing | Server-side |

---

## OmniScript Element Types

| Element Type | Purpose | Key Properties | Example |
|-------------|---------|----------------|---------|
| **Step** | Container grouping form elements | `name`, child elements, conditions | `ServiceAreaVerificationStep` |
| **Text Block** | Display-only text/HTML | `text`, `textHTML`, conditions | `TextBlockCa` |
| **Type Ahead** | Autocomplete search input | `dataSource`, `minChars`, `displayField` | `HCFTypeAhead` |
| **Select** | Dropdown/picklist | `options[]`, `optionSource`, `defaultValue` | `PractitionerState` |
| **Radio** | Radio button group | `options[]`, `layout` | `PlQuestion` |
| **Checkbox** | Boolean toggle | `defaultValue`, conditions | `CBPNCCkd` |
| **Text** | Text input field | `validation`, `mask`, `readOnly` | `DEAState` |
| **Email** | Email input | `validation` | — |
| **Date** | Date picker | `format`, `min`, `max` | `PRM_Decision_Date__c` |
| **Edit Block** | Table/grid of records | `selectSobject`, `sobjectMapping`, `allowNew` | `VerifyLicensureBusinessLicense` |
| **Set Values** | Assign data to the OmniScript JSON | `ElementValueMap` key-value pairs | `SV_PNC` |
| **DataRaptor Post Action** | Save data via DataRaptor Load | `DRName`, `inputMap`, `bundle` | `DRUpdateHealthcareFacilityPNC` |
| **IP Action** | Invoke an Integration Procedure | `IPName`, `inputMap`, `responseMap` | `IPCreatePDMRecords` |
| **Remote Action** | Call Apex method | `className`, `methodName`, `inputMap` | `IPValidatePracticeLocation` |
| **Navigate Action** | Redirect on completion | `targetType`, `targetId`, `URL` | `NavigateToCaseManager` |
| **Conditional** | Show/hide logic | `show` expression, element references | `show: IsRecredentialing = true` |
| **Embedded OmniScript** | Nest another OmniScript | `Type`, `SubType`, `Language` | `ProviderChangeFormCapitationSite` |
| **Repeat** | Repeatable block of elements | `maxRepeat`, child elements | `PLRecredBlock` (max 4) |
| **Custom LWC** | Embedded Lightning Web Component | `lwcName`, `properties` | `prmDisplayQuickLinks` |
| **Formula** | Calculated value | `expression`, dependencies | — |
| **Aggregate** | Summarize repeated data | `aggregateFunction`, `sourceField` | — |

---

## OmniScript JSON Structure

Each OmniScript element is stored as a JSON file in the force-app directory:

```
force-app/main/default/omniScripts/
  [Type]_[SubType]_[Language]/
    [Type]_[SubType]_[Language].json           # Main definition
    [Type]_[SubType]_[Language]_Element_[Name].json  # Per-element
```

Key fields in element JSON:
- `propertySetConfig.options` — picklist/radio options array
- `propertySetConfig.show` — visibility condition expression
- `propertySetConfig.optionSource` — dynamic option source (Salesforce picklist)
- `propertySetConfig.readOnly` — whether element is editable
- `propertySetConfig.dataRaptorPostActionInput` — DR Post Action mapping
- `propertySetConfig.HTMLTemplateId` — FlexCard/template reference

---

## DataRaptor Patterns

| Type | Naming Convention (PNM) | Purpose | Key Config |
|------|------------------------|---------|-----------|
| **Extract** | `PRMDRExtract[Object][Context]` | Read from Salesforce | SObject, Fields, Filters, Output JSON path |
| **Transform** | `PRMDR[Transform][Purpose]` | Reshape JSON | Input path, Output path, Formula |
| **Load** | `PRMDRUpdate[Object][Context]` | Write to Salesforce | SObject, Fields, Upsert key, Input mapping |
| **Turbo Extract** | `PRMDRExtract[Object]Turbo` | High-performance read | Same as Extract, optimized |

### DataRaptor Extract Config
- **SObject:** The Salesforce object to query
- **Fields:** Which fields to return
- **Filter:** WHERE conditions (field, operator, value, merge field)
- **Relationship:** Child/Parent joins
- **Output:** JSON output path mapping (e.g., `Facility:Account.PRM_PNC__c`)

### DataRaptor Load Config
- **SObject:** Target object
- **Fields:** Input JSON path → Salesforce field mapping
- **Upsert Key:** External ID or record ID for upsert
- **Input Mapping:** How OmniScript JSON maps to DR input

---

## Integration Procedure Patterns

| Pattern | Example | Description |
|---------|---------|-------------|
| **Parent → Child** | `PRM_FetchDetailsParent` → `PRM_FetchDetails` | Parent IP orchestrates, child does work |
| **Chained DRs** | IP with DR Extract → DR Transform → DR Load | Read, transform, write in sequence |
| **Conditional Execution** | `execution condition: PDMManualUpdateType = "Add/Remove PNC"` | Element runs only when condition met |
| **Response Action** | `%DRExtractResult:FieldPath%` | Map DR output to IP response |
| **Remote Action** | Apex class call within IP | Complex logic not possible in DR |

### IP Element Types (inside Integration Procedure)
- **DataRaptor Extract/Load/Transform/Turbo** — DR invocations
- **Remote Action** — Apex method call
- **HTTP Action** — External API callout
- **Decision Matrix Action** — Lookup from matrix
- **Set Values** — Assign constants or merge fields
- **Loop** — Iterate over list
- **Conditional Block** — Branch logic
- **Response Action** — Shape the IP output

---

## Naming Conventions by Vertical

### PNM (Provider Network Management)

| Component | Pattern | Example |
|-----------|---------|---------|
| OmniScript | `PRM_[FlowName]_English` | `PRM_ProviderChangeForm_English` |
| DataRaptor | `PRMDR[Action][Object]` | `PRMDRUpdateAccountPDM` |
| Integration Procedure | `PRM_[Name]` | `PRM_PDMRecordsCreation` |
| Parent IP | `PRM_[Name]Parent` | `PRM_FetchDetailsParent` |
| LWC Override | `prm[ComponentName]` | `prmDisplayQuickLinks` |
| Custom Metadata | `PRM_[Name]__mdt` | `PRM_Quick_Links__mdt` |
| Custom Field | `PRM_[FieldName]__c` | `PRM_PNC__c` |
| Set Values Element | `SV_[Name]` | `SV_PNC` |
| IP Action Element | `IP[Name]` | `IPCreatePDMRecords` |

### HLS (Health & Life Sciences)

| Component | Pattern | Example |
|-----------|---------|---------|
| OmniScript | `HLS_[FlowName]_English` | `HLS_PatientIntake_English` |
| DataRaptor | `HLSDR[Action][Object]` | `HLSDRExtractCarePlan` |
| Integration Procedure | `HLS_[Name]` | `HLS_CareProgEnrollment` |

### Insurance

| Component | Pattern | Example |
|-----------|---------|---------|
| OmniScript | `INS_[FlowName]_English` | `INS_QuoteCreation_English` |
| DataRaptor | `INSDR[Action][Object]` | `INSDRExtractPolicy` |
| Integration Procedure | `INS_[Name]` | `INS_RatingProcedure` |
