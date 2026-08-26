# Persona & AC Authoring Contract + AC Pattern Library

The two non-negotiables for every generated story: a concrete business-role
persona, and acceptance criteria written in business language using one of four
patterns. This file is the authoritative detail for both; `SKILL.md` summarizes
and links here.

## Contents

- Persona rule (concrete business role) + Workspace Persona Cheatsheet
- Given / When / Then contract (Pattern A rules + right/wrong examples)
- AC Pattern Library: Pattern A (behavioural), B (field/object/metadata),
  C (permission set / FLS), D (field update rules), E (record & field specification)
- "When in doubt" pattern-selection guide

---

## A) Persona must be a real, concrete business role

| Don't write | Write instead |
|---|---|
| "As a business user" | "As an **Ancillary Cred Specialist**" (for the PNM Ancillary flow) |
| "As a user" | "As a **Credentialing Specialist**" / "**PDM Specialist**" / etc. |
| "As a developer / business analyst" | If the story is a developer-facing spec, split it: keep the business persona at the top, and put the developer-facing rules into the Technical Implementation section. |
| "As a data steward" | "As an **Ancillary Cred Specialist** (acting as data steward)" |

For US-stories whose *consumer* really is a developer (e.g., merge-rule
contracts, internal Apex helpers), keep the business persona on the header and
use the Technical Implementation section to describe the developer contract —
the user-facing story line must still be from the business role's perspective
("So that **my** submission cannot silently destroy data I captured earlier").

### Workspace Persona Cheatsheet (PNM)

Detected on first run by scanning `requirements/` and `permissionsets/` for role
labels. Current canonical list for this workspace:

| Flow / Context | Persona to use |
|---|---|
| Ancillary Assessment / Re-Assessment / Add Sub-Service | **Ancillary Cred Specialist** |
| HACAC Committee Review | **Ancillary Cred Specialist** (HACAC committee member) |
| Practitioner initial credentialing | **Credentialing Specialist** |
| Practitioner re-credentialing | **Credentialing Specialist** |
| Provider Data Management (Account / Practitioner updates) | **PDM Specialist** |
| Network management QC | **Network Management QC Specialist** |
| PAR / Off-cycle | **Credentialing Specialist** |

If the user names a persona that isn't in the cheatsheet, accept it verbatim and
add it to the story header. If the workspace later proves the canonical name is
different, prefer the workspace's term over the user's casual term.

---

## B) Acceptance Criteria — Given / When / Then is mandatory

Every behavioural AC is **three explicit lines**, not a prose paragraph:

```
**AC-N — Short title**

**Given** [precondition / state before the action — be specific about objects, fields, picklist values, RecordTypes, account state]
**When** [the single trigger / action — usually one user action]
**Then** [the observable, verifiable outcome — record changes, field values, error messages, UI behavior]
**And** [optional additional outcomes, one per line]
```

Hard rules:

- One **When** per AC. If you have two actions, split into two ACs.
- The **Then** must be observable and checkable (QA can query, click, or read a
  log to confirm it). "It works" is not a valid Then.
- Use `**And**` lines for compound outcomes, not commas inside Then.
- Keep verbs in business language; implementation details belong in the
  Technical Implementation section.
- Edge cases get their own AC (Given = the edge state; Then = the
  rejection / fallback / log entry).
- If you write more than ~6 lines under a single Then, split the AC — long ACs
  are a smell that two scenarios got merged.

**Example — wrong (prose with technical jargon):**

> AC-1.1 When the form's Submit action fires, `PRM_AncillaryFormRecordsCreation_Procedure_19` calls `PRM_AncillaryFormContextResolver.resolveContext(...)` before any record creation step.

**Example — wrong (GWT but stuffed with implementation noise):**

```
**Given** an Ancillary Cred Specialist is on the Submit step of
`PRM_AncillaryProviderForm_English_38` with a valid `accountId` ...,
**When** the parent IP `PRM_AncillaryFormRecordsCreationParent_Procedure_3`
invokes the child `PRM_AncillaryFormRecordsCreation_Procedure_19`,
**Then** the first executed step is the Apex Action
`PRM_AncillaryFormContextResolver.resolveContext(...)` ...
```

**Example — right (GWT in pure business language):**

```
**AC-1.1 — System auto-routes additional Ancillary submissions**

**Given** an Ancillary Cred Specialist submits the Ancillary form for a vendor
that already has at least one Case Manager (in-flight or approved) on file,
**When** they click Submit on the Provider Form,
**Then** the system silently determines whether to reuse the existing Case
Manager, create a new Case Manager alongside it, or block the submission,
**And** no record is created or modified until that routing decision is made,
**And** the Ancillary Cred Specialist is never asked a routing question.
```

The implementation details (resolver class name, IP step numbers, SOQL queries)
move to the story's Technical Implementation (high-level) section.

---

## AC Pattern Library

Every AC uses ONE of four patterns. Pick the pattern that matches what the AC is
asserting; don't force a GWT shape on a metadata-spec AC.

### Pattern A — Behavioural AC (Given / When / Then) — DEFAULT

Use for: anything that asserts **system behaviour** the persona can observe — a
record gets created, a field gets updated, an error is shown, a Chatter post
fires, a routing decision happens.

```
**AC-N — Short business-language title**

**Given** [persona + business state, no API names, no class names]
**When** [single business action]
**Then** [observable business outcome — what the persona sees, what business records change in business terms]
**And** [optional additional outcomes, one per line]
```

Keep the verbs in business language. Say "the Case Manager is reused", not
"`existingCaseManagerId` is reused". Say "a note is added to the Case Manager's
Chatter feed", not "a `FeedItem` is inserted with `ParentId = existingCaseManagerId`".

### Pattern B — Field / Object / Metadata Creation

Use for: new custom fields, new custom objects, new Custom Metadata Types, new
field history tracking, new picklist values. These are inherently technical-spec
ACs — bullet structure is required, GWT is not.

```
**AC-N — Create following fields on [Object Label]**

- **API Name:** PRM_XxxYyy__c
- **Object:** [Salesforce object label / API name]
- **Type:** Checkbox / Text(80) / Lookup(Target) / Picklist / Master-Detail / etc.
- **Label:** [User-facing label]
- **Default:** [optional]
- **Help text:** [optional, customer-facing]
- **Description:** [optional, admin-facing]
- **Track History:** true / false
- **Required:** true / false (where applicable)
```

For new objects, add: Plural label, Sharing model, Auto-Number / Name format,
and a sub-list of fields using the same bullet style.

For new Custom Metadata Types, add: a Seed-rows bullet describing how many rows
should be created and what governs the count (e.g., "one per queryable custom
field on PRM_AncillaryAssessment__c").

### Pattern C — Permission Set / FLS

Use for: permission set updates, profile FLS, OWD changes, sharing rules.

```
**AC-N — Field Access & Permission Sets**

- **PRM_DataModifyAll:**
  - Object level: Read, Create, Edit, View All Records
  - Field level: Read and Edit on all available fields
- **PRM_DataViewAll, PRM_NetworkManagementQC:**
  - Object level: Read, View All Records
  - Field level: Read on all available fields
- **PRM_ProviderDataAdmin, PRM_CredentialingUser:**
  - Object level: Read, Create, Edit
  - Field level: Read on all available fields
```

If only one permission set is affected and only one field is changing, you may
collapse into a single bullet, but keep the Object-level / Field-level split.

### Pattern D — Field Update Rules (business calculation tables)

Use for: ACs that describe **how** a value is computed when many conditional
branches feed it. Often appears inside the Then of a Pattern A AC, or as a
standalone "update rules" supporting block.

```
**AC-N — Update following records on [Object]**

**Given** [precondition],
**When** [action],
**Then** the following fields are set per the rules below:

- **Effective From =**
  - When Inactive -> {Effective Date of Change}
  - When Active & New Effective Date of Change < Current Effective From -> {Effective Date of Change}
  - Else -> Current Effective From
- **Effective To =**
  - If Effective To added in the guided flow and Inactive -> {New Effective To}
  - If Effective To added in the guided flow and Active and New Effective To > Current Effective To -> {New Effective To}
  - If Effective To not added in the guided flow -> NULL
- **Active =**
  - If Effective From <= TODAY & Effective To > TODAY -> Active
  - If Effective To = NULL -> If Effective From <= TODAY -> Active; Else -> Inactive
- **Pending = FALSE**
- **Is Error Record = FALSE**
- **Case Manager = Case Manager**
```

This pattern is preferred over cramming six "And" lines into a single Then.

### Pattern E — Record & Field Specification (post-action record recipe) — MANDATORY when records are created/updated

Use for: any story where a submit, batch run, flow completion, or trigger
**creates or updates records** and the business team needs to see the *exact
recipe* — every object, every field, and the exact value (or formula) each field
is set to. This is the "developer-buildable record spec" the screenshot-style
requirements demand: one block **per object**, listing **every field** so a
developer can build the record write without a follow-up meeting and QA can
assert every field.

**Why this pattern is mandatory:** a Pattern-A AC says *"the Case Manager is
completed"* in business language, but it does **not** tell the developer that
`Stage = Complete`, `Status = Approved`, `Decision Date = TODAY`, etc. Whenever
an AC's outcome is *"records are created/updated"*, you MUST pair it with a
Pattern E block that enumerates the fields. Never leave the field-level recipe
implied.

**Structure — one sub-block per object, in creation/update order (parents before children):**

```
**AC-N — Records created/updated on <trigger> (outcome = <branch>)**

**Given** [precondition / which branch this recipe applies to],
**When** [the single trigger — Submit / Done / batch run / button click],
**Then** the following records are created/updated exactly as specified:

**<Object 1 — business label> — [Create | Update]**

| Field | Value | Notes |
|---|---|---|
| Record Type | Professional Staff Verification | new / existing |
| Status | New | |
| Stage | Professional Staff Verification | |
| Applied Date | {Current date/time} | |
| Account | {Practitioner} | lookup |
| Owner | Professional Staff Verification Queue | round-robin assignment |
| ... every remaining field ... | ... | ... |

**<Object 2 — business label> — [Create | Update]**

| Field | Value | Notes |
|---|---|---|
| ... | ... | ... |
```

Hard rules for Pattern E:

- **List EVERY field** the record write touches — do not abbreviate with "etc."
  or "and other fields". If a field is intentionally left unchanged, don't list
  it; if it is set, it must appear.
- **One table per object.** Order objects the way they're written (parents
  before children) so the developer can follow the DML order.
- **Value column** holds the literal value, a `{merge/source}` placeholder in
  curly braces (e.g. `{Practitioner}`, `{TODAY}`, `{Termination Date}`), or a
  short formula. For multi-branch computed fields (Effective To / Active), nest
  the Pattern D rules inside the Value cell or link to the Pattern D block.
- Use **business field labels** (e.g. "Re-Cred Due Date", "Decision Date"), not
  API names — the API-name mapping lives in the Technical Implementation table.
- If the same trigger produces **different recipes per branch** (e.g. Verification
  Complete vs. Manager Review vs. Termination), give **each branch its own
  Pattern E AC** so QA can test each outcome independently.
- A "Create a Note" instruction is a record write — spec it as its own object
  block with Note Title and Note Body fields.

**Example — right (screenshot-style, every field enumerated):**

```
**AC-4 — Records updated on Done (outcome = Verification Complete)**

**Given** a Credentialing Specialist completed the verification with outcome
"Verification Complete",
**When** they click Done,
**Then** the following records are updated exactly as specified:

**Case Manager — Update**

| Field | Value | Notes |
|---|---|---|
| Stage | Complete | |
| Status | Approved | |
| Decision Date | {TODAY} | |
| Professional Staff Verification Outcome | Verification Complete | |

**Case — Update**

| Field | Value | Notes |
|---|---|---|
| Status | Closed | |

**Note — Create**

| Field | Value | Notes |
|---|---|---|
| Title | Professional Staff Verification Complete | |
| Body | {Note Body} | from the flow |
```

### When in doubt

- A field, object, metadata type, or perm set is being **created or changed** (its *definition*) -> Pattern B or C (structured bullets).
- The persona observes **behaviour** of the system -> Pattern A (GWT).
- A computation has **many conditional branches** that map to a single business outcome -> Pattern D (rules block).
- A submit / Done / batch / trigger **creates or updates record data** and you need the exact per-field recipe -> Pattern E (record & field specification). **Always pair Pattern E with the Pattern A AC that describes the same action in business language.**

See `references/story-examples.md` for worked exemplars (Patterns A–D).
