---
name: attempt-tracker
description: Record a competitive programming attempt in this repository when the user wants to start or end an attempt, snapshot `workspace/main.cpp`, save attempt YAML, preserve notes, or update problem status after a try.
---

# Attempt Tracker

Use this skill to convert active workspace state into a persistent attempt record.
Prefer `../../scripts/start_attempt.py` when it is implemented. Until then, follow the file contract manually.

## Read Only If Needed
- `../../cp-training-system-requirements.md`
- `../../docs/conventions.md`
- `../../docs/schemas.md`
- target problem's `problem.yaml`

## Inputs
- target problem path
- language if different from `problem.yaml`
- attempt status such as `in_progress`, `wrong_answer`, or `accepted`
- optional run output to store in `run.log`

## Required Output
- Generate or confirm `attempt_id`
- Create `attempts/{attempt_id}/`
- Save `attempt.yaml`, `solution.cpp`, `notes.md`, `run.log`
- Update `problem.yaml` with `current_attempt_id`, `last_touched_at`, and solution path if relevant
- Move problem state to `solved` or `review_pending` when justified by the saved attempt

## Workflow
1. Read the target `problem.yaml` and active workspace files.
2. Derive `attempt_id` with local time format `YYYYMMDD-HHMM` unless the user supplied one.
3. Snapshot `workspace/main.cpp` into `attempts/{attempt_id}/solution.cpp`.
4. Snapshot the current working notes into `attempts/{attempt_id}/notes.md`.
5. Create `attempt.yaml` with timestamps, language, status, artifact paths, and short self-assessment if the user provided one.
6. Save `run.log` with actual command output when available; otherwise create an empty file or leave a clear placeholder.
7. Update `problem.yaml` so later review work can find the latest attempt without guesswork.

## Guardrails
- Do not summarize editorial or ranker content.
- Do not create retrospective claims that are not supported by the saved attempt.
- Do not overwrite older attempts.
- Do not mutate `workspace/` more than needed for snapshotting.
