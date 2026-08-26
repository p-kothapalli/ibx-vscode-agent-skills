# Evaluations — LSC User Story Solution Architect

Evaluations are the source of truth for whether this skill actually works. Build
evaluations before extending documentation, run them across the models you use
(Haiku, Sonnet, Opus), and iterate on failures.

There is no built-in runner. Use these scenarios manually or in your own harness:
give a fresh agent (with this skill loaded) the `query`, provide any `files`, then
score the output against every item in `expected_behavior` (pass = all items met).

## Scenarios

| File | Mode | Exercises |
|------|------|-----------|
| `eval-01-veeva-migration.json` | Veeva→LSC Migration | Terminology translation, persona correction (field user, not HCP), Pattern A + Pattern E, Veeva Source header |
| `eval-02-sample-drop.json` | New Feature (Commercial) | Pattern A GWT + mandatory Pattern E record spec, negative ACs (over-disbursement, ineligible HCP), greenfield "proposed" components |
| `eval-03-field-creation.json` | New Feature (field/perm) | Pattern B (field creation) + Pattern C (permission sets), no GWT forced |

## How to score

For each scenario, the run **passes** only if every `expected_behavior` bullet is
satisfied. Common failure modes to watch for:

- Persona is "user"/"business user"/"system", or **"HCP" used as the login
  persona** for an internal feature (RULE 12 violation).
- Apex class names / IP versions / SOQL / API field names inside a Pattern-A
  Given/When/Then (RULE 13 violation).
- Missing `## Technical Implementation (high-level)` section (RULE 14).
- "records created/updated" outcome with no Pattern E field spec (RULE 15).
- Veeva terminology retained in the story body during a migration (STEP 0).
- Component/object names invented instead of verified or marked *proposed*.
- Missing Definition of done or Estimated Effort.

Record results per model. When a run fails, refine SKILL.md or the referenced
files, then re-run.
