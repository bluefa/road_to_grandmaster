---
name: test-runner
description: Build and test a competitive programming solution when the user wants to compile `workspace/main.cpp`, run it against `workspace/testcases/sample_input_*.txt`, compare against `sample_output_*.txt`, and produce `workspace/summary.md` with PASS/FAIL results.
---

# Test Runner

Use this skill to build and verify a problem's active `workspace/main.cpp` against its sample cases.
Runs `../../scripts/run_tests.sh` and reports the outcome.

## Main Workspace Rule
- Canonical workspace root: `/Users/study/road_to_grandmaster`
- If the current session is running inside a Codex worktree or any path other than the canonical root, build and write artifacts in the canonical root instead of the transient worktree.
- When reporting file paths, use canonical-root paths.

## Read Only If Needed
- `../../docs/conventions.md`
- target problem's `problem.yaml`
- target `workspace/summary.md` after running

## Inputs
- target problem path (e.g. `problems/atc/atc-abc436_g`)

## Required Output
- `workspace/.solution` compiled binary (git-ignored)
- `workspace/summary.md` with PASS/FAIL per sample
- terminal report of each test outcome

## Workflow
1. Resolve the canonical workspace root as `/Users/study/road_to_grandmaster`.
2. Ensure `workspace/main.cpp` exists at the target problem path. Stop if missing.
3. Ensure `workspace/testcases/` exists. Create it if missing.
4. Run `./scripts/run_tests.sh <problem-dir>` from the canonical root.
5. Report the summary to the user: build status, PASS/FAIL per sample, total.
6. If any FAIL occurred, point the user to `workspace/summary.md` for the recorded table.

## Script Behavior
- Build: `g++ -std=c++17 -O2 -Wall`. Failure prints compiler stderr, writes `summary.md` with build error, exits 1.
- Each sample: `timeout 5s ./.solution < sample_input_N.txt`, compared to `sample_output_N.txt` after stripping trailing whitespace per line.
- Status mapping:
  - `PASS` — exit 0 and output matches expected
  - `FAIL` — output mismatch
  - `FAIL (TLE)` — timeout exceeded (5s)
  - `FAIL (RTE exit N)` — non-zero exit
  - `SKIP (no expected)` — input exists but no paired output file
- Idempotent: `.solution` and `summary.md` are overwritten each run; `testcases/` is read-only.

## Guardrails
- Do not modify `workspace/main.cpp` or files in `workspace/testcases/`.
- Do not create attempt snapshots; hand off to `attempt-tracker` for that.
- Do not fabricate test results; always drive them from the script's actual output.
- If the user wants to add a new test case, instruct them to create paired `sample_input_N.txt` and `sample_output_N.txt` files in `workspace/testcases/`. Do not auto-generate expected outputs.
