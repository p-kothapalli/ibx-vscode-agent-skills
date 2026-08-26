#!/usr/bin/env python3
"""Write package.json with a chatSkills contribution for every skill folder."""

import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
skills = sorted(
    p.name
    for p in (root / "skills").iterdir()
    if p.is_dir() and (p / "SKILL.md").exists()
)

manifest = {
    "name": "ibx-vscode-agent-skills",
    "displayName": "IBX Salesforce Agent Skills",
    "description": "IBX Salesforce agent skills for GitHub Copilot in VS Code (Apex, OmniStudio, Data Cloud, user stories).",
    "version": "1.0.0",
    "publisher": "pkothapalli",
    "license": "SEE LICENSE IN LICENSE",
    "engines": {"vscode": "^1.100.0"},
    "categories": ["Machine Learning", "Other"],
    "keywords": [
        "salesforce",
        "copilot",
        "agent-skills",
        "omnistudio",
        "apex",
        "ibx",
    ],
    "activationEvents": [],
    "main": "./extension.js",
    "contributes": {
        "chatSkills": [
            {"path": f"./skills/{name}/SKILL.md"} for name in skills
        ]
    },
}

(root / "package.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(f"Wrote package.json with {len(skills)} chatSkills")
