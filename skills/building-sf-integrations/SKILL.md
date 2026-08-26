---
name: building-sf-integrations
description: 'Salesforce integration architecture and runtime plumbing with 120-point scoring.
  Use this skill to set up Named Credentials, External Credentials, External Services, REST/SOAP
  callout patterns, Platform Events, and Change Data Capture. TRIGGER when: user sets up Named
  Credentials, External Services, REST/SOAP callouts, Platform Events, CDC, or touches .namedCredential-meta.xml
  files. DO NOT TRIGGER when: Connected App/OAuth config (use configuring-connected-apps),
  Apex-only logic (use generating-apex), or data import/export (use handling-sf-data).'
metadata:
  version: 1.1-ibx
  upstream: https://github.com/forcedotcom/sf-skills/tree/main/skills/building-sf-integrations
  source: IBXEnhancements .cursor/skills
  host: vscode-copilot
compatibility: 'GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph,
  Salesforce DX.'
user-invocable: true
---

# building-sf-integrations: Salesforce Integration Patterns Expert

> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/building-sf-integrations` if it does not auto-load.


Use for **integration architecture and runtime plumbing**: Named Credentials, External Credentials, External Services, REST/SOAP callouts, Platform Events, CDC, event-driven design.

## Choose the Pattern

| Need | Default pattern |
|---|---|
| authenticated outbound API call | Named Credential / External Credential + Apex or Flow |
| spec-driven API client | External Service |
| trigger-originated callout | async callout pattern |
| decoupled event publishing | Platform Events |
| change-stream consumption | CDC |

## High-Signal Rules

- Never hardcode credentials. Prefer **External Credentials / Named Credentials** for runtime-managed auth.
- **No synchronous callouts from triggers** — go async (Queueable/future).
- Define timeouts explicitly; plan retries / dead-letter for transient failures.
- Add request/response logging and observability.
- Endpoint security: Remote Site Settings / CSP Trusted Sites as needed.

## Output

Credential metadata + callout Apex (async/sync as appropriate) + event/CDC artifacts + endpoint security metadata + next deploy/test step.

Delegate: OAuth app setup → `configuring-connected-apps`; deeper service/retry code → `generating-apex`; declarative HTTP/Flow wrapper → `generating-flow`; deploy → `deploying-metadata`; data import/export → `handling-sf-data`.

---

## IBX Overrides & Additions

> IBX-project-specific rules that **override or extend** the upstream guidance above.
> When there is a conflict, IBX rules win.

### 1 — Existing IBX Named Credentials (reuse before creating)

IBX already integrates with several external systems via `PRM_`-prefixed Named Credentials. Reuse these instead of creating new auth plumbing:

| Named Credential | System | Typical use |
|---|---|---|
| `PRM_Precisely_API` | Precisely | Address validation/standardization (`PRM_AddressValidationService`) |
| `PRM_CAQH_API` | CAQH ProView | Provider credentialing data |
| `NPPES_API` | CMS NPPES | NPI registry lookups |
| `PRM_SDSApi` | SDS | Sanctions/screening data source |
| `PRM_SendGrid` | SendGrid | Outbound email |

Files live in `force-app/main/default/namedCredentials/`. Read the existing one first to match auth model and conventions.

### 2 — Mulesoft Is the Primary Integration Backbone

Much external traffic flows through **Mulesoft**. The project ships `PRM_Mulesoft_Endpoint` / `PRM_Mulesoft_Access_Token` remote sites and `PRM_Mulesoft_Connector` / `PRM_Mulesoft_Integration` / `PRM_ManageDataIntegrations` permission sets. For new outbound work, check whether it should route through Mulesoft (and use those permission sets for the integration user) before standing up a direct callout.

### 3 — Callouts Often Originate from OmniStudio, Not Just Apex

A large portion of IBX integration runs as **Integration Procedure Remote Actions** calling `PRM_*` Apex (`Callable` / `omnistudio.VlocityOpenInterface2`). When designing/repairing an integration:
- Decide whether the entry point is an IP Remote Action (see `building-omnistudio-integration-procedure` + `building-omnistudio-callable-apex`) or a pure Apex service.
- Keep the callout in a `PRM_*` `with sharing` class; log failures via **`PRM_ExceptionLogger`**; never block the IP on a synchronous trigger callout.

### 4 — Naming, Endpoint Security, Bypass

- New named/external credentials, classes, remote sites: **`PRM_`** prefix.
- Add Remote Site Setting / CSP Trusted Site (`remoteSiteSettings/`) for any new endpoint; FlexCard/VF callbacks already use `FlexCardLightningForceURL`/`FlexCardVisualForceURL`.
- Integration users typically carry `PRM_TriggerBypassPermission` / `PRM_TriggerFlowBypassPermission` so inbound writes skip automation — coordinate via `generating-permission-set`.

### 5 — Precisely Bypass Toggle

The address-validation integration has a documented bypass (`PRM_AddressValidationService.isPreciselySkipped()`). Preserve such feature toggles when modifying the Precisely path rather than hardcoding endpoint behavior.

### 6 — Deploy & Test

```bash
sf project deploy start \
  --source-dir force-app/main/default/namedCredentials/<Name>.namedCredential-meta.xml \
  --source-dir force-app/main/default/remoteSiteSettings/<Name>.remoteSite-meta.xml \
  --target-org qa-sandbox --wait 10
```
Default alias `qa-sandbox`. Test callout Apex with `HttpCalloutMock` (see `running-apex-tests`); deploy ordering and non-source-tracking handling per `deploying-metadata`.
