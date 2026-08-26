# Evaluations — User Story Solution Architect

Evaluations are the source of truth for whether this skill actually works. Per
the [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices),
build evaluations before extending documentation, run them across the models you
use (Haiku, Sonnet, Opus), and iterate on failures.

There is no built-in runner. Use these scenarios manually or in your own harness:
give a fresh agent (with this skill loaded) the `query`, provide any `files`, then
score the output against every item in `expected_behavior` (pass = all items met).

## Scenarios

| File | Mode | Exercises |
|------|------|-----------|
| `eval-01-par-enhancement.json` | New Feature (PNM) | Pattern A GWT ACs, persona contract, graph-first verification, Technical Implementation split |
| `eval-02-field-creation.json` | New Feature (PNM) | Pattern B (field creation) + Pattern C (permission sets), no GWT forced |
| `eval-03-epic-breakdown.json` | Epic Breakdown | Decomposition plan approval, cross-references, dependency ordering, per-story contract compliance |

## How to score

For each scenario, the run **passes** only if every `expected_behavior` bullet is
satisfied. Common failure modes to watch for:

- Persona is "user"/"business user"/"developer"/"system" (RULE 12 violation).
- Apex class names / IP versions / SOQL / API field names inside a Pattern-A
  Given/When/Then (RULE 13 violation).
- Missing `## Technical Implementation (high-level)` section (RULE 14).
- Component names invented instead of verified via `code-review-graph`.
- Missing Definition of done or Estimated Effort.

Record results per model. When a run fails, refine SKILL.md or the referenced
files, then re-run.
