# User Story Architect — MCP Server (Phase II)

## Overview

FastMCP server that provides machine-readable tools for the User Story Architect agent.
Replaces manual codebase scanning with structured, reusable MCP tool calls.

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | Tested on 3.11, 3.12 |
| pip | latest | Or use `uv` |
| fastmcp | 2.0+ | `pip install fastmcp` |
| pyyaml | 6.0+ | `pip install pyyaml` |

## Quick Start

```bash
# 1. Install dependencies
cd mcp_server
pip install -r requirements.txt

# 2. Run in stdio mode (for VS Code Copilot MCP)
python server.py

# 3. Or run in HTTP mode (for external clients / testing)
python server.py --http
# Server runs on http://127.0.0.1:29120
```

## VS Code Copilot MCP Configuration

Add to `.vscode/mcp.json` (VS Code Copilot):

```json
{
  "servers": {
    "user-story-architect": {
      "type": "stdio",
      "command": "python3",
      "args": ["${workspaceFolder}/mcp_server/server.py"]
    }
  }
}
```

## Tools Reference

### Codebase Analysis

| Tool | Purpose | Key Args |
|------|---------|----------|
| `analyze_omniscript` | Parse OmniScript elements, steps, conditions, data sources from force-app/ | `omniscript_name` |
| `find_impacted_components` | Cross-reference search: find all files that reference a component | `component_name`, `search_scope` |
| `search_existing_stories` | Search requirements/ for stories matching a keyword | `keyword` |

### Vertical Configuration

| Tool | Purpose | Key Args |
|------|---------|----------|
| `select_vertical` | Load vertical config (prefix, objects, flows, naming) from YAML | `vertical` |

Available verticals: PNM, HLS, Insurance, FSC

### Session Management

| Tool | Purpose | Key Args |
|------|---------|----------|
| `create_session` | Create new session directory with metadata files | `story_title`, `vertical` |
| `save_interview_qa` | Append Q&A pair to interview transcript | `session_id`, `question`, `answer`, `phase` |
| `save_component_delta` | Save proposed component changes | `session_id`, `story_id`, `components` |
| `save_codebase_scan` | Persist codebase scan results | `session_id`, `scan_results` |
| `finalize_session` | Mark session complete, link to story file | `session_id`, `story_file_path` |

### Story Linting

| Tool | Purpose | Key Args |
|------|---------|----------|
| `lint_story` | Deterministic validation: sections, Gherkin format, naming, effort disclaimer | `story_text`, `vertical` |

Checks performed:
- Required sections present (Story, Scope, Technical, AC, Questions, Impact, Effort)
- Gherkin Given/When/Then format in Acceptance Criteria
- Minimum 2 scenarios (happy path + edge case)
- As a / I want / So that structure
- Persona field present
- AI-estimated effort disclaimer

### Dependency Graph

| Tool | Purpose | Key Args |
|------|---------|----------|
| `build_dependency_graph` | Build graph from story metadata (nodes + edges) | `stories` |
| `save_dependency_graph` | Persist graph to session directory | `session_id`, `graph` |

### Story Versioning

| Tool | Purpose | Key Args |
|------|---------|----------|
| `version_story` | Create new version with diff tracking and revision history | `story_file`, `new_text`, `change_summary` |

### Bulk Story Mode

| Tool | Purpose | Key Args |
|------|---------|----------|
| `decompose_scope_document` | Analyze scope doc, propose story boundaries (max 10) | `scope_file` |
| `generate_bulk_story_skeleton` | Generate skeleton markdown with cross-references | `stories`, `epic_name` |

## Session Artifacts

Each session creates a directory under `requirements/agent_sessions/{session_id}/`:

```
requirements/agent_sessions/20260330_143022_a1b2c3d4/
├── session_metadata.json          # Session ID, title, vertical, status, timestamps
├── interview_transcript.json      # Structured Q&A pairs with phase numbers
├── codebase_scan_results.json     # Discovered components, file paths, element counts
├── component_delta.json           # Proposed changes for deployment pipeline
└── story_dependency_graph.json    # Cross-story relationships (if applicable)
```

## Schemas

JSON schemas for machine-readable artifacts live in `mcp_server/schemas/`:

- `component_delta.json` — Schema for deployment pipeline consumption
- `story_dependency_graph.json` — Schema for cross-story dependency tracking

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `USA_WORKSPACE` | Parent of mcp_server/ | Workspace root (auto-detected) |

## System Permissions

This server **reads** files from:
- `force-app/` (OmniScript metadata, Apex classes, LWC)
- `requirements/` (existing stories, scope documents)
- `mcp_server/verticals/` (YAML configs)

This server **writes** files to:
- `requirements/agent_sessions/` (session artifacts)
- `requirements/*.md` (story versioning only, when explicitly called)

No network access required. No Salesforce org access (that's Phase III — SFDX integration).

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: fastmcp` | Run `pip install -r mcp_server/requirements.txt` |
| `force-app/ not found` | Set `USA_WORKSPACE` env var or run from project root |
| Session directory missing | Call `create_session` before other session tools |
| Lint reports false positives | Check story uses `**Given**` bold markdown format |
