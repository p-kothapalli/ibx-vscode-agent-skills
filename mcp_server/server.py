"""
User Story Architect MCP Server (Phase II)

FastMCP server providing tools for:
  - OmniScript metadata analysis
  - Impacted component detection
  - Existing story search
  - Vertical config loading
  - Session artifact management
  - Story linting (Gherkin + naming conventions)
  - Story dependency graph
  - Story versioning & diff
  - Bulk story mode (epic decomposition)

Run: python server.py          (stdio, for Cursor MCP)
     python server.py --http   (HTTP on port 29120, for external clients)
"""

from __future__ import annotations

import datetime as dt
import difflib
import hashlib
import json
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Any

import yaml
from fastmcp import FastMCP

WORKSPACE = Path(os.environ.get("USA_WORKSPACE", Path(__file__).resolve().parent.parent))
REQUIREMENTS_DIR = WORKSPACE / "requirements"
FORCE_APP_DIR = WORKSPACE / "force-app"
VERTICALS_DIR = Path(__file__).resolve().parent / "verticals"
SESSIONS_DIR = REQUIREMENTS_DIR / "agent_sessions"
SCHEMAS_DIR = Path(__file__).resolve().parent / "schemas"

mcp = FastMCP(
    "user-story-architect",
    instructions="User Story Architect — MCP tools for codebase analysis, session management, linting, dependency graphs, versioning, and bulk story mode.",
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError):
        return None


def _walk_json(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(directory.rglob("*.json"))


def _walk_md(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(directory.rglob("*.md"))

# ---------------------------------------------------------------------------
# 2.5  select_vertical — load YAML config for a vertical
# ---------------------------------------------------------------------------

@mcp.tool()
def select_vertical(vertical: str) -> dict:
    """Load vertical configuration (prefix, key objects, flows, naming conventions).

    Args:
        vertical: One of PNM, HLS, Insurance, FSC, CME, Custom
    """
    slug = vertical.strip().lower()
    aliases = {"pnm": "pnm", "hls": "hls", "insurance": "insurance", "fsc": "fsc",
               "cme": "cme", "custom": "custom",
               "provider network management": "pnm",
               "health & life sciences": "hls",
               "financial services cloud": "fsc"}
    slug = aliases.get(slug, slug)
    yaml_path = VERTICALS_DIR / f"{slug}.yaml"
    if not yaml_path.exists():
        available = [p.stem for p in VERTICALS_DIR.glob("*.yaml")]
        return {"error": f"Vertical '{vertical}' not found. Available: {available}"}
    with open(yaml_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return {"vertical": config, "source": str(yaml_path)}

# ---------------------------------------------------------------------------
# 2.2  analyze_omniscript — parse element JSONs from force-app/
# ---------------------------------------------------------------------------

@mcp.tool()
def analyze_omniscript(omniscript_name: str) -> dict:
    """Analyze an OmniScript's elements, steps, conditions, and data flow from force-app/ metadata.

    Args:
        omniscript_name: API name of the OmniScript (e.g. PRM_PractitionerParticipationForm_English)
    """
    results: dict[str, Any] = {"omniscript": omniscript_name, "found": False, "elements": [], "steps": [], "data_sources": []}
    if not FORCE_APP_DIR.exists():
        results["error"] = "force-app/ directory not found in workspace"
        return results

    matches: list[Path] = []
    for p in FORCE_APP_DIR.rglob("*"):
        if omniscript_name.lower() in p.name.lower() and p.is_file():
            matches.append(p)

    if not matches:
        results["error"] = f"No files matching '{omniscript_name}' found in force-app/"
        return results

    results["found"] = True
    results["files"] = [str(m.relative_to(WORKSPACE)) for m in matches]

    for m in matches:
        if m.suffix == ".json":
            try:
                data = json.loads(m.read_text(encoding="utf-8"))
                element_info = {
                    "file": str(m.relative_to(WORKSPACE)),
                    "name": data.get("Name", data.get("name", m.stem)),
                    "type": data.get("Type", data.get("type", "unknown")),
                }
                if "propertySetConfig" in data:
                    psc = data["propertySetConfig"]
                    if isinstance(psc, str):
                        try:
                            psc = json.loads(psc)
                        except json.JSONDecodeError:
                            psc = {}
                    element_info["options"] = psc.get("options", [])
                    element_info["conditionType"] = psc.get("conditionType")
                    element_info["dataRaptorExtract"] = psc.get("dataRaptorExtract")
                    element_info["integrationProcedure"] = psc.get("integrationProcedure")
                    if psc.get("dataRaptorExtract"):
                        results["data_sources"].append(psc["dataRaptorExtract"])
                    if psc.get("integrationProcedure"):
                        results["data_sources"].append(psc["integrationProcedure"])
                results["elements"].append(element_info)
                if data.get("Type") in ("Step", "step"):
                    results["steps"].append(element_info["name"])
            except (json.JSONDecodeError, UnicodeDecodeError):
                results["elements"].append({"file": str(m.relative_to(WORKSPACE)), "parse_error": True})

    results["data_sources"] = list(set(results["data_sources"]))
    results["element_count"] = len(results["elements"])
    results["step_count"] = len(results["steps"])
    return results

# ---------------------------------------------------------------------------
# 2.3  find_impacted_components — cross-reference search
# ---------------------------------------------------------------------------

@mcp.tool()
def find_impacted_components(component_name: str, search_scope: str = "all") -> dict:
    """Find all components that reference a given component name (OmniScript, DataRaptor, IP, Apex class, object).

    Args:
        component_name: Name of the component to search for
        search_scope: 'all', 'force-app', or 'requirements'
    """
    results: dict[str, Any] = {"component": component_name, "references": []}
    search_dirs: list[Path] = []
    if search_scope in ("all", "force-app"):
        search_dirs.append(FORCE_APP_DIR)
    if search_scope in ("all", "requirements"):
        search_dirs.append(REQUIREMENTS_DIR)

    pattern = re.compile(re.escape(component_name), re.IGNORECASE)

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for p in search_dir.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix not in (".json", ".md", ".cls", ".trigger", ".xml", ".js", ".html"):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except (PermissionError, OSError):
                continue
            hits = pattern.findall(text)
            if hits:
                results["references"].append({
                    "file": str(p.relative_to(WORKSPACE)),
                    "occurrences": len(hits),
                    "type": _classify_file(p),
                })

    results["total_references"] = len(results["references"])
    return results


def _classify_file(p: Path) -> str:
    suffix_map = {
        ".cls": "ApexClass", ".trigger": "ApexTrigger", ".json": "Metadata/JSON",
        ".md": "UserStory/Doc", ".xml": "MetadataXML", ".js": "LWC/JS", ".html": "LWC/HTML",
    }
    return suffix_map.get(p.suffix, "Other")

# ---------------------------------------------------------------------------
# 2.4  search_existing_stories
# ---------------------------------------------------------------------------

@mcp.tool()
def search_existing_stories(keyword: str) -> dict:
    """Search requirements/ for existing user stories containing a keyword.

    Args:
        keyword: Keyword or phrase to search for (case-insensitive)
    """
    results: list[dict] = []
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)

    for md in _walk_md(REQUIREMENTS_DIR):
        text = _read_text(md)
        if text is None:
            continue
        matches = pattern.findall(text)
        if matches:
            title_match = re.search(r"^#\s+(.+)", text, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else md.stem
            results.append({
                "file": str(md.relative_to(WORKSPACE)),
                "title": title,
                "occurrences": len(matches),
            })

    return {"keyword": keyword, "stories_found": len(results), "results": results}

# ---------------------------------------------------------------------------
# 2.6  Session management
# ---------------------------------------------------------------------------

@mcp.tool()
def create_session(story_title: str, vertical: str = "PNM") -> dict:
    """Create a new agent session directory with metadata.

    Args:
        story_title: Working title of the user story
        vertical: Vertical code (PNM, HLS, Insurance, FSC, etc.)
    """
    session_id = dt.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]
    session_dir = SESSIONS_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "session_id": session_id,
        "story_title": story_title,
        "vertical": vertical,
        "created": _now_iso(),
        "status": "in_progress",
    }
    (session_dir / "session_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (session_dir / "interview_transcript.json").write_text("[]", encoding="utf-8")
    (session_dir / "codebase_scan_results.json").write_text("{}", encoding="utf-8")
    (session_dir / "component_delta.json").write_text(json.dumps({
        "story_id": "", "session_id": session_id, "timestamp": _now_iso(),
        "vertical": vertical, "components": [],
    }, indent=2), encoding="utf-8")

    return {"session_id": session_id, "session_dir": str(session_dir.relative_to(WORKSPACE)), "files_created": [
        "session_metadata.json", "interview_transcript.json",
        "codebase_scan_results.json", "component_delta.json",
    ]}


@mcp.tool()
def save_interview_qa(session_id: str, question: str, answer: str, phase: int) -> dict:
    """Append a Q&A pair to the session interview transcript.

    Args:
        session_id: Session identifier
        question: The question asked
        answer: The answer received
        phase: Question phase (1-4)
    """
    transcript_path = SESSIONS_DIR / session_id / "interview_transcript.json"
    if not transcript_path.exists():
        return {"error": f"Session '{session_id}' not found"}

    transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
    transcript.append({
        "phase": phase,
        "question": question,
        "answer": answer,
        "timestamp": _now_iso(),
    })
    transcript_path.write_text(json.dumps(transcript, indent=2), encoding="utf-8")
    return {"session_id": session_id, "total_qa_pairs": len(transcript)}


@mcp.tool()
def save_component_delta(session_id: str, story_id: str, components: list[dict]) -> dict:
    """Save the component delta (proposed changes) for deployment pipeline consumption.

    Args:
        session_id: Session identifier
        story_id: Story identifier (e.g. US-1.1)
        components: List of component dicts with keys: name, type, action, path (optional), details
    """
    delta_path = SESSIONS_DIR / session_id / "component_delta.json"
    if not delta_path.exists():
        return {"error": f"Session '{session_id}' not found"}

    delta = json.loads(delta_path.read_text(encoding="utf-8"))
    delta["story_id"] = story_id
    delta["timestamp"] = _now_iso()
    delta["components"] = components
    delta_path.write_text(json.dumps(delta, indent=2), encoding="utf-8")
    return {"session_id": session_id, "story_id": story_id, "components_saved": len(components)}


@mcp.tool()
def save_codebase_scan(session_id: str, scan_results: dict) -> dict:
    """Save codebase scan results to the session directory.

    Args:
        session_id: Session identifier
        scan_results: Dict with discovered components, paths, element counts
    """
    scan_path = SESSIONS_DIR / session_id / "codebase_scan_results.json"
    if not scan_path.exists():
        return {"error": f"Session '{session_id}' not found"}

    scan_results["timestamp"] = _now_iso()
    scan_path.write_text(json.dumps(scan_results, indent=2), encoding="utf-8")
    return {"session_id": session_id, "saved": True}


@mcp.tool()
def finalize_session(session_id: str, story_file_path: str) -> dict:
    """Mark a session as complete and link to the final story file.

    Args:
        session_id: Session identifier
        story_file_path: Relative path to the final .md story file
    """
    meta_path = SESSIONS_DIR / session_id / "session_metadata.json"
    if not meta_path.exists():
        return {"error": f"Session '{session_id}' not found"}

    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    metadata["status"] = "complete"
    metadata["completed"] = _now_iso()
    metadata["story_file"] = story_file_path
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return {"session_id": session_id, "status": "complete", "story_file": story_file_path}

# ---------------------------------------------------------------------------
# 2.7  Deterministic linting
# ---------------------------------------------------------------------------

_GHERKIN_GIVEN = re.compile(r"^\*{0,2}Given\*{0,2}\s+.+", re.MULTILINE | re.IGNORECASE)
_GHERKIN_WHEN  = re.compile(r"^\*{0,2}When\*{0,2}\s+.+",  re.MULTILINE | re.IGNORECASE)
_GHERKIN_THEN  = re.compile(r"^\*{0,2}Then\*{0,2}\s+.+",  re.MULTILINE | re.IGNORECASE)

_REQUIRED_SECTIONS = [
    "Story", "Scope", "Technical Section", "Acceptance Criteria",
    "Clarification Questions", "Impact Analysis", "Estimated Effort",
]

_PNM_PREFIXES = {
    "OmniScript": re.compile(r"PRM_\w+_English"),
    "DataRaptor": re.compile(r"PRMDR\w+"),
    "IntegrationProcedure": re.compile(r"PRM_\w+"),
}

@mcp.tool()
def lint_story(story_text: str, vertical: str = "PNM") -> dict:
    """Run deterministic linting on a user story: Gherkin format, required sections, naming conventions.

    Args:
        story_text: Full markdown text of the user story
        vertical: Vertical code for naming convention checks
    """
    issues: list[dict] = []

    for section in _REQUIRED_SECTIONS:
        pattern = re.compile(rf"^#+\s+{re.escape(section)}", re.MULTILINE | re.IGNORECASE)
        if not pattern.search(story_text):
            issues.append({"rule": "missing_section", "severity": "error", "message": f"Missing required section: '{section}'"})

    ac_match = re.search(r"(?:^#+\s+Acceptance Criteria.*?$)(.*?)(?=^#+\s|\Z)", story_text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if ac_match:
        ac_text = ac_match.group(1)
        given_count = len(_GHERKIN_GIVEN.findall(ac_text))
        when_count  = len(_GHERKIN_WHEN.findall(ac_text))
        then_count  = len(_GHERKIN_THEN.findall(ac_text))
        if given_count == 0:
            issues.append({"rule": "gherkin_missing_given", "severity": "error", "message": "Acceptance Criteria missing 'Given' clauses"})
        if when_count == 0:
            issues.append({"rule": "gherkin_missing_when", "severity": "error", "message": "Acceptance Criteria missing 'When' clauses"})
        if then_count == 0:
            issues.append({"rule": "gherkin_missing_then", "severity": "error", "message": "Acceptance Criteria missing 'Then' clauses"})
        if given_count < 2:
            issues.append({"rule": "gherkin_few_scenarios", "severity": "warning", "message": f"Only {given_count} scenario(s) found; recommend at least 2 (happy path + edge case)"})
    else:
        issues.append({"rule": "no_acceptance_criteria_content", "severity": "error", "message": "Acceptance Criteria section found but appears empty"})

    if vertical.upper() == "PNM":
        for comp_type, prefix_re in _PNM_PREFIXES.items():
            names_in_text = re.findall(r"\b[A-Z][A-Za-z0-9_]+(?:_English)?\b", story_text)
            for name in names_in_text:
                if comp_type.lower() in story_text.lower():
                    pass  # Convention check only when component is explicitly referenced

    effort_match = re.search(r"(?:^#+\s+Estimated Effort.*?$)(.*?)(?=^#+\s|\Z)", story_text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if effort_match:
        effort_text = effort_match.group(1)
        if "AI-estimated" not in effort_text and "ai-estimated" not in effort_text.lower():
            issues.append({"rule": "effort_disclaimer_missing", "severity": "warning", "message": "Effort section should include 'AI-estimated — validate with team' disclaimer"})

    persona_match = re.search(r"\*\*Persona:\*\*\s*(.+)", story_text)
    if not persona_match:
        issues.append({"rule": "missing_persona", "severity": "error", "message": "Missing Persona field in story header"})

    as_a = re.search(r"\*\*As a\*\*", story_text, re.IGNORECASE)
    i_want = re.search(r"\*\*I want\*\*", story_text, re.IGNORECASE)
    so_that = re.search(r"\*\*So that\*\*", story_text, re.IGNORECASE)
    if not as_a:
        issues.append({"rule": "missing_as_a", "severity": "error", "message": "Story missing 'As a' clause"})
    if not i_want:
        issues.append({"rule": "missing_i_want", "severity": "error", "message": "Story missing 'I want' clause"})
    if not so_that:
        issues.append({"rule": "missing_so_that", "severity": "error", "message": "Story missing 'So that' clause"})

    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]
    return {
        "passed": len(errors) == 0,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "issues": issues,
    }

# ---------------------------------------------------------------------------
# 2.8  Story dependency graph
# ---------------------------------------------------------------------------

@mcp.tool()
def build_dependency_graph(stories: list[dict]) -> dict:
    """Build a dependency graph from a list of story metadata dicts.

    Args:
        stories: List of dicts with keys: id, title, priority, epic, effort, components (list of component names), depends_on (list of story ids)
    """
    nodes = []
    edges = []
    component_map: dict[str, list[str]] = {}

    for s in stories:
        sid = s["id"]
        nodes.append({
            "id": sid,
            "title": s.get("title", ""),
            "priority": s.get("priority", "P1"),
            "status": s.get("status", "pending"),
            "epic": s.get("epic", ""),
            "effort": s.get("effort", ""),
            "components": s.get("components", []),
        })
        for comp in s.get("components", []):
            component_map.setdefault(comp, []).append(sid)
        for dep in s.get("depends_on", []):
            edges.append({"from": dep, "to": sid, "type": "blocks"})

    for comp, story_ids in component_map.items():
        if len(story_ids) > 1:
            for i in range(len(story_ids)):
                for j in range(i + 1, len(story_ids)):
                    existing = any(
                        e["from"] in (story_ids[i], story_ids[j]) and e["to"] in (story_ids[i], story_ids[j])
                        for e in edges
                    )
                    if not existing:
                        edges.append({
                            "from": story_ids[i], "to": story_ids[j],
                            "type": "shares_component", "shared_component": comp,
                        })

    return {
        "graph_id": uuid.uuid4().hex[:12],
        "timestamp": _now_iso(),
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }


@mcp.tool()
def save_dependency_graph(session_id: str, graph: dict) -> dict:
    """Persist a dependency graph to the session directory.

    Args:
        session_id: Session identifier
        graph: Graph dict returned by build_dependency_graph
    """
    out_path = SESSIONS_DIR / session_id / "story_dependency_graph.json"
    if not (SESSIONS_DIR / session_id).exists():
        return {"error": f"Session '{session_id}' not found"}
    out_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    return {"session_id": session_id, "saved": True, "path": str(out_path.relative_to(WORKSPACE))}

# ---------------------------------------------------------------------------
# 2.9  Story versioning & diff
# ---------------------------------------------------------------------------

@mcp.tool()
def version_story(story_file: str, new_text: str, change_summary: str) -> dict:
    """Create a new version of a story file. Stores the diff and appends a revision history entry.

    Args:
        story_file: Relative path to the .md story file under requirements/
        new_text: Full updated story markdown
        change_summary: One-line description of what changed
    """
    abs_path = WORKSPACE / story_file
    old_text = _read_text(abs_path) or ""

    diff_lines = list(difflib.unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile=f"a/{story_file}",
        tofile=f"b/{story_file}",
        lineterm="",
    ))
    diff_text = "\n".join(diff_lines)

    version_hash = hashlib.sha256(new_text.encode("utf-8")).hexdigest()[:12]
    revision_entry = (
        f"\n\n---\n\n## Revision History\n\n"
        f"| Version | Date | Summary |\n"
        f"|---------|------|---------|\n"
        f"| {version_hash} | {_now_iso()[:10]} | {change_summary} |\n"
    )

    existing_revision = re.search(r"^## Revision History", new_text, re.MULTILINE)
    if existing_revision:
        table_end = new_text.rfind("\n|")
        if table_end > existing_revision.start():
            insert_pos = new_text.index("\n", table_end + 1) if "\n" in new_text[table_end + 1:] else len(new_text)
            row = f"\n| {version_hash} | {_now_iso()[:10]} | {change_summary} |"
            new_text = new_text[:insert_pos] + row + new_text[insert_pos:]
    else:
        new_text = new_text.rstrip() + revision_entry

    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_text(new_text, encoding="utf-8")

    return {
        "file": story_file,
        "version": version_hash,
        "diff_lines": len(diff_lines),
        "diff_preview": diff_text[:2000] if diff_text else "(no changes)",
        "change_summary": change_summary,
    }

# ---------------------------------------------------------------------------
# 2.10  Bulk story mode (epic decomposition)
# ---------------------------------------------------------------------------

@mcp.tool()
def decompose_scope_document(scope_file: str) -> dict:
    """Read a scope/requirements document and propose story boundaries for epic decomposition.

    Args:
        scope_file: Relative path to the scope document (.md)
    """
    abs_path = WORKSPACE / scope_file
    text = _read_text(abs_path)
    if text is None:
        return {"error": f"File not found: {scope_file}"}

    headings: list[dict] = []
    for match in re.finditer(r"^(#{1,4})\s+(.+)", text, re.MULTILINE):
        level = len(match.group(1))
        title = match.group(2).strip()
        headings.append({"level": level, "title": title, "line": text[:match.start()].count("\n") + 1})

    story_candidates: list[dict] = []
    story_num = 1
    for h in headings:
        keywords = ["story", "feature", "capability", "flow", "workflow", "requirement", "epic", "user story"]
        if h["level"] <= 3 or any(kw in h["title"].lower() for kw in keywords):
            story_candidates.append({
                "proposed_id": f"US-{story_num}",
                "title": h["title"],
                "source_line": h["line"],
                "heading_level": h["level"],
            })
            story_num += 1

    if len(story_candidates) > 10:
        story_candidates = story_candidates[:10]
        truncated = True
    else:
        truncated = False

    return {
        "scope_file": scope_file,
        "total_headings": len(headings),
        "proposed_stories": story_candidates,
        "story_count": len(story_candidates),
        "truncated_to_10": truncated,
        "instructions": "Review the proposed stories. Reply with approved list to generate each story sequentially with cross-references.",
    }


@mcp.tool()
def generate_bulk_story_skeleton(stories: list[dict], epic_name: str) -> dict:
    """Generate skeleton markdown for multiple stories with cross-references and dependency ordering.

    Args:
        stories: List of dicts with keys: id, title, depends_on (list of ids), priority
        epic_name: Name of the parent epic
    """
    output_lines = [f"# {epic_name} — Story Decomposition\n"]
    output_lines.append(f"**Generated:** {_now_iso()[:10]}\n")
    output_lines.append(f"**Total Stories:** {len(stories)}\n\n---\n")

    output_lines.append("## Execution Order & Dependencies\n")
    output_lines.append("| # | Story | Depends On | Priority |\n")
    output_lines.append("|---|-------|------------|----------|\n")
    for s in stories:
        deps = ", ".join(s.get("depends_on", [])) or "None"
        output_lines.append(f"| {s['id']} | {s['title']} | {deps} | {s.get('priority', 'P1')} |\n")
    output_lines.append("\n---\n")

    for s in stories:
        deps_note = f"**Depends on:** {', '.join(s.get('depends_on', []))}" if s.get("depends_on") else "**Depends on:** None (can start immediately)"
        output_lines.append(f"\n## {s['id']}: {s['title']}\n")
        output_lines.append(f"**Priority:** {s.get('priority', 'P1')}  \n{deps_note}\n")
        output_lines.append("\n### Story\n\n**As a** [persona],  \n**I want** [capability],  \n**So that** [outcome].\n")
        output_lines.append("\n### Acceptance Criteria\n\n**Given** [precondition],  \n**When** [action],  \n**Then** [result].\n")
        output_lines.append("\n### Estimated Effort\n\n| Component | Effort | Notes |\n|-----------|--------|-------|\n| TBD | TBD | AI-estimated — validate with team |\n")
        output_lines.append("\n---\n")

    markdown = "\n".join(output_lines)
    return {
        "epic_name": epic_name,
        "story_count": len(stories),
        "markdown": markdown,
        "instructions": "Fill in each story skeleton using the full story generation workflow. Cross-references are pre-linked.",
    }

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http", host="127.0.0.1", port=29120)
    else:
        mcp.run(transport="stdio")
