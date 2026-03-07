# Conventions

## Canonical Root
- Canonical workspace root: `/Users/study/road_to_grandmaster`
- If Codex is running inside `/Users/study/.codex/worktrees/...`, treat that location as a transient execution path, not the source of truth.
- Default read and write target is the canonical root unless the user explicitly asks to work in a different repository path.

## Naming
- `problem_slug`: `{platform}-{problem_id}`
- `attempt_id`: `YYYYMMDD-HHMM` in local time
- Problem root: `problems/{platform}/{problem_slug}/`

## Metadata Sources
- Vendored AtCoder difficulty dataset path: `/Users/study/road_to_grandmaster/data/atcoder/problem-models.json`
- Upstream reference for that dataset: `https://kenkoooo.com/atcoder/resources/problem-models.json`
- AtCoder problem difficulty lookup must read the vendored local file first, not the network endpoint.
- Use `/Users/study/road_to_grandmaster/scripts/lookup_atcoder_difficulty.py` for deterministic local lookup.
- Store the source name in `problem.difficulty.source` and the numeric estimate in `problem.difficulty.value`.
- If the problem is not present in the vendored dataset or the value cannot be verified, keep the field `null` instead of guessing.

## Status Enums
- `problem.status.state`: `not_started`, `in_progress`, `solved`, `review_pending`, `reviewed`, `archived`
- `attempt.status`: `in_progress`, `accepted`, `wrong_answer`, `time_limit`, `memory_limit`, `runtime_error`, `compile_error`, `abandoned`
- `references.*.status`: `pending`, `collected`, `reviewed`
- `review.outcome`: `pending`, `solved_after_review`, `needs_retry`, `concept_gap`, `implementation_gap`

## Time Format
- Use ISO 8601 with timezone, for example `2026-03-07T09:00:00+09:00`

## File Roles
- `workspace/main.cpp`: active working file
- `attempts/{attempt_id}/solution.cpp`: immutable snapshot for that attempt
- `references/*.md`: evidence notes, not full source dumps
- `review/review.md`: grounded retrospective from saved artifacts only
