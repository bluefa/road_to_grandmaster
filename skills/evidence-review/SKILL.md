---
name: evidence-review
description: Generate a grounded retrospective for a competitive programming problem when the user asks to compare their saved attempt with editorial and ranker notes and produce `review.yaml` and `review.md` from repository evidence.
---

# Evidence Review

Use this skill after at least one attempt snapshot exists and review should be based on stored artifacts.
Prefer `../../scripts/build_review.py` when it is implemented. Until then, build the review directly from repository files.

## Main Workspace Rule
- Canonical workspace root: `/Users/study/road_to_grandmaster`
- If the current session is running inside a Codex worktree or any path other than the canonical root, read evidence and write review files in the canonical root instead of the transient worktree.
- Use canonical-root paths for all input and output artifacts.
- When the same problem exists in both a worktree and the canonical root, treat the canonical root as source of truth.

## Read Only If Needed
- `../../cp-training-system-requirements.md`
- `../../docs/conventions.md`
- `../../docs/schemas.md`
- target `problem.yaml`
- target `attempts/{attempt_id}/attempt.yaml`
- relevant `notes.md`, `references/editorial.md`, `references/ranker.md`

## Inputs
- target problem path
- target attempt ID or the current attempt from `problem.yaml`
- saved reference notes

## Required Output
- `review/review.yaml`
- `review/review.md`
- comparison across `my solution`, `editorial`, and `ranker`
- mistakes, reusable rules, and next action grounded in saved files

## Workflow
1. Resolve the canonical workspace root as `/Users/study/road_to_grandmaster` and operate there even if the active shell is inside a worktree.
2. Read the target attempt artifacts first.
3. Read `references/editorial.md` and `references/ranker.md` only as evidence files, not as sources for broad explanation.
4. Mark missing evidence explicitly as `missing evidence`, `unknown`, or an empty field instead of guessing.
5. Write `review/review.yaml` with structured comparison, mistakes, and follow-up action.
6. Write `review/review.md` with the fixed section order from the PRD.
7. Update problem review state only if the created review files are present and coherent.

## Guardrails
- Do not switch into hint mode.
- Do not invent editorial or ranker details that are not in the saved notes.
- Do not flatten all differences into generic advice; preserve concrete comparison points.
- If there is no saved attempt, stop and ask for attempt capture first.
