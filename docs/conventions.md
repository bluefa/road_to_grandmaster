# Conventions

## Naming
- `problem_slug`: `{platform}-{problem_id}`
- `attempt_id`: `YYYYMMDD-HHMM` in local time
- Problem root: `problems/{platform}/{problem_slug}/`

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
