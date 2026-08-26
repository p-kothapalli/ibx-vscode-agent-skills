# IBX Salesforce Agent Skills for VS Code

Port of the IBX Cursor agent skills from [`pkothapalli/IBXEnhancements`](https://git.soma.salesforce.com/pkothapalli/IBXEnhancements) so they work with **GitHub Copilot Agent Skills** in [Visual Studio Code](https://code.visualstudio.com/docs/agent-customization/agent-skills).

Each skill is a folder with a `SKILL.md` that follows the open [Agent Skills](https://agentskills.io/specification) standard. Copilot reads the YAML `description` to decide when to load a skill, then follows the instructions in the body.

**Where upstream [`forcedotcom/sf-skills`](https://github.com/forcedotcom/sf-skills) and IBX rules conflict, the IBX rules win.**

> Internal pack. These skills encode IBX org conventions (`PRM_` naming, OmniStudio as SFDX metadata, `qa-sandbox`, graph-first MCP). Keep the GitHub repo **private**.

---

## Table of contents

1. [What you get](#what-you-get)
2. [Prerequisites](#prerequisites)
3. [Install (pick one method)](#install-pick-one-method)
   - [Method A — Personal install (recommended)](#method-a--personal-install-recommended-one-command)
   - [Method B — Point VS Code at a clone](#method-b--point-vs-code-at-this-clone-no-copy)
   - [Method C — Project install (share with the repo)](#method-c--project-install-share-with-the-salesforce-repo)
   - [Method D — VS Code extension (VSIX)](#method-d--vs-code-extension-vsix)
4. [Verify the skills loaded](#verify-the-skills-loaded)
5. [How to use the skills](#how-to-use-the-skills)
6. [Optional: MCP servers the skills expect](#optional-mcp-servers-the-skills-expect)
7. [Optional: always-on Copilot instructions](#optional-always-on-copilot-instructions)
8. [What was rewired from Cursor](#what-was-rewired-from-cursor)
9. [Skill catalog](#skill-catalog)
10. [Updating](#updating)
11. [Uninstall](#uninstall)
12. [Troubleshooting](#troubleshooting)

---

## What you get

| Count | Kind |
|------:|------|
| 28 | Agent skills under `skills/<name>/SKILL.md` — IBX overlays of [`forcedotcom/sf-skills`](https://github.com/forcedotcom/sf-skills) |
| 3 | Always-on Copilot instruction templates (IBX conventions, graph-first, SOQL archive) |
| 1 | VS Code MCP template (Salesforce DX, code-review-graph, Salesforce Docs) |

This pack is **only** the upstream Salesforce skills that IBX has layered org conventions onto. IBX-only skills (User Story Architect, Practitioner Creation verifiers) are not included. Folder names keep the IBX/Cursor names (`generating-apex`, …); each maps to a current `forcedotcom/sf-skills` skill (`platform-apex-generate`, …). **Where upstream and IBX rules conflict, the IBX rules win.**

---

## Prerequisites

1. **Visual Studio Code** recent enough to support Agent Skills (the feature landed in Copilot’s 2026 agent-customization work). Use the latest stable or [Insiders](https://code.visualstudio.com/insiders/).
2. **[GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)** and **[GitHub Copilot Chat](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot-chat)** extensions, signed in with a Copilot plan that includes **Agent mode**.
3. In VS Code settings, leave Agent Skills enabled (this is the default):

   ```json
   {
     "chat.useAgentSkills": true
   }
   ```

4. Open **Copilot Chat** and switch the mode dropdown to **Agent** (not Ask / Edit). Skills load in Agent mode.
5. Optional but strongly recommended for IBX work:
   - Salesforce CLI (`sf`)
   - The MCP servers in [Optional: MCP servers](#optional-mcp-servers-the-skills-expect)

Confirm Agent Skills exist in your build:

- Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`) → **Chat: Open Customizations** → **Skills** tab  
  or type `/skills` in the Copilot Chat input.

---

## Install (pick one method)

All methods install the **same** `skills/` folders. Choose based on whether you want skills on every project, only in the IBX Salesforce repo, or bundled as an extension.

```
                    ┌─────────────────────────────┐
                    │  this GitHub repo (clone)   │
                    │  skills/<skill>/SKILL.md    │
                    └──────────────┬──────────────┘
           ┌───────────────────────┼───────────────────────┐
           ▼                       ▼                       ▼
   ~/.copilot/skills/     .github/skills/          VS Code extension
   (Method A — user)      (Method C — project)     (Method D — VSIX)
           │                       │                       │
           └───────────┬───────────┴───────────┬───────────┘
                       ▼                       ▼
              Copilot Agent mode        slash commands: /generating-apex
```

### Method A — Personal install (recommended, one command)

Puts skills in your user profile so **every VS Code window** can see them.

```bash
git clone https://github.com/p-kothapalli/ibx-vscode-agent-skills.git
cd ibx-vscode-agent-skills
./scripts/install-user.sh
```

What the script does:

- Copies each `skills/<name>/` folder to `~/.copilot/skills/<name>/` (macOS / Linux).
- On Windows (Git Bash or WSL), copies to `~/.copilot/skills/` as well. Native Windows Copilot also reads `%USERPROFILE%\.copilot\skills\`.
- Does not overwrite extra files you added in those folders unless you pass `--force`.

Then **reload VS Code**:

1. `Cmd+Shift+P` / `Ctrl+Shift+P`
2. Run **Developer: Reload Window**

Default discovery already includes `~/.copilot/skills`, so you do **not** need to change `chat.agentSkillsLocations` for this method.

### Method B — Point VS Code at this clone (no copy)

Useful if you want a single git-tracked copy and to `git pull` updates in place.

1. Clone this repo somewhere stable, for example `~/src/ibx-vscode-agent-skills`.
2. Open **VS Code Settings (JSON)** — Command Palette → **Preferences: Open User Settings (JSON)**.
3. Add the clone’s `skills` folder to `chat.agentSkillsLocations`:

   ```json
   {
     "chat.useAgentSkills": true,
     "chat.agentSkillsLocations": {
       ".github/skills": true,
       ".claude/skills": true,
       "~/.copilot/skills": true,
       "~/.claude/skills": true,
       "~/src/ibx-vscode-agent-skills/skills": true
     }
   }
   ```

   Use your real clone path. `~` is expanded. Relative paths are resolved from the **workspace root**, so a `~/…` (user-level) path is the right choice here.

4. Reload the window.

A ready-made snippet lives in [`templates/settings.json`](templates/settings.json).

### Method C — Project install (share with the Salesforce repo)

Puts skills in the IBX Salesforce project so **everyone who clones that project** gets them. Copilot discovers project skills from `.github/skills/` automatically.

```bash
# from this skills repo
./scripts/install-project.sh /path/to/your/IBXEnhancements-or-IBXQA-clone
```

The script:

1. Copies `skills/*` → `<target>/.github/skills/`
2. Copies always-on instruction files → `<target>/.github/instructions/`
3. Writes `<target>/.vscode/mcp.json` **only if that file does not already exist** (it will not clobber a teammate’s MCP config)
4. Merges `chat.useAgentSkills: true` into `<target>/.vscode/settings.json` if needed

Commit the new folders in the **Salesforce** repo (not this skills repo) if you want the team to share them:

```bash
cd /path/to/your/IBXEnhancements-or-IBXQA-clone
git add .github/skills .github/instructions .vscode/mcp.json .vscode/settings.json
git status   # review, then commit in that repo when you are ready
```

### Method D — VS Code extension (VSIX)

Bundles every skill via the `chatSkills` contribution point so Copilot loads them from the extension, not from disk copies.

```bash
cd ibx-vscode-agent-skills
npm install -g @vscode/vsce
vsce package --allow-missing-repository
code --install-extension ibx-vscode-agent-skills-1.0.0.vsix
```

Reload the window. Skills appear in **Chat: Open Customizations → Skills** with the extension as the source.

To uninstall the extension later: Extensions view → **IBX Salesforce Agent Skills** → Uninstall.

---

## Verify the skills loaded

Do all three checks the first time.

### 1. Customizations editor

1. Open Copilot Chat.
2. Click the gear (**Configure Chat**) or run **Chat: Open Customizations**.
3. Open the **Skills** tab.
4. You should see names such as `generating-apex`, `building-omnistudio-omniscript`, `querying-soql`, `salesforce-development`.

If the list is empty, see [Troubleshooting](#troubleshooting).

### 2. Slash command menu

In Copilot Chat (Agent mode), type `/`.

You should see skill commands, for example:

- `/generating-apex`
- `/generating-apex-test`
- `/building-omnistudio-integration-procedure`
- `/querying-soql`
- `/running-apex-tests`

### 3. Auto-invoke smoke test

In Agent mode, send:

> Add a roll-up summary field on the Case Manager related custom object following IBX naming.

Copilot should load `generating-custom-field` (and often `salesforce-development`). In the response, look for IBX-specific rules: `PRM_` prefix, graph-first lookup, permission-set FLS — not a generic Salesforce tutorial.

A second probe:

> Build an Integration Procedure that calls the Precisely address API following IBX naming.

That should load `building-omnistudio-integration-procedure` and mention `PRM_*` IPs plus the active-version rule.

---

## How to use the skills

### Automatic (preferred)

Describe the work in Agent mode. Copilot matches your wording to each skill’s `description`. Examples:

| You say | Skill that should load |
|---|---|
| “Create a `PRM_FooService` with a selector” | `generating-apex` + `generating-apex-test` |
| “Build the Integration Procedure that calls Precisely” | `building-omnistudio-integration-procedure` |
| “Export these OmniScripts to QA with DataPacks” | `deploying-omnistudio-datapacks` |
| “Run local tests with coverage on qa-sandbox” | `running-apex-tests` |
| “Archive this SOQL for Case Manager history” | `querying-soql` |

### Explicit slash command

Force a skill when auto-select is wrong or you want only that workflow:

```
/generating-apex create PRM_RosterParseService with USER_MODE queries
/running-code-analyzer scan force-app/main/default/classes/PRM_CMAService.cls
```

You can add extra context after the command. That text is the skill’s argument.

### Confirm it actually loaded

A correctly loaded IBX skill will mention grounded rules, for example:

- `PRM_` / `prm` naming
- Active OmniStudio version only (`<isActive>true</isActive>`)
- `PRM_ExceptionLogger` / `PRM_TestDataFactory` / `PRM_TriggerBypassPermission`
- SOQL archive path `requirements/SOQL/YYYY-MM-DD_<Topic>.md`
- Graph-first via `code-review-graph` before raw search

If the answer is generic Salesforce advice with none of those, the skill did not load — invoke it with `/skill-name` or reload the window.

---

## Optional: MCP servers the skills expect

Skills still work without MCP (they fall back to Copilot workspace search). Graph-first impact analysis, org tests, and Salesforce docs citations are much better with MCP enabled.

### Workspace MCP file

Copy [`templates/mcp.json`](templates/mcp.json) to your Salesforce project:

```bash
mkdir -p /path/to/sf-project/.vscode
cp templates/mcp.json /path/to/sf-project/.vscode/mcp.json
```

Then in VS Code: Command Palette → **MCP: List Servers** → start **Salesforce DX** and **code-review-graph**. Approve the trust prompt.

VS Code Copilot reads `.vscode/mcp.json` using a `"servers"` map (not Cursor’s `"mcpServers"`). The template is already in VS Code shape.

| Server | Why the skills need it |
|---|---|
| **Salesforce DX** (`@salesforce/mcp`) | Org deploy, retrieve, Apex tests (`run_apex_test`), metadata describe |
| **code-review-graph** | Callers, callees, impact radius, “does this IP/DR exist?” — **use first** before search |
| **salesforce-docs** | Official Health Cloud / LSC object and field facts |

`code-review-graph` must be installed and on your `PATH` (`code-review-graph serve`). If it is missing, skills tell Copilot to fall back to workspace search.

### User-level MCP (all workspaces)

Command Palette → **MCP: Open User Configuration** and paste the same `"servers"` block.

Do **not** commit Named Credential secrets, OAuth client ids, or org tokens into `mcp.json`. The template uses placeholders only.

---

## Optional: always-on Copilot instructions

Cursor used **always-apply rules** (`.cursor/rules/*.mdc`). VS Code’s equivalent is [custom instructions](https://code.visualstudio.com/docs/copilot/copilot-customization) under `.github/instructions/`.

Method C copies these for you. For a manual install, copy:

| File | When it applies |
|---|---|
| `templates/instructions/salesforce-development.instructions.md` | `force-app/**` |
| `templates/instructions/code-review-graph-first.instructions.md` | whole repo |
| `templates/instructions/soql-queries-archive.instructions.md` | whole repo |

They are instruction files, not skills: Copilot applies them continuously (by `applyTo` glob) instead of loading them on demand.

You can also paste [`templates/copilot-instructions.md`](templates/copilot-instructions.md) into `.github/copilot-instructions.md` for a short always-on IBX briefing.

---

## What was rewired from Cursor

| Cursor | VS Code / Copilot |
|---|---|
| `.cursor/skills/<name>/SKILL.md` | `skills/<name>/SKILL.md`, installed to `~/.copilot/skills/` or `.github/skills/` |
| Auto-discovery of `.cursor/skills/` | `chat.agentSkillsLocations` + defaults (`.github/skills`, `~/.copilot/skills`, …) |
| `AskQuestion` tool | Numbered-option questions **in Copilot Chat**; wait for the user’s reply |
| Cursor `Grep` / `Glob` / `Read` | Copilot workspace search, file search, and file read (after graph MCP) |
| `.cursor/mcp.json` (`mcpServers`) | `.vscode/mcp.json` (`servers`) |
| `.cursor/rules/*.mdc` (`alwaysApply`) | `.github/instructions/*.instructions.md` (`applyTo`) |
| Reload Cursor window | **Developer: Reload Window** or **Chat: Open Customizations** |
| `globs:` / `effort:` on skill frontmatter | Moved under `metadata:` (VS Code only honors the Agent Skills spec fields) |
| Slash-style nudges | Native `/skill-name` slash commands (`user-invocable: true`) |

Skill **bodies** (IBX overrides, rubrics, field maps) are preserved. Tool-host sentences were rewritten so Copilot does not look for Cursor-only tools.

---

## Skill catalog

This pack keeps the IBX folder names. Each is an overlay of a skill in [`forcedotcom/sf-skills`](https://github.com/forcedotcom/sf-skills):

| This pack | Upstream `sf-skills` |
|---|---|
| `generating-apex` | `platform-apex-generate` |
| `generating-apex-test` | `platform-apex-test-generate` |
| `generating-lwc-components` | `experience-lwc-generate` |
| `building-omnistudio-integration-procedure` | `omnistudio-integration-procedure-generate` |
| `building-omnistudio-datamapper` | `omnistudio-datamapper-generate` |
| `building-omnistudio-omniscript` | `omnistudio-omniscript-generate` |
| `building-omnistudio-flexcard` | `omnistudio-flexcard-generate` |
| `building-omnistudio-callable-apex` | `omnistudio-callable-apex-generate` |
| `analyzing-omnistudio-dependencies` | `omnistudio-dependencies-analyze` |
| `deploying-omnistudio-datapacks` | `omnistudio-datapacks-deploy` |
| `deploying-metadata` | `platform-metadata-deploy` |
| `querying-soql` | `platform-soql-query` |
| `running-apex-tests` | `platform-apex-test-run` |
| `running-code-analyzer` | `dx-code-analyzer-run` |
| `configuring-code-analyzer` | `dx-code-analyzer-configure` |
| `debugging-apex-logs` | `platform-apex-logs-debug` |
| `generating-custom-field` | `platform-custom-field-generate` |
| `generating-custom-object` | `platform-custom-object-generate` |
| `generating-validation-rule` | `platform-validation-rule-generate` |
| `generating-permission-set` | `platform-permission-set-generate` |
| `generating-flexipage` | `platform-flexipage-generate` |
| `generating-flow` | `automation-flow-generate` |
| `building-sf-integrations` | `integration-connectivity-generate` |
| `handling-sf-data` | `platform-data-manage` |
| `getting-datacloud-schema` | `data360-schema-get` |
| `developing-datacloud-code-extension` | `data360-code-extension-generate` |
| `investigating-agentforce-d360` | `agentforce-d360-analyze` |
| `salesforce-development` | IBX umbrella conventions (builder plugin analogue) |

### Umbrella


| Skill | Slash command | Use when |
|---|---|---|
| `salesforce-development` | `/salesforce-development` | Editing Apex, LWC, or metadata under `force-app/` — org conventions |

### Foundational

| Skill | Slash command |
|---|---|
| `generating-apex` | `/generating-apex` |
| `generating-apex-test` | `/generating-apex-test` |
| `generating-lwc-components` | `/generating-lwc-components` |

### OmniStudio (critical)

| Skill | Slash command |
|---|---|
| `building-omnistudio-integration-procedure` | `/building-omnistudio-integration-procedure` |
| `building-omnistudio-datamapper` | `/building-omnistudio-datamapper` |
| `building-omnistudio-omniscript` | `/building-omnistudio-omniscript` |
| `building-omnistudio-flexcard` | `/building-omnistudio-flexcard` |
| `building-omnistudio-callable-apex` | `/building-omnistudio-callable-apex` |
| `analyzing-omnistudio-dependencies` | `/analyzing-omnistudio-dependencies` |
| `deploying-omnistudio-datapacks` | `/deploying-omnistudio-datapacks` |

### Platform loop

| Skill | Slash command |
|---|---|
| `deploying-metadata` | `/deploying-metadata` |
| `querying-soql` | `/querying-soql` |
| `running-apex-tests` | `/running-apex-tests` |
| `running-code-analyzer` | `/running-code-analyzer` |
| `configuring-code-analyzer` | `/configuring-code-analyzer` |
| `debugging-apex-logs` | `/debugging-apex-logs` |

### Schema and declarative

| Skill | Slash command |
|---|---|
| `generating-custom-field` | `/generating-custom-field` |
| `generating-custom-object` | `/generating-custom-object` |
| `generating-validation-rule` | `/generating-validation-rule` |
| `generating-permission-set` | `/generating-permission-set` |
| `generating-flexipage` | `/generating-flexipage` |
| `generating-flow` | `/generating-flow` |

### Integration and data

| Skill | Slash command |
|---|---|
| `building-sf-integrations` | `/building-sf-integrations` |
| `handling-sf-data` | `/handling-sf-data` |

### Data Cloud and Agentforce

Upstream counterparts: `data360-schema-get`, `data360-code-extension-generate`, `agentforce-d360-analyze`.

| Skill | Slash command | Upstream `sf-skills` name |
|---|---|---|
| `getting-datacloud-schema` | `/getting-datacloud-schema` | `data360-schema-get` |
| `developing-datacloud-code-extension` | `/developing-datacloud-code-extension` | `data360-code-extension-generate` |
| `investigating-agentforce-d360` | `/investigating-agentforce-d360` | `agentforce-d360-analyze` |

Older Data Cloud lifecycle skills (`orchestrating-datacloud`, `connecting-datacloud`, …) are **not** in current [`forcedotcom/sf-skills`](https://github.com/forcedotcom/sf-skills) and are not shipped here.

---

## Updating

```bash
cd /path/to/ibx-vscode-agent-skills
git pull origin main
./scripts/install-user.sh --force          # Method A
# or re-run Method C against the Salesforce clone
./scripts/install-project.sh --force /path/to/sf-project
```

If you used Method B (settings path to the clone), `git pull` is enough — then reload the window.

If you used Method D, rebuild and reinstall the VSIX after pulling.

If you installed an earlier revision of this pack, run `./scripts/uninstall-user.sh` then `./scripts/install-user.sh --force`. That removes retired IBX-only skills (`user-story-architect`, `verifying-*`, old Data Cloud lifecycle folders) from `~/.copilot/skills/`.

---

## Uninstall

**Method A**

```bash
./scripts/uninstall-user.sh
```

Or delete the skill folders under `~/.copilot/skills/` whose names match this pack.

**Method B** — remove the clone path from `chat.agentSkillsLocations`.

**Method C** — delete `.github/skills/` in the Salesforce project (and the instruction files if you added them).

**Method D** — uninstall the VS Code extension.

Reload the window after uninstalling.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Skills tab is empty | Confirm Copilot Chat is installed, you are in **Agent** mode, and `chat.useAgentSkills` is `true`. Reload the window. |
| Slash menu has no `/generating-apex` | Personal install: check `ls ~/.copilot/skills/generating-apex/SKILL.md`. Project install: check `.github/skills/generating-apex/SKILL.md`. The `name:` in frontmatter **must** match the folder name (lowercase, hyphens). |
| Skill exists but never auto-loads | Invoke it with `/skill-name`. If that works, the `description` is not matching your prompt — add keywords or ask more specifically. |
| Copilot looks for an `AskQuestion` tool | You are on an old copy of the skill. Pull this repo and reinstall. Rewired skills ask numbered questions in chat. |
| `code-review-graph` tools missing | Install the graph CLI, add it to `.vscode/mcp.json`, start the server from **MCP: List Servers**. Skills will fall back to search if it is absent. |
| MCP file ignored | VS Code wants `.vscode/mcp.json` with a top-level `"servers"` key. Cursor’s `"mcpServers"` key will not load. |
| Windows paths | Prefer `~\.copilot\skills\` or Git Bash `~/.copilot/skills/`. Reload after the copy. |
| Monorepo / nested package | Enable `chat.useCustomizationsInParentRepositories` so Copilot walks up to the parent `.github/skills/`. |
| Extension skills missing | Confirm the VSIX installed (Extensions view) and that you reloaded. `chatSkills` contributions only register from installed extensions. |
| `name` with slashes or uppercase | The skill will **silently fail to load**. This pack’s names are already valid (`a-z`, `0-9`, hyphen). |

Official reference: [Use Agent Skills in VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills).

---

## Repository layout

```
ibx-vscode-agent-skills/
├── README.md                          ← you are here
├── ATTRIBUTION.md                     ← upstream sf-skills credit
├── LICENSE                            ← internal use
├── package.json                       ← VS Code extension manifest (chatSkills)
├── .vscodeignore
├── skills/                            ← canonical skill folders (28)
│   └── generating-apex/SKILL.md
├── templates/
│   ├── mcp.json                       ← VS Code Copilot MCP servers
│   ├── settings.json                  ← chat.agentSkillsLocations snippet
│   ├── copilot-instructions.md        ← short always-on IBX briefing
│   └── instructions/                  ← .github/instructions templates
└── scripts/
    ├── install-user.sh
    ├── install-project.sh
    ├── uninstall-user.sh
    └── rewire_skills.py               ← Cursor → VS Code transform (already applied)
```

---

## License and source

- **Source skills:** Salesforce internal repo `git.soma.salesforce.com/pkothapalli/IBXEnhancements` (`.cursor/skills/`), themselves based on [`forcedotcom/sf-skills`](https://github.com/forcedotcom/sf-skills). See [ATTRIBUTION.md](ATTRIBUTION.md).
- **License:** Internal IBX / Salesforce use. Do not publish this repository as public.
