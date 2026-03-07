# Daily Workflow

## Scope
Use this workflow whenever a new problem is requested.
Canonical root is `/Users/study/road_to_grandmaster` for all file writes.

## Problem Intake Workflow
1. Identify platform and `problem_id`, e.g. `atc` + `abc439_g`.
2. Resolve `problem_slug = {platform}-{problem_id}`.
3. Build local paths under `problems/{platform}/{problem_slug}/`.
4. For AtCoder problems, run local difficulty lookup first:
   - `python3 scripts/lookup_atcoder_difficulty.py abc439_g`
   - read `difficulty` from JSON output.
5. Fill `problem.yaml`:
   - set `problem.problem_id`, `slug`, `contest_id`, `title`, `url`
   - set `problem.difficulty.source` and `problem.difficulty.value`.
   - if lookup returns `null`/`found=false`, set `difficulty` to `null`.
6. Copy the standard problem scaffold:
   - `problem.yaml`, `README.md`, `statement.md`, `workspace/`, `attempts/`, `references/`, `review/`, `workspace/main.cpp`, `workspace/notes.md`, `references/{editorial.md,ranker.md,references.yaml}`, `review/{review.yaml,review.md}`
7. Open and verify the new problem path:
   - `problems/{platform}/{problem_slug}/`
8. Optionally add to today's session file if queue tracking is requested.

## Daily Solve Workflow
1. Start or update attempt with `attempt-tracker`.
2. Solve in `workspace/main.cpp` and keep a snapshot under `attempts/{attempt_id}/`.
3. Save first review-ready evidence:
   - `references/editorial.md`
   - `references/ranker.md`
   - `review/review.md`
4. Run `evidence-review` to write grounded comparison results into `review/review.yaml` and `review/review.md`.
5. Run `daily-manager` to update `sessions/{yyyy-mm-dd}.yaml` action items.

## Hard Rule
- For AtCoder difficulty, do not call a network endpoint. Use only `data/atcoder/problem-models.json` via `scripts/lookup_atcoder_difficulty.py`.
