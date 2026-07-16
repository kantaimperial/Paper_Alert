# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

paper-alert searches for new journal articles matching a user's keywords/journals, generates
a Japanese summary of each match via the Gemini API, and emails a digest via Gmail. It's meant
to run on a schedule (e.g. macOS `launchd`), tracking the last run date so each run only
searches the gap since the previous one.

## Commands

```bash
# Setup (one-time)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python setup.py            # interactive wizard -> writes profile.yaml
cp .env.example .env       # then fill in GEMINI_API_KEY / GMAIL_ADDRESS / GMAIL_APP_PASSWORD

# Run
python main.py
```

There is no test suite, linter, or build step configured in this repo.

## Architecture

Pipeline, driven by `main.py::run()`:

1. **Profile load** (`src/profile.py`) — reads `profile.yaml` (recipient email, `keywords`,
   `broad_terms`, `flagship_journals`, `priority_journals`). This file is gitignored since it's
   per-user config; `profile.example.yaml` documents the schema. `setup.py` is the wizard that
   generates it.
2. **Date range** — `src/state.py` persists the last successful run date to
   `state/last_run.json`. Each run searches from that date (or `LOOKBACK_DAYS_DEFAULT` = 7 days
   back on first run) through today.
3. **Search** (`src/sources/crossref.py`) — queries the Crossref API once per journal in
   `flagship_journals` (tier=1) and `priority_journals` (tier=2). Crossref's
   `query.bibliographic` is a plain relevance search with no boolean operators, so all keywords
   are passed through as-is and real filtering happens in the next step.
4. **Dedupe + filter** (`src/filtering.py`) — `dedupe()` collapses papers by DOI (falling back
   to normalized title). Match rules differ by tier: `match_priority` (tier 2) requires any
   keyword hit; `match_flagship` (tier 1) also accepts a hit on the broader `broad_terms` list,
   since flagship journals get a wider net. Short terms (<=2 chars, e.g. element symbols like
   "Bi") use word-boundary regex to avoid false substring matches; longer terms use plain
   substring matching.
5. **Abstract backfill** (`src/sources/semantic_scholar.py`) — Crossref entries without an
   abstract get a best-effort DOI lookup against Semantic Scholar.
6. **Summarize + send** (`src/summarize.py`, `src/emailer.py`) — each matched paper is
   summarized individually via the Gemini API (`gemini-3.5-flash`) into a 3-4 sentence Japanese
   summary, then `emailer.build_digest()` groups papers by tier into a plain-text digest sent
   over Gmail SMTP (`smtplib.SMTP_SSL`, app-password auth).

`src/models.py::Paper` is the shared record type threaded through the whole pipeline; `tier`
(1/2/3) and `dedup_key()` (DOI-based, title fallback) are its two load-bearing behaviors.

## Config and secrets

- `src/config.py` loads `.env` (via `python-dotenv`) into module-level constants —
  `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`, `GEMINI_API_KEY` — that other modules import directly.
- `.env` and `profile.yaml` are gitignored (real secrets/config); `.env.example` and
  `profile.example.yaml` are the checked-in templates.
