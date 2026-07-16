---
description: Add a journal to profile.yaml's flagship_journals or priority_journals list. Use when the user wants to start watching a new journal for paper alerts.
---

Add a journal name to `profile.yaml` in this project.

Steps:

1. Read `profile.yaml`.
2. If no journal name was given in the request, ask for it.
3. Determine which list it belongs in:
   - `flagship_journals` — Nature/Science-family journals (broadest match: keywords + broad_terms)
   - `priority_journals` — field-specific top journals, e.g. ACS/RSC/Wiley (keywords-only match)
   If it's ambiguous which tier fits, ask the user rather than guessing.
4. Check the journal isn't already present in either list (case-insensitive). If it already is, say so and stop.
5. Add it as a new line in the appropriate list, preserving existing formatting, comments, and ordering (append at the end of the list).
6. Show the user the diff and confirm what was added and to which tier.

Do not touch any other part of `profile.yaml`.
