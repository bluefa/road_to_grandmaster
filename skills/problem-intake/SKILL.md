---
name: problem-intake
description: Create a new competitive programming problem workspace in this repository when the user starts a new BOJ, Codeforces, AtCoder, or similar problem and needs the standard directory, YAML metadata, workspace files, and optional session entry.
---

# Problem Intake

Use this skill to initialize a new problem under `problems/{platform}/{problem_slug}/`.
Prefer `../../scripts/init_problem.py` when it is implemented. Until then, apply the same contract directly.

## Read Only If Needed
- `../../cp-training-system-requirements.md`
- `../../docs/conventions.md`
- `../../docs/schemas.md`

## Inputs
- `platform`
- `problem_id` or existing slug
- `title`
- optional `url`
- optional request to add the problem into today's session

## Required Output
- Create `problems/{platform}/{problem_slug}/`
- Materialize `problem.yaml`, `README.md`, `statement.md`
- Create `workspace/`, `attempts/`, `references/`, `review/`
- Initialize `workspace/main.cpp` and `workspace/notes.md`
- Initialize empty evidence and review note files
- If asked, register the slug in `sessions/{yyyy-mm-dd}.yaml`

## Workflow
1. Normalize `problem_slug` as `{platform}-{problem_id}` unless the repo already uses a different explicit slug.
2. Create the standard problem directory tree without creating attempt snapshots.
3. Fill `problem.yaml` from the template with `state: not_started` or `in_progress` depending on the user request.
4. Fill the problem `README.md` so the current state and file entry points are visible.
5. Initialize `statement.md` as a local summary file, not a full source dump unless the user explicitly wants that.
6. Leave `references/editorial.md` and `references/ranker.md` empty or skeletal. Do not summarize them before the user has reviewed them.
7. Update today's session file only if the user asked for queue tracking or the existing workflow clearly requires it.

## Guardrails
- Do not solve the problem.
- Do not generate hints.
- Do not read or summarize editorial or ranker content during intake.
- Do not invent metadata that is not present; use `null`, empty lists, or placeholders.
