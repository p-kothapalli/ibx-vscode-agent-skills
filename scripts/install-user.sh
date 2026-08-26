#!/usr/bin/env bash
# Install IBX agent skills into the Copilot user profile (~/.copilot/skills).
set -euo pipefail

FORCE=0
if [[ "${1:-}" == "--force" ]]; then
  FORCE=1
  shift
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${ROOT}/skills"
DEST="${HOME}/.copilot/skills"

if [[ ! -d "${SRC}" ]]; then
  echo "error: skills/ folder not found at ${SRC}" >&2
  echo "Run this script from a clone of ibx-vscode-agent-skills." >&2
  exit 1
fi

mkdir -p "${DEST}"

copied=0
skipped=0
for skill_dir in "${SRC}"/*; do
  [[ -d "${skill_dir}" ]] || continue
  [[ -f "${skill_dir}/SKILL.md" ]] || continue
  name="$(basename "${skill_dir}")"
  target="${DEST}/${name}"
  if [[ -e "${target}" && "${FORCE}" -ne 1 ]]; then
    echo "skip  ${name}  (exists; pass --force to overwrite)"
    skipped=$((skipped + 1))
    continue
  fi
  rm -rf "${target}"
  cp -R "${skill_dir}" "${target}"
  echo "install  ${name}  →  ${target}"
  copied=$((copied + 1))
done

echo
echo "Installed ${copied} skill(s) to ${DEST} (${skipped} skipped)."
echo
echo "Next:"
echo "  1. In VS Code: Cmd+Shift+P / Ctrl+Shift+P → Developer: Reload Window"
echo "  2. Open Copilot Chat in Agent mode"
echo "  3. Type /  and confirm you see /generating-apex, /user-story-architect, …"
echo "  4. Or run Chat: Open Customizations → Skills"
echo
echo "Docs: https://code.visualstudio.com/docs/agent-customization/agent-skills"
