---
applyTo: "**"
---

# Graph-first codebase exploration

Never start with workspace search, file search, or reading whole XML/JSON files to discover structure **if** the `code-review-graph` MCP server is connected.

| Task | Use first | Fall back only if the graph returns nothing |
|---|---|---|
| Find a function / class / OmniStudio asset | `semantic_search_nodes` | workspace search |
| Who calls a component | `query_graph` (`callers_of`) | workspace search |
| What a component calls | `query_graph` (`callees_of`) | read the file |
| Blast radius | `get_impact_radius` | manual search |
| Review current edits | `detect_changes` + `get_review_context` | read the file |
| Tests for a component | `query_graph` (`tests_for`) | search test dirs |
| Architecture | `get_architecture_overview` | read multiple files |

If `code-review-graph` is not configured or errors, say so briefly and fall back to Copilot workspace search. Do not invent callers or component names.
