# IBX Copilot briefing

You are working in the IBX provider-credentialing Salesforce org (Health Cloud + OmniStudio + custom `PRM_*` metadata).

- Prefer the installed **agent skills** for the task (`generating-apex`, OmniStudio builders, `user-story-architect`, verification skills, …). Invoke with `/skill-name` when unsure.
- IBX overrides beat upstream `forcedotcom/sf-skills` guidance.
- Custom names use `PRM_` / `prm`. OmniStudio source is SFDX metadata; only the **active** version is live.
- Graph-first: `code-review-graph` MCP before workspace search when that server is connected.
- Archive user-facing SOQL under `requirements/SOQL/`.
- Default org alias: `qa-sandbox`. Coverage target: ≥ 85%. Logger: `PRM_ExceptionLogger`. Test data: `PRM_TestDataFactory`.
