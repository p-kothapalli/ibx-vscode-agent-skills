#!/usr/bin/env python3
"""Copy Cursor skills and rewire SKILL.md files for GitHub Copilot in VS Code."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

SRC = Path("/Users/pkothapalli/Documents/IBXQA/IBXQA/.cursor/skills")
DEST_ROOT = Path(__file__).resolve().parent.parent
DEST = DEST_ROOT / "skills"

VSCODE_NOTE = """\
> **VS Code / Copilot:** Follow the [Agent Skills](https://agentskills.io/specification) standard.
> Ask clarifying questions as a **numbered list in Copilot Chat** and wait for the user's reply
> (there is no Cursor `AskQuestion` tool). Explore the codebase with the `code-review-graph` MCP
> tools first if they are configured; otherwise use Copilot workspace search / file search / file read.
> MCP servers live in `.vscode/mcp.json`. Invoke this skill with `/{name}` if it does not auto-load.
"""

BODY_REPLACEMENTS = [
    (r"\.cursor/mcp\.json", ".vscode/mcp.json"),
    (r"\.cursor/skills/", ".github/skills/"),
    (
        r"\.cursor/rules/code-review-graph-first\.mdc",
        ".github/instructions/code-review-graph-first.instructions.md",
    ),
    (
        r"\.cursor/rules/soql-queries-archive\.mdc",
        ".github/instructions/soql-queries-archive.instructions.md",
    ),
    (r"\.cursor/AGENTS\.md", "AGENTS.md"),
    (
        r"MCP/Cursor wiring",
        "MCP / Copilot wiring",
    ),
    (
        r"for Cursor MCP",
        "for VS Code Copilot MCP",
    ),
    (
        r"via the `AskQuestion` tool",
        "as a numbered list in Copilot Chat",
    ),
    (
        r"via `AskQuestion`",
        "in Copilot Chat as numbered options",
    ),
    (
        r"a single `AskQuestion` call",
        "a single Copilot Chat message with numbered options",
    ),
    (
        r"the `AskQuestion` tool",
        "a numbered list in Copilot Chat",
    ),
    (
        r"`AskQuestion` tool",
        "Copilot Chat numbered-options prompt",
    ),
    (
        r"via AskQuestion",
        "in Copilot Chat as numbered options",
    ),
    (
        r"ask via `AskQuestion`",
        "ask in Copilot Chat as numbered options",
    ),
    (
        r"Grep/Glob/Read",
        "workspace search / file search / file read",
    ),
    (
        r"Grep / Glob / Read",
        "workspace search / file search / file read",
    ),
    (
        r"Glob / Grep",
        "workspace file search",
    ),
    (
        r"Grep \+ Read",
        "workspace search + file read",
    ),
    (
        r"Reload Cursor so it re-scans",
        "Reload VS Code so Copilot re-scans",
    ),
    (
        r"Cursor auto-invokes",
        "Copilot auto-loads",
    ),
    (
        r"Cursor auto-discovers",
        "Copilot discovers",
    ),
]


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    if not m:
        return {}, text
    raw = m.group(1)
    body = text[m.end() :]
    if yaml is not None:
        data = yaml.safe_load(raw) or {}
    else:
        data = {}
        for line in raw.splitlines():
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip().strip('"')
    return data, body


def dump_frontmatter(data: dict) -> str:
    # Preserve readable YAML without requiring pyyaml dump quirks for multiline.
    if yaml is not None:
        dumped = yaml.safe_dump(
            data,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
            width=88,
        )
        return dumped
    lines = []
    for k, v in data.items():
        if isinstance(v, (dict, list)):
            lines.append(f"{k}: {v!r}")
        else:
            lines.append(f"{k}: {v}")
    return "\n".join(lines) + "\n"


def transform_frontmatter(fm: dict, folder_name: str) -> dict:
    extra_keys = [
        k
        for k in list(fm)
        if k
        not in {
            "name",
            "description",
            "license",
            "compatibility",
            "metadata",
            "allowed-tools",
            "user-invocable",
            "disable-model-invocation",
            "argument-hint",
            "context",
        }
    ]
    metadata = dict(fm.get("metadata") or {})
    if not isinstance(metadata, dict):
        metadata = {"value": str(metadata)}
    for k in extra_keys:
        metadata[k] = fm.pop(k)
    metadata.setdefault("source", "IBXEnhancements .cursor/skills")
    metadata.setdefault("host", "vscode-copilot")
    fm["name"] = folder_name
    fm["metadata"] = metadata
    fm.setdefault(
        "compatibility",
        "GitHub Copilot in VS Code (Agent mode) or Copilot CLI. Optional MCP: code-review-graph, Salesforce DX.",
    )
    fm.setdefault("user-invocable", True)
    hints = {
        "generating-apex": "[class type] [object or goal]",
        "generating-apex-test": "[Apex class to test]",
        "generating-lwc-components": "[component name or OmniScript LWC]",
        "generating-custom-field": "[object] [field type and purpose]",
        "generating-custom-object": "[object purpose]",
        "querying-soql": "[object or question the query should answer]",
        "running-apex-tests": "[test class or --tests list]",
        "running-code-analyzer": "[path under force-app/]",
        "deploying-metadata": "[metadata type or source path]",
        "user-story-architect": "[feature, bug, or epic to story]",
        "lsc-user-story-architect": "[LSC feature or Veeva migration story]",
        "building-omnistudio-omniscript": "[form or OmniScript name]",
        "building-omnistudio-integration-procedure": "[IP name or orchestration goal]",
        "building-omnistudio-datamapper": "[Extract/Transform/Load and objects]",
        "debugging-apex-logs": "[user, request id, or reproduction]",
        "verifying-practitioner-build": "[epic, service, or batch under review]",
    }
    if folder_name in hints:
        fm.setdefault("argument-hint", hints[folder_name])
    return fm


def transform_body(body: str, name: str) -> str:
    text = body
    for pat, repl in BODY_REPLACEMENTS:
        text = re.sub(pat, repl, text)
    # Avoid double-injecting on re-run.
    if "VS Code / Copilot:" not in text:
        note = VSCODE_NOTE.format(name=name)
        # Insert after the first markdown heading, or at the top.
        m = re.search(r"^# .+$", text, re.M)
        if m:
            insert_at = m.end()
            text = text[:insert_at] + "\n\n" + note + text[insert_at:]
        else:
            text = note + "\n" + text
    return text


def copy_tree() -> None:
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    for src_dir in sorted(p for p in SRC.iterdir() if p.is_dir()):
        if not (src_dir / "SKILL.md").exists():
            continue
        dest_dir = DEST / src_dir.name
        shutil.copytree(
            src_dir,
            dest_dir,
            ignore=shutil.ignore_patterns(".DS_Store"),
        )


def rewire() -> list[str]:
    warnings: list[str] = []
    for skill_dir in sorted(p for p in DEST.iterdir() if p.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        original = skill_md.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(original)
        fm = transform_frontmatter(fm, skill_dir.name)
        desc = str(fm.get("description") or "")
        if len(desc) > 1024:
            warnings.append(f"{skill_dir.name}: description is {len(desc)} chars (max 1024)")
        body = transform_body(body, skill_dir.name)
        out = "---\n" + dump_frontmatter(fm) + "---\n" + body
        if not body.startswith("\n"):
            out = "---\n" + dump_frontmatter(fm) + "---\n\n" + body.lstrip("\n")
        skill_md.write_text(out, encoding="utf-8")
    return warnings


def main() -> int:
    if not SRC.exists():
        print(f"Source skills not found: {SRC}", file=sys.stderr)
        return 1
    copy_tree()
    warnings = rewire()
    skills = sorted(p.name for p in DEST.iterdir() if p.is_dir() and (p / "SKILL.md").exists())
    print(f"Rewired {len(skills)} skills → {DEST}")
    for w in warnings:
        print("WARNING:", w)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
