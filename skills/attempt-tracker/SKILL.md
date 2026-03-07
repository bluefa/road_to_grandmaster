---
name: attempt-tracker
description: Record a competitive programming attempt in this repository when the user wants to start or end an attempt, snapshot `workspace/main.cpp`, save attempt YAML, preserve notes, or update problem status after a try.
---

# Attempt Tracker

Use this skill to convert active workspace state into a persistent attempt record.
Prefer `../../scripts/start_attempt.py` when it is implemented. Until then, follow the file contract manually.

## Main Workspace Rule
- Canonical workspace root: `/Users/study/road_to_grandmaster`
- If the current session is running inside a Codex worktree or any path other than the canonical root, snapshot and update files in the canonical root instead of the transient worktree.
- Read and write attempt artifacts from canonical-root paths.
- When reporting changed files, use canonical-root paths.

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
1. Resolve the canonical workspace root as `/Users/study/road_to_grandmaster` and operate there even if the active shell is inside a worktree.
2. Read the target `problem.yaml` and active workspace files.
3. Derive `attempt_id` with local time format `YYYYMMDD-HHMM` unless the user supplied one.
4. Snapshot `workspace/main.cpp` into `attempts/{attempt_id}/solution.cpp`.
5. Snapshot the current working notes into `attempts/{attempt_id}/notes.md`.
6. Create `attempt.yaml` with timestamps, language, status, artifact paths, and short self-assessment if the user provided one.
7. Save `run.log` with actual command output when available; otherwise create an empty file or leave a clear placeholder.
8. Update `problem.yaml` so later review work can find the latest attempt without guesswork.

## Guardrails
- Do not summarize editorial or ranker content.
- Do not create retrospective claims that are not supported by the saved attempt.
- Do not overwrite older attempts.
- Do not mutate `workspace/` more than needed for snapshotting.
