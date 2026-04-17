# Schemas

This file is a compact reference for the YAML contracts defined in [cp-training-system-requirements.md](../cp-training-system-requirements.md).

## Required Schemas
- `templates/problem.yaml`
- `templates/attempt.yaml`
- `templates/review.yaml`
- `templates/session.yaml`

## `problem.yaml`
Tracks problem metadata, workflow defaults, reference status, and review status.

Required top-level keys:
- `schema_version`
- `problem`
- `status`
- `workflow`
- `references`
- `review`

## `attempt.yaml`
Tracks one attempt snapshot and its artifacts.

Required top-level keys:
- `schema_version`
- `attempt`
- `artifacts`
- `analysis`

## `review.yaml`
Tracks grounded comparison output and follow-up actions.

Required top-level keys:
- `schema_version`
- `review`
- `comparison`
- `insights`
- `follow_up`

## `session.yaml`
Tracks the day queue and completed work.

Required top-level keys:
- `schema_version`
- `session`
- `log`
- `next_actions`

## `references/references.yaml`
Tracks collected reference metadata for editorial and ranker notes.

Recommended fields for each of `editorial` and `ranker`:
- `primary_url`
- `status`
- `read_at`
- `summary_keywords`
- `sources`
- `notes_path`
