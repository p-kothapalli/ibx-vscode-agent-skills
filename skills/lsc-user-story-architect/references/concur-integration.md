# SAP Concur ⇄ LSC Expense Integration Reference

Grounding for stories about the **SAP Concur expense integration** in LSC4CE
(Life Sciences Cloud for Customer Engagement). It covers **two surfaces**:

- **Visit Expenses** (releases 260/264/266; **Summer '26** release enablement) — field-rep visit spend.
- **Event / Managed Events Expenses** (release 264, "EM: Expense Management") —
  event-organizer event/meeting spend, incl. **Estimated Expense Allocation to
  Participants**.

Load this whenever a story touches expenses, expense reports, visit/event spend,
Concur sync, expense allocation, or the MuleSoft expense connector. **Verify exact
object/field API names via `salesforce-docs`** — this file is a domain map, not a
substitute for verification, and this IBXQA workspace is a PNM org where
LSC/Concur metadata may not be deployed.

## Contents

- What it is + architecture (MuleSoft connector, bidirectional + scheduled sync)
- Personas
- Data model (Visit/Event → Expense → Expense Report Entry → Expense Report; allocations; IntegrationJobRun; sync-status fields)
- Sync-status model + edit matrix
- Actual vs Estimated expenses (Event-specific)
- Core business rules (create / modify / delete / delink)
- Sync directionality rules (incl. reverse-sync-on-delete)
- Platform, offline & attachment rules
- MuleSoft integration configuration (admin)
- Estimated Expense Allocation to Participants (Event epic)
- Admin configuration (Concur Settings tile — 264/266)
- System of record evolution
- Authoring guidance + worked mini-examples
- Reference links

---

## What it is + architecture

Field users manage expenses tied to **HCP Visits** (field reps) or **Managed
Events / meetings** (event organizers) without leaving LSC. It parallels IQVIA
OCE-P "Concur Integration for Call Expenses" but is adapted to the LSC data model.

- **Bidirectional sync** via a **1st-party MuleSoft connector** ("LSC Concur
  Expense Sync", a MuleSoft Direct integration app) — NOT hand-rolled Apex callouts.
- **Forward sync (LSC → Concur):** pushes LSC expense reports + expenses (+ their
  attendees/receipts) to Concur; only records with the configured integration
  status (e.g. `Pending`) are picked up.
- **Reverse sync (Concur → LSC):** monitors Concur for modifications/deletions
  and updates the mapped LSC records.
- **Scheduled batch sync (Events, 264):** on a configurable frequency, MuleSoft
  **retrieves open/unsubmitted expense reports from Concur** and creates/updates
  them in LSC (Concur trending toward the system of record — see below).
- Sync is **asynchronous/batch**; errors are handled in the **integration
  layer**, not shown to field end users (they see sync status, not raw errors).

## Personas

| Persona | Job to be done |
|---|---|
| **Field Sales Representative** (primary, Visits) | Create/submit expenses incurred during HCP visits |
| **Key Account Manager (KAM)** | Create/submit expenses incurred during client visits |
| **Medical Science Liaison (MSL)** | Create/submit expenses incurred during visits with influential HCPs |
| **Event Organizer** (primary, Events) | Link actual event expenses to Concur reports; allocate estimated expenses to participants |
| **LSC Admin** | Define Concur Settings (status mappings), enable/disable report-linking, configure allocation rules |
| **MuleSoft Admin** | Configure connection params, field mappings, retry/rate-limit policy, schedule + manually trigger sync jobs |

HCPs are the **subjects** of the visit/event, never the login persona.

## Data model

> Standard LSC4CE expense objects. Verify exact API names via `salesforce-docs`.

| Object (business term) | Purpose | Notes |
|---|---|---|
| **Visit** | Parent record for a field interaction | Has an "Expenses" tab (LSC4CE 258+) |
| **Event / Meeting (Managed Event)** | Parent record for an event/meeting | Event Expenses component; actual + estimated expenses |
| **Expense** (`ExpenseEntry`) | A single expense line (meal, travel, honoraria) | `ExpenseSystemIntegrationStatus` drives sync |
| **Expense Type** | Classifies an expense (meal, travel, etc.) | Carries the estimated-allocation **Distribution Type** (All/Individual/Multiple/N-A) |
| **Expense Report** | Grouping of expenses submitted together in Concur | Maps 1:1 to a Concur report |
| **Expense Report Entry** | **Junction** linking an Expense to an Expense Report | The link is a junction record, NOT a field on Expense (per LSC data model) |
| **Expense Participant** | Attendee/participant allocation of an expense | The object for attendee allocations (split of an expense across participants) |
| **IntegrationJobRun** | Stores each MuleSoft job run (name, timestamp, status, processed count) | Monitoring/audit of sync jobs |
| **Expense System Integration Status** | Sync-state field on **Expense** AND **Expense Report** | Introduced in 260 |

> **Supported Expense-management object schema** (what admins configure for the
> integration, per the Summer '26 enablement): **Expense, Expense Type, Expense
> Participant, Expense Report, Expense Report Entry.**

Key relationships: **Visit/Event → Expense**; **Expense ↔ Expense Report** via the
**Expense Report Entry** junction; **Expense → Expense Participant** allocations.
LSC↔Concur objects correlate by a **1:1 mapping** (LSC `ER1`↔Concur `CR1`,
`E1`↔`CE1`). The MuleSoft forward sync carries **four payload types**: expense
reports, expense entries, **attendee allocations (Expense Participant)**, and
receipts.

## Sync-status model + edit matrix

**Expense System Integration Status** values: `Pending` (eligible / not yet
synced — "Ready to Send"), `In Progress` (syncing), `Completed`, `Failure`,
`Error`, `Deleted`.

**Expense Report Status** values: `Not Submitted`, `Submitted`, `In Review`,
`Approved`, `Rejected`, `Deleted`.

Whether a user can edit expenses from the UI (drives most edit/delete/delink ACs):

| Integration Status | Report Status | User can edit? |
|---|---|---|
| Pending (not yet synced) | N/A | Yes |
| In Progress (syncing) | N/A | **No** |
| Completed | Not Submitted | Yes |
| Failure | N/A | Yes |
| Error | N/A | Yes |
| Deleted (deleted in Concur) | Deleted | N/A |
| N/A | Submitted | **No** |
| N/A | In Review | **No** |
| N/A | Approved | **No** |
| N/A | Rejected | Yes |

Setting `ExpenseSystemIntegrationStatus = Pending` ("Ready to Send") is what makes
the MuleSoft job pick up an expense — used both for **new** expenses and to
**re-sync** a modified/failed expense.

## Actual vs Estimated expenses (Event-specific)

- **Actual expenses** — real spend; **can be linked to a Concur Expense Report**
  and synced. The Expense Report field/picklist is available **only** for actual
  expenses.
- **Estimated (planned) expenses** — budget/planned spend; **NOT** linked to
  Concur and **not** synced. Estimated expenses are what get **allocated to
  participants** (see the allocation epic).

## Core business rules

**Creation**
- Visit expenses: created only for a **"Planned"** Visit ("Completed" = read-only).
- Post-260 GA (Visits): a new visit expense requires **mandatory association with
  an Expense Report** (enforced at the Expense UI component level, Visits only).
- Expenses can be linked **only to expense reports not yet submitted in Concur**.
- Event: when adding an **actual** expense, the user selects an **unsubmitted
  Concur expense report** (only the user's own open/unsubmitted reports; one
  report per expense). If none exist, the picklist is empty with a message.

**Modification / re-sync**
- Cannot modify while **In Progress** (syncing); allowed after sync completes.
- Event: an expense already sent to Concur can be updated **only if its report is
  still `open`/`unsubmitted`**; the update is **queued for re-sync** (next batch).
  Multiple edits before the next run collapse into a **single** queued update.
- Cannot modify once the report is **Submitted / Paid / Approved** (final states).
- **Allocation rule:** need not allocate the full amount, but **cannot allocate
  more than the total**; when editing, the expense amount **cannot be less than
  the sum of allocations** (reduce allocations first).

**Deletion**
- Delete only **unsynchronized** expenses (Visits: Planned visit only). Deleting
  an allocated unsynced expense also deletes its allocation records.
- To delete a **synced** expense, delete it **in Concur first** → deletion
  reverse-syncs and the LSC expense is removed.
- **Expense Report deletion (Web only):** cannot delete a report that is **linked
  to expenses** or **submitted in Concur**.

**Delink (Event, status-driven)**
- Modify/remove the linked Concur report **only** when Expense Integration Status
  = **`Pending`** (before sync). Then the user may pick a different unsubmitted
  report or remove the link entirely and save.
- Delinking is **blocked** once Integration Status = `Completed` (regardless of
  report status), and also when status = `Failure`/`Error`, or report status =
  `Deleted`/`Submitted`/`InReview`/`Approved`/`Rejected`.

## Sync directionality rules (LSC ↔ Concur)

- New expenses created **directly in Concur** (not from LSC) are **NOT** synced to LSC.
- Attaching a synced LSC expense to a **different Concur report with no LSC
  mapping** → a **new Expense Report is created in LSC** on the next sync.
- New Concur reports **not attached** to any synced LSC expense are **not** synced.
- Deletions in Concur of **mapped** items reverse-sync; **unmapped** items do not.
- **Reverse-sync on delete (264 change):** when an expense is deleted in Concur,
  LSC **preserves the Expense record** and removes **only the link** (the
  **Expense Report Entry** junction), clearing the integration data on the Expense
  (rather than deleting the Expense outright).
- **Attachment/receipt changes made in Concur do NOT reverse-sync to LSC.**
- **Atomicity:** sync is **not** atomic per expense — Concur is micro-service
  based (report API, then per-expense API, then attendee + receipt APIs). If the
  receipt call fails, the synced expense is **not rolled back**; the Expense is
  marked `Error` in LSC. Sync error details are captured at **Expense** and
  **Expense Report** level (attendee/receipt failures roll up to Expense level).

## Platform, offline & attachment rules

- **Platforms:** iPad (mobile) and Web; some actions are Web-only (Expense Report
  deletion; adding multiple attachments to an existing expense). Offline Mobile is
  the primary end-user surface for Events.
- **Offline:** expenses can be created **offline** (iPad); sent to Core when back
  online, then synced to Concur.
- **Attachments:** the current Concur Expense Sync app supports files **up to
  1 MB**; supported formats **PNG, JPG, JPEG, PDF**; files are sent in original
  format (no conversion). iPad allows **one** attachment on a newly created
  expense and **cannot** attach to an existing expense; Web allows **one or more**
  on existing expenses. (Early Visit PRD cited 6MB; the shipped app limit is 1MB —
  confirm the target org's limit.)

## MuleSoft integration configuration (admin)

- **Connection:** MuleSoft endpoint + auth via Salesforce **Named Credentials**;
  Concur API endpoint, client ID/secret, OAuth scopes configured in MuleSoft;
  end-to-end connection test (Salesforce → MuleSoft → Concur).
- **Retry policy:** max retry count (default **3**), retry interval (default
  **30 s**), exponential backoff multiplier (default **2x**).
- **Batch:** default **10 expense reports per iteration** (e.g. 25 reports → 3
  batches); configurable by a MuleSoft admin.
- **Field mappings (MuleSoft):** e.g. Amount → Concur `TransactionAmount`,
  Expense Category → `ExpenseTypeCode`, Attendee Name → `Attendee`, Allocation
  Amount → `AttendeeAmount`. Editing mappings requires a MuleSoft developer; no
  versioning/rollback today.
- **Rate limiting:** configurable max API calls/minute (aligned to the org's
  Concur quota); **priority queue** so user-initiated sends beat batch background
  sends; auto-throttle batch while allowing interactive ops near the limit.
- **Manual trigger:** authorized admins can run the sync job on demand outside
  the schedule; each run creates an **IntegrationJobRun**; duplicate concurrent
  runs are prevented/queued.
- **Monitoring:** IntegrationJobRun stores job name, run timestamp, status,
  processed record count; full request/response logs live in the MuleSoft app.

## Estimated Expense Allocation to Participants (Event epic)

Distribute **estimated** event expenses across participants (HCP attendees,
speakers, colleagues, write-ins, non-profiled attendees) for spend tracking,
cap enforcement, and compliance.

- **Distribution types (set on the Expense Type by admin):**
  - **All** — auto-evenly across all eligible participants (no manual selection)
  - **Individual** — entire amount to one participant
  - **Multiple** — even OR uneven across selected participants
  - **Not Applicable** — event-level only; not allocatable to participants
- **Participant eligibility (admin-configured):** by participant type and by
  **Invitation Status** (default eligible: No Response, Tentative, Accepted).
- **Even allocation:** system splits equally; on participant add/remove it
  **auto-redistributes**; user can't manually edit amounts in even mode.
- **Uneven allocation** (only if admin-enabled, only for `Multiple` type): manual
  per-participant amounts; total must equal the expense amount to save.
- **Reallocation on change:** removing a participant flags the expense **Needs
  Reallocation** (partial) or **Not Allocated** (full); a **Reallocate** action
  redistributes (even mode only). Allocations must be removed **before** a
  participant can be removed (FK constraint).
- **Controls:** configurable rounding rules, partial-allocation permission, and
  **spend caps** (overages flagged/logged).

## Admin configuration (Concur Settings tile — 264/266)

A **Concur Settings** tile in the LSC Commercial Admin Console (GA 264, Winter '27)
lets admins define **custom values** (instead of hardcoded) that the MuleSoft
connector uses — aligned between **LSC and MuleSoft**:

- `Expense.ExpenseSystemIntegrationStatus` (which status makes an expense eligible for sync)
- `ExpenseReport.ExpenseSystemIntegrationStatus`
- `ExpenseReport.Status`

Applies to both **Visit** and **Managed Events** expenses. Admins can also
enable/disable the ability for reps/organizers to link Concur reports to expenses
(consistent across web + mobile, config-only). Epic 266 makes the connector read
these admin-defined values with no regression.

**Visit admin setup sequence** (Summer '26 enablement, maps to the Help articles):
1. Enable **"Concur Expense Sync"** via the Built-In MuleSoft Integration.
2. **Set up Expense Management for Concur Integration:**
   - a. Add the **Expense tab** to the Visit page.
   - b. Create **Expense Types** for expense classification.
   - c. Define **permissions** to manage expenses on iPad.
   - d. Configure the **object schema** for the supported Expense-management
     objects (**Expense, Expense Type, Expense Participant, Expense Report,
     Expense Report Entry**).
   - e. **Generate a metadata cache** so iPad picks up the latest metadata.

## System of record evolution

- **Today:** CRM (LSC) is the system of record for expense reports — the user
  creates the report in LSC, links expenses, forward-sync pushes to Concur.
- **Ideal (264+):** **Concur** becomes the system of record — a scheduled MuleSoft
  job pulls open/unsubmitted Concur reports into LSC as mappings, and users link
  visit/event expenses to those pre-created reports.

## Authoring guidance for Concur stories

- **Pick the surface:** Visit expenses (Field Rep/KAM/MSL) vs Event expenses
  (Event Organizer). They share the sync model but differ in parent record,
  actual/estimated split, and allocation.
- **Persona:** the field/event user for expense actions; **LSC Admin** for Concur
  Settings/linking toggles; **MuleSoft Admin** for connection/mapping/schedule.
  Never "user"; HCP is the subject.
- **Add a Platform axis** (iPad, Web, Offline) — behavior differs by platform.
- **Status-driven ACs:** edit/delete/delink rules key off the Integration Status
  + Report Status edit matrix — write a separate Pattern A AC per relevant state
  (locked while In Progress; view-only after Submitted; delink only while Pending).
- **Pattern E for every record write:** an expense create/link/allocate, a status
  flip to Pending ("Ready to Send"), or a reverse-sync delete is a record write —
  enumerate Expense, Expense Type, Expense Report, **Expense Report Entry**
  (junction), and **Expense Participant** (attendee allocation) fields (incl.
  `ExpenseSystemIntegrationStatus`).
- **Model the link as the junction:** linking/delinking creates/deletes an
  **Expense Report Entry**, it is not a lookup edit on Expense.
- **Edge cases to always cover:** syncing lock; submitted/paid lock; delete-in-
  Concur-first; delink-only-while-Pending; reverse-sync delete preserves Expense
  and clears integration data; offline create→sync; 1MB / png,jpg,jpeg,pdf /
  single-attachment-on-iPad; allocation-exceeds-total; needs-reallocation on
  participant removal.
- **Integration is MuleSoft, not Apex** — name the "LSC Concur Expense Sync"
  connector, forward/reverse jobs, IntegrationJobRun, Named Credentials, retry/
  batch/rate-limit config in Technical Implementation, not in the ACs.
- **Errors are not shown to field users** — don't write end-user error ACs; route
  error handling to the integration layer / admin monitoring (IntegrationJobRun).

## Worked mini-examples (abridged — full format per `output-template.md`)

**Visit — Field Sales Representative (iPad, Web)**

**AC — Expense locked while syncing (edge case)**
**Given** a visit expense whose sync with Concur is **In Progress**,
**When** the rep tries to modify or delete it,
**Then** the action is blocked until the sync completes.

**Event — Event Organizer (Web, Offline Mobile)**

**AC — Delink allowed only before sync (edge case)**
**Given** an actual event expense whose Expense Integration Status is **Pending**,
**When** the Event Organizer changes or removes its linked Concur expense report,
**Then** the previous link is replaced or removed and saved,
**And** once the expense reaches **Completed**, the report can no longer be
changed or removed regardless of the report's status.

**AC — Records on link (Pattern E)** → Expense (Update: `ExpenseSystemIntegrationStatus`
= Pending) + **Expense Report Entry** (Create: Expense, Expense Report) — one
report per expense.

**Technical Implementation:** LSC Concur Expense Sync MuleSoft connector (forward
+ reverse jobs, scheduled + on-demand), IntegrationJobRun logging, Named
Credentials/OAuth, `ExpenseSystemIntegrationStatus` on Expense + Expense Report,
Expense Report Entry junction, Event Expenses component.

## Reference links

**Salesforce Help (setup & usage):**
- [Concur Expense Sync](https://help.salesforce.com/s/articleView?id=ind.lsc_concur_expense_sync.htm&type=5)
- [Set Up Concur Expense Sync by Using Built-In MuleSoft Integration](https://help.salesforce.com/s/articleView?id=ind.lsc_concur_expense_sync_setup_using_mulesoft_integration.htm&type=5)
- [Set Up Expense Management for Concur Integration](https://help.salesforce.com/s/articleView?id=ind.lsc_expense_management_setup_for_concur_integration.htm&type=5)
- [Add Expense Tab to Visit Page](https://help.salesforce.com/s/articleView?id=ind.lsc_concur_integration_setup_add_expense_tab_to_visit_page.htm&type=5)
- [Create an Expense Type](https://help.salesforce.com/s/articleView?id=ind.lsc_concur_integration_setup_create_an_expense_type.htm&type=5)
- [Permissions to Manage Expenses in the Mobile App](https://help.salesforce.com/s/articleView?id=ind.lsc_permissions_to_manage_expenses_in_mobile_app.htm&type=5)
- [Mobile App Configuration for Expense Management](https://help.salesforce.com/s/articleView?id=ind.lsc_expense_management_mobile_app_configuration.htm&type=5)

**Developer & MuleSoft (integration):**
- [Get Started with MuleSoft Direct for Life Sciences](https://developer.salesforce.com/docs/industries/lifesciences/guide/get-started.html)
- [Explore MuleSoft Direct Integration Apps (Concur Expense Sync)](https://developer.salesforce.com/docs/industries/lifesciences/guide/mulesoft-direct-integrations.html#concur-expense-sync)
- [Concur Expense Sync integration app (Anypoint Exchange)](https://anypoint.mulesoft.com/exchange/org.mule.examples/concur-expense-sync-impl/)

**Parity reference:** IQVIA OCE-P — Concur Integration for Call Expenses (Call 2.0).

> Link status (verified 2026-07-28): developer.salesforce.com + Anypoint links
> resolve and confirm the feature (attachments **up to 1 MB**, bidirectional +
> reverse sync, offline). The `help.salesforce.com` article IDs come from the
> official PRD and are canonical KB IDs (the help site is a JS SPA that blocks
> direct fetch). Tracking params (e.g. Anypoint `_ga`) have been stripped.
