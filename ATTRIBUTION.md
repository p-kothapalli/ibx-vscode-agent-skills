# Attribution

## IBX Cursor skills

The skill bodies and IBX override sections were copied from:

- https://git.soma.salesforce.com/pkothapalli/IBXEnhancements  
  path: `.cursor/skills/`

They were rewired in this repository so GitHub Copilot in Visual Studio Code can load them (Agent Skills locations, VS Code MCP shape, Copilot Chat numbered questions instead of Cursor `AskQuestion`).

## Upstream Salesforce skills

Many skills started from the public Salesforce pack:

- https://github.com/forcedotcom/sf-skills

Where a skill folder includes `CREDITS.md` or an `upstream` metadata field, that file/field is authoritative for the upstream revision. IBX override sections win on conflict.

## Agent Skills standard

- https://agentskills.io/specification
- https://code.visualstudio.com/docs/agent-customization/agent-skills
