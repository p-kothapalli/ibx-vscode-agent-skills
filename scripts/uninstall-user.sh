#!/usr/bin/env bash
# Remove IBX agent skills that were copied into ~/.copilot/skills.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${ROOT}/skills"
DEST="${HOME}/.copilot/skills"

if [[ ! -d "${SRC}" ]]; then
  echo "error: skills/ folder not found at ${SRC}" >&2
  exit 1
fi
if [[ ! -d "${DEST}" ]]; then
  echo "nothing to uninstall (${DEST} does not exist)"
  exit 0
fi

removed=0
for skill_dir in "${SRC}"/*; do
  [[ -d "${skill_dir}" ]] || continue
  name="$(basename "${skill_dir}")"
  target="${DEST}/${name}"
  if [[ -d "${target}" ]]; then
    rm -rf "${target}"
    echo "removed  ${target}"
    removed=$((removed + 1))
  fi
done

echo
echo "Removed ${removed} skill folder(s) from ${DEST}."
echo "Reload VS Code (Developer: Reload Window) for Copilot to drop them."
