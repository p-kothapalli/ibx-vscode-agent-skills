# Veeva CRM → Salesforce LSC Migration Workflow & Terminology Map

Used by STEP 0's **Veeva→LSC Migration** mode. Transform a legacy Veeva-centric
requirement ("As a… I need…") into a modern Salesforce LSC user story that keeps
the business intent but modernizes the mechanics to LSC-native terminology.

## Contents

- Migration workflow (5 steps)
- Terminology map (Veeva → LSC)
- Concepts with no clean 1:1 mapping (flag these)
- Worked transform example

---

## Migration workflow

```
Migration Progress:
- [ ] M1: Parse the Veeva requirement — extract persona, capability, business value, objects touched
- [ ] M2: Translate every Veeva term to its LSC-native equivalent (table below)
- [ ] M3: Re-align the persona to a concrete LSC role (HCP/HCO are subjects, not the login user)
- [ ] M4: Rewrite ACs in Gherkin (Pattern A) + Pattern E for record writes, in LSC terms
- [ ] M5: Flag any Veeva concept with no clean LSC equivalent in Clarification Questions
```

Rules:

1. **Transform the core story** — convert the Veeva "As a… I need…" into a
   standard Agile user story focused on business value in the LSC ecosystem.
2. **Modernize acceptance criteria** — Gherkin (Given/When/Then), Pattern A;
   pair every record write with Pattern E.
3. **LSC technical alignment** — use LSC-native terminology (Location, Product
   Item, Production Batch, Action Launcher, Visit, Sample Transaction). The story
   body must NOT retain Veeva wording — keep the original Veeva term only in the
   `**Veeva Source:**` header field and, if useful, a one-line mapping note in
   Technical Implementation.
4. **Tone** — methodical, professional, architecturally sound.
5. **Do not invent** LSC object/field names — verify standard ones via
   `salesforce-docs`; mark unverifiable ones *proposed*.

---

## Terminology map (Veeva → LSC)

| Veeva CRM term | Salesforce LSC equivalent | Notes |
|---|---|---|
| Call / Call2 | **Visit** (+ Visit Task) | The field interaction |
| Call Objective | **Visit Task / Objective** | |
| My Schedule / Daily Planner | **Visit scheduling / Calendar** | |
| Account (HCP) | **Account (Person Account)** | Individual provider |
| Account (HCO) | **Account (Business Account)** | Organization |
| Address | **Address / Location** | Sampleable location |
| Sample Management | **Product Item + Inventory** | On-hand stock model |
| Sample Lot | **Production Batch / Production Batch Item** | Lot + expiry |
| Sample Transaction / Disbursement | **Sample Transaction / Disbursement** | With signature |
| Sample Order | **Sample Order / Sample Request** | Replenishment |
| Sample Inventory reconciliation | **Inventory Count / Reconciliation** | Physical vs. system |
| Product / Detail | **Product (Product2)** | |
| CLM / Media (presentations) | **Engage / Content (Approved Documents / DAM)** | Approved content |
| Approved Email | **Approved email / Content distribution** | |
| Territory / Alignment | **Territory Management / Alignment** | |
| Cycle Plan / Call Plan | **MC Cycle Plan / Call Plan / Target** | Reach & frequency |
| Medical Inquiry (Veeva Medical) | **Medical Inquiry / Medical Information Request** | SLA-tracked |
| KOL / Stakeholder Navigator | **KOL/DOL management on Account + Assessment** | Scoring/tiering |
| Consent capture | **Consent / Communication Subscription** | |
| Veeva Vault (content/docs) | **Salesforce Files / DAM / external Vault integration** | May stay in Vault via integration |
| Zvod / offline sync | **Salesforce mobile offline / Field Service offline** | Verify offline capability |
| MyInsights | **CRM Analytics / Dashboards / LWC** | |
| Action Bar / quick actions | **Action Launcher** | Guided actions |
| Call Expenses / Concur (expense mgmt) | **Visit Expenses + Expense Report + Concur Expense Sync** | Bidirectional MuleSoft sync — see `concur-integration.md` |

> **IQVIA OCE-P note:** the LSC Concur expense integration is explicitly modeled
> on **IQVIA OCE-P "Concur Integration for Call Expenses" (Call 2.0)**. When
> migrating from OCE (not Veeva), treat "Call Expenses" → "Visit Expenses" the
> same way and use `references/concur-integration.md` for the LSC-native rules.

---

## Concepts with no clean 1:1 mapping (always flag in Clarification Questions)

- **Offline-first behavior** — Veeva is heavily offline; confirm the LSC/mobile
  offline strategy for the story's actions.
- **Veeva Vault content lifecycle** — approval/withdrawal of content may remain
  in Vault; clarify whether content is migrated or integrated.
- **Veeva-specific config objects** (e.g. proprietary data-change-request,
  network/OpenData) — clarify the LSC/Data Cloud master-data source.
- **Custom Veeva VOD packages / Zvod records** — no direct equivalent; redesign.

Never silently drop a Veeva concept — either map it or raise it as a question.

---

## Worked transform example

**Veeva input:**

> As a Field Rep, I need a Sample Inventory screen to see my on-hand sample lots
> so I can manage inventory and stay compliant.

**LSC output (abridged — full format per `output-template.md`):**

> **Persona:** Field Sales Representative
> **LSC Sub-domain:** Commercial
> **Veeva Source:** Sample Management / Sample Inventory
>
> **As a** Field Sales Representative,
> **I want** a Sample Inventory Dashboard in the Life Sciences Commercial app to
> view and manage my on-hand sample batches,
> **So that** I can maintain accurate inventory levels and ensure PDMA compliance.
>
> **AC-1 — On-hand sample lots are shown for the rep's location**
> **Given** a Field Sales Representative is logged into the LSC app,
> **When** they open the Sample Inventory Dashboard,
> **Then** a filtered list of active Production Batch Items linked to their
> Location is displayed with lot number, quantity on hand, and expiration date.
>
> **AC-2 — Quick actions are available from the inventory timeline**
> **Given** the rep is viewing their dashboard,
> **When** they interact with the Inventory Timeline,
> **Then** they can launch quick actions (acknowledge a shipment, initiate a
> Product Request) via Action Launcher.

Note how "Sample Management" → "Product Item / Production Batch", "Call" isn't
present, and the persona is the field user (not the HCP).
