#!/usr/bin/env bash
# Copy IBX agent skills + Copilot instruction templates into a Salesforce project.
set -euo pipefail

FORCE=0
if [[ "${1:-}" == "--force" ]]; then
  FORCE=1
  shift
fi

TARGET="${1:-}"
if [[ -z "${TARGET}" ]]; then
  echo "usage: $0 [--force] /path/to/salesforce-project" >&2
  exit 1
fi
if [[ ! -d "${TARGET}" ]]; then
  echo "error: target is not a directory: ${TARGET}" >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC_SKILLS="${ROOT}/skills"
SRC_INSTRUCTIONS="${ROOT}/templates/instructions"
SRC_MCP="${ROOT}/templates/mcp.json"

TARGET="$(cd "${TARGET}" && pwd)"
DEST_SKILLS="${TARGET}/.github/skills"
DEST_INSTRUCTIONS="${TARGET}/.github/instructions"
DEST_VSCODE="${TARGET}/.vscode"

mkdir -p "${DEST_SKILLS}" "${DEST_INSTRUCTIONS}" "${DEST_VSCODE}"

copied=0
for skill_dir in "${SRC_SKILLS}"/*; do
  [[ -d "${skill_dir}" ]] || continue
  [[ -f "${skill_dir}/SKILL.md" ]] || continue
  name="$(basename "${skill_dir}")"
  dest="${DEST_SKILLS}/${name}"
  if [[ -e "${dest}" && "${FORCE}" -ne 1 ]]; then
    echo "skip skill  ${name}"
    continue
  fi
  rm -rf "${dest}"
  cp -R "${skill_dir}" "${dest}"
  echo "skill  ${name}"
  copied=$((copied + 1))
done

if [[ -d "${SRC_INSTRUCTIONS}" ]]; then
  for f in "${SRC_INSTRUCTIONS}"/*.instructions.md; do
    [[ -f "${f}" ]] || continue
    base="$(basename "${f}")"
    dest="${DEST_INSTRUCTIONS}/${base}"
    if [[ -e "${dest}" && "${FORCE}" -ne 1 ]]; then
      echo "skip instruction  ${base}"
      continue
    fi
    cp "${f}" "${dest}"
    echo "instruction  ${base}"
  done
fi

if [[ -f "${SRC_MCP}" ]]; then
  if [[ -e "${DEST_VSCODE}/mcp.json" && "${FORCE}" -ne 1 ]]; then
    echo "skip  .vscode/mcp.json  (already exists; pass --force to overwrite)"
  else
    cp "${SRC_MCP}" "${DEST_VSCODE}/mcp.json"
    echo "wrote  .vscode/mcp.json"
  fi
fi

SETTINGS="${DEST_VSCODE}/settings.json"
if [[ ! -f "${SETTINGS}" ]]; then
  cat > "${SETTINGS}" <<'JSON'
{
  "chat.useAgentSkills": true
}
JSON
  echo "wrote  .vscode/settings.json"
else
  echo "note: left existing .vscode/settings.json unchanged — set \"chat.useAgentSkills\": true if needed"
fi

echo
echo "Installed ${copied} skill(s) into ${DEST_SKILLS}"
echo
echo "Next:"
echo "  1. Open ${TARGET} in VS Code"
echo "  2. Reload Window"
echo "  3. Copilot Chat → Agent mode → type /"
echo "  4. Optional: MCP: List Servers → start Salesforce DX and code-review-graph"
echo "  5. Commit .github/skills (and instructions) in the Salesforce repo if the team should share them"
