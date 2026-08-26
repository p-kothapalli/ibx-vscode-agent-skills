# Post-Generation Offers (STEP 6 detail)

After presenting a validated LSC story, offer these optional next steps. Each one
depends on an MCP server or CLI being connected — check availability first with
the MCP tooling and only offer what is usable. If a server is present but needs
auth, mention that it can be authenticated first.

> **MCP tool names are fully qualified** as `server:tool` (e.g.,
> `code-review-graph:query_graph`). In this workspace the underlying server ID
> may be prefixed (e.g., `project-0-IBXQA-code-review-graph`); use the tooling to
> resolve the exact ID before calling.

## Contents

- 6.1 QTA Test Bridge (`qta-core`)
- 6.2 Diagram Generation (`udd-whiteboard` / `figma` / `diagram-beautifier` / Mermaid)
- 6.3 GUS Work Item Creation (`gus_server`)
- 6.4 Salesforce Docs Verification (`salesforce-docs`)
- 6.5 Knowledge Base (`notebooklm`)
- 6.6 Story Dependency Check

---

## 6.1 QTA Test Bridge (`qta-core`)

If the `qta-core` MCP server is connected, offer to convert acceptance criteria
into QTA-compatible test prompts.

```
"This story has [N] acceptance criteria. Would you like me to generate
QTA browser automation test prompts from them?"
```

Mapping rules for AC -> QTA prompt:

| AC Section | QTA Prompt Section |
|-----------|-------------------|
| **Given** (precondition) | Navigation steps + setup context |
| **When** (user action) | Click, type, select interaction steps |
| **Then** (expected result) | Assertion / verification checks |
| OmniScript / component name | Target URL / flow identifier |

Example output:

```
QTA Test Prompt: "Open the LSC Commercial app. Navigate to the Sample Inventory
Dashboard. Verify that only active sample lots for the running user's location
are listed with lot number, on-hand quantity, and expiration date. Confirm an
expired lot is flagged and excluded from the disbursable total."
```

Generate one QTA prompt per acceptance criterion. Store in `qta_test_prompts.md`
alongside the story.

---

## 6.2 Diagram Generation

Offer a diagram of the story (and, for an epic breakdown, an end-to-end
dependency chain). Use whichever is available, in this order:

1. **`udd-whiteboard`** MCP — collaborative whiteboard diagram.
2. **`figma`** MCP — if the team maintains design/flow diagrams in Figma.
3. **`diagram-beautifier`** skill — to produce a polished diagram.
4. **Mermaid fallback** — embed a Mermaid diagram directly in the story markdown.

The diagram should show:
- The current user story as the highlighted node
- The previous story that feeds into it and the next story that depends on it
- The full epic chain across all generated stories (epic breakdown mode)
- Any shared systems/objects (Product Item, Territory, Data Cloud) connecting stories

---

## 6.3 GUS Work Item Creation (`gus_server`)

If the `gus_server` MCP is connected (or GUS CLI via `sf data` as a fallback),
offer to create a work item:

```
"The story is validated. Would you like me to create a GUS work item?"
```

Map story sections to GUS fields:
- Story -> `Description`
- Acceptance Criteria -> `Acceptance_Criteria__c`
- Priority -> `Priority`
- Persona -> Team assignment context

---

## 6.4 Salesforce Docs Verification (`salesforce-docs`)

If the Salesforce Docs MCP is connected (`salesforce-docs:salesforce_docs_search`
/ `salesforce-docs:salesforce_docs_fetch`), use it to verify any **standard**
Salesforce / Life Sciences Cloud object, field, feature, or API fact the story
relies on (Account/Person Account, Visit, Product Item, Production Batch, Sample
Transaction, Action Launcher, Territory) and cite the returned source URL. This
is the **primary** verification path for standard LSC facts in a PNM workspace
where the LSC package may not be deployed. Custom `LSC_*` components are still
verified via `code-review-graph`.

---

## 6.5 Knowledge Base (`notebooklm`)

If the `notebooklm` MCP is connected, use it to consult the shared **Salesforce
Life Sciences Librarian** notebook for LSC/HLS best practices, data models, and
implementation patterns when a story touches unfamiliar commercial or medical
territory. This is also where the JIRA-generation reference guidance lives.

---

## 6.6 Story Dependency Check

After generating, scan `requirements/` for stories that reference the same
components. Report any dependencies or conflicts:

```
"I found 2 existing stories that reference the same components:
  - LSC_SampleInventoryDashboard_UserStory.md
  This story depends on the Product Item model from that story and blocks the
  reconciliation story. Would you like me to add cross-references?"
```
