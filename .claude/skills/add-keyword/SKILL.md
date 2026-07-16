---
description: Add a term to profile.yaml's keywords or broad_terms list. Use when the user wants paper alerts to also match on a new word/phrase.
---

Add a term to `profile.yaml` in this project.

Steps:

1. Read `profile.yaml`.
2. If no term was given in the request, ask for it.
3. Determine which list it belongs in:
   - `keywords` — the normal match list, used against every journal (any single match triggers an alert from `priority_journals`, and contributes to the match for `flagship_journals` too)
   - `broad_terms` — only used for `flagship_journals`, a much wider net (e.g. broad terms like "inorganic", "halide"). Only add here if the user explicitly wants a broader, flagship-only match, or if the term is clearly too generic for `keywords` (would over-match on ACS/RSC/Wiley journals). If unsure, default to `keywords` and ask if they meant the broader list instead.
4. Check the term isn't already present in either list (case-insensitive, ignoring hyphenation like "lone pair" vs "lone-pair"). If it's already covered, say so and stop.
5. Add it as a new line in the appropriate list, preserving existing formatting, comments, and ordering (append at the end of the list).
6. Show the user the diff and confirm what was added and to which list.

Do not touch any other part of `profile.yaml`.
