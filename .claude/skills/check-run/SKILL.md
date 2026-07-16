---
description: Diagnose the state of paper-alert - last run date, logs, and whether config is in place. Use when the user asks whether paper-alert ran, why it didn't send an alert, or wants a health check.
---

Diagnose the current state of this paper-alert installation. Report findings in Japanese, plainly (this project's user is not deeply technical) - don't just dump raw file contents.

Checks to run, in order:

1. **Last run**: read `state/last_run.json`. Report the last recorded run date, and how many days ago that was.
2. **Logs**: list `logs/`. If there are log files, read the most recent one and summarize what happened (papers found, errors, etc.). If `logs/` is empty, say so explicitly - it means either the tool has never been run, or nothing is being logged yet.
3. **Config present**: check `.env` and `profile.yaml` both exist. Do not print their contents (they contain secrets/personal config) - just confirm presence/absence and, for `.env`, confirm (without printing values) whether `GEMINI_API_KEY`, `GMAIL_ADDRESS`, and `GMAIL_APP_PASSWORD` are non-empty.
4. **Scheduled run (optional)**: if the user has set up a `launchd` job for this project, check `launchctl list` for it and report whether it's loaded. Don't assume one exists - only report on this if asked or if one is found.

Summarize with a clear verdict: is the pipeline configured and did it last run successfully, or is something missing/broken. If something looks broken, suggest the likely next step (e.g. "`.env`にGEMINI_API_KEYが設定されていません" or "前回の実行から10日経っています、launchdジョブが動いているか確認しましょう").
