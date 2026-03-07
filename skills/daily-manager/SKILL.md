---
name: daily-manager
description: Manage the daily training queue in this repository when the user wants to open a session, add or move problem slugs across planned, active, review, or completed lists, or close the day with next actions.
---

# Daily Manager

Use this skill to maintain `sessions/{yyyy-mm-dd}.yaml` as the source of truth for a training day.
Prefer `../../scripts/update_session.py` when it is implemented. Until then, update the YAML manually while preserving schema shape.

## Read Only If Needed
- `../../cp-training-system-requirements.md`
- `../../docs/conventions.md`
- `../../docs/schemas.md`
- relevant `sessions/{date}.yaml`

## Inputs
- date
- queue changes for `planned`, `active`, `review`
- completed items or finished reviews
- optional session focus and next actions

## Required Output
- Create or update `sessions/{yyyy-mm-dd}.yaml`
- Keep `planned`, `active`, `review`, `completed`, and `review_completed` consistent
- Leave a concrete `next_actions` list at session close

## Workflow
1. Open the target session file or create it from the template.
2. Apply only the requested queue transitions.
3. Preserve existing entries unless the user asked to remove or move them.
4. When a problem is completed, append a structured log entry instead of only removing it from the queue.
5. When review is completed, append the slug to `log.review_completed`.
6. Write next actions as concrete follow-ups, not generic reminders.

## Guardrails
- Do not reprioritize the queue without a user instruction or a directly implied state transition.
- Do not create problem directories; hand off to `problem-intake` for that.
- Do not fabricate completion results or attempt IDs.
