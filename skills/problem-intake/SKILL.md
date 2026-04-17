---
name: problem-intake
description: Create a new competitive programming problem workspace in this repository when the user starts a new BOJ, Codeforces, AtCoder, or similar problem and needs the standard directory, YAML metadata, workspace files, and optional session entry.
---

# Problem Intake

Use this skill to initialize a new problem under `problems/{platform}/{problem_slug}/`.
Prefer `../../scripts/init_problem.py` when it is implemented. Until then, apply the same contract directly.

## Main Workspace Rule
- Canonical workspace root: `/Users/study/road_to_grandmaster`
- If the current session is running inside a Codex worktree or any path other than the canonical root, create and update files in the canonical root instead of the transient worktree.
- Before writing, resolve all output paths from `/Users/study/road_to_grandmaster`.
- When showing the user file locations, prefer canonical-root paths.

## Read Only If Needed
- `../../cp-training-system-requirements.md`
- `../../docs/conventions.md`
- `../../docs/schemas.md`
- `../../data/atcoder/problem-models.json`

## Inputs
- `platform`
- `problem_id` or existing slug
- `title`
- optional `url`
- optional request to add the problem into today's session

## Required Output
- Create `problems/{platform}/{problem_slug}/`
- Materialize `problem.yaml`, `README.md`, `statement.md`
- Create `workspace/`, `workspace/testcases/`, `attempts/`, `references/`, `review/`
- Initialize `workspace/main.cpp` and `workspace/notes.md`
- Initialize empty evidence and review note files
- For AtCoder problems, fill `problem.difficulty` from the vendored local dataset at `data/atcoder/problem-models.json` when the value can be verified
- If asked, register the slug in `sessions/{yyyy-mm-dd}.yaml`

## Workflow
1. Resolve the canonical workspace root as `/Users/study/road_to_grandmaster` and write there even if the active shell is inside a worktree.
2. Normalize `problem_slug` as `{platform}-{problem_id}` unless the repo already uses a different explicit slug.
3. Create the standard problem directory tree without creating attempt snapshots. Include `workspace/testcases/` so the `test-runner` skill can drop sample files there.
4. Fill `problem.yaml` from the template with `state: not_started` or `in_progress` depending on the user request.
5. For AtCoder problems, call `../../scripts/lookup_atcoder_difficulty.py <problem_id>` and use its output to populate `problem.difficulty.source` and `problem.difficulty.value`.
6. If the local dataset does not contain the task id or the value is missing, keep difficulty `null`.
7. Fill the problem `README.md` so the current state and file entry points are visible.
8. Initialize `statement.md` as a local summary file, not a full source dump unless the user explicitly wants that.
9. Leave `references/editorial.md` and `references/ranker.md` empty or skeletal. Do not summarize them before the user has reviewed them.
10. Update today's session file only if the user asked for queue tracking or the existing workflow clearly requires it.

## Guardrails
- Do not solve the problem.
- Do not generate hints.
- Do not read or summarize editorial or ranker content during intake.
- Do not invent metadata that is not present; use `null`, empty lists, or placeholders.
- Do not guess AtCoder difficulty; either verify it from the vendored local dataset or keep it `null`.
