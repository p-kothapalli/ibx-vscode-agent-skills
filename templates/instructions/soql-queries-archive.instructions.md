---
applyTo: "**"
---

# SOQL query archive

Whenever the user asks for a SOQL query, or you produce one they could run in the org, also save it under `requirements/SOQL/`.

- Create the folder if it is missing.
- File name: `YYYY-MM-DD_<TopicInPascalCase>.md` (append to today's file for the same topic).
- Each query block needs: title, object, use case in plain English, the SQL, notes/gotchas.

Do not skip this for "simple" or throwaway queries. Schema/`describeSObject` exploration and queries used only for your own internal search do **not** go in the archive.

Load the `querying-soql` skill when authoring or optimizing queries.
