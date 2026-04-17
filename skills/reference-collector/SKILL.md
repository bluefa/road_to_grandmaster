---
name: reference-collector
description: Collect competitive programming reference notes for a saved problem when the user asks for hints, editorial notes, or ranker solution notes, preferring accepted submission code for ranker analysis and persisting the results into `references/editorial.md`, `references/ranker.md`, and `references/references.yaml`.
---

# Reference Collector

Use this skill when a problem workspace already exists and the user wants external reference material saved into the repository.
This skill fills the gap between `problem-intake` and `evidence-review`.

## Main Workspace Rule
- Canonical workspace root: `/Users/study/road_to_grandmaster`
- If the current session is running inside a Codex worktree or any path other than the canonical root, read and write reference artifacts in the canonical root instead of the transient worktree.
- Resolve all target paths from the canonical root before writing.
- When reporting changed files, use canonical-root paths.

## Read Only If Needed
- `../../cp-training-system-requirements.md`
- `../../docs/conventions.md`
- `../../docs/schemas.md`
- target `problem.yaml`
- target `references/references.yaml`
- target `references/editorial.md`
- target `references/ranker.md`

## Inputs
- target problem path or slug
- requested source type: `editorial`, `ranker`, or both
- optional request for `hint`
- optional preferred ranker source such as a specific user, submission, or blog

## Required Output
- Update `references/editorial.md` when editorial notes were requested and found
- Update `references/ranker.md` when ranker notes were requested and found
- Update `references/references.yaml` with primary URL, source list, status, read time, and summary keywords
- Update `problem.yaml` reference statuses to match the collected evidence
- If the user asked for hints, answer from the saved notes after the files are updated

## Workflow
1. Resolve the canonical workspace root as `/Users/study/road_to_grandmaster` and operate there even if the active shell is inside a worktree.
2. Read the target `problem.yaml` and existing reference files first so you do not overwrite useful notes.
3. Find primary sources for the requested reference type:
   - editorial: prefer the official task editorial page and collect every relevant solution entry listed for that problem, not just the first one
   - ranker: prefer a concrete accepted submission code from a strong user; use a blog write-up only as supplemental material or fallback when code is unavailable
4. For editorial notes, create one subsection per collected solution and add a short comparison section when multiple approaches exist.
5. For ranker notes, analyze the implementation itself:
   - identify the main functions, state representation, and algorithmic trick used in code
   - explain why the code structure works, not only the math idea behind it
   - if multiple strong code submissions show distinct approaches, collect more than one
6. Write concise local notes, not full source dumps. Keep the existing section structure unless there is a strong reason to extend it.
7. Save exact source URLs in both the markdown note and `references/references.yaml`.
8. Record multiple sources in `references/references.yaml` under `sources`, and set `primary_url` to the source that best represents the saved note.
9. Set `references.*.status` to `collected` after notes are saved. Use `reviewed` only when the user explicitly asks for a comparison or retrospective that consumes those notes.
10. Update `references.*.read_at` with the current local timestamp and add a short keyword list that helps later review work.
11. If one requested source cannot be found, leave the note skeletal and record the metadata as missing instead of guessing.
12. If the user asked for hints, provide incremental hints grounded in the saved notes and avoid dumping the full solution unless the user asked for it.

## Guardrails
- Do not create `review/review.yaml` or `review/review.md`; hand that off to `evidence-review`.
- Do not invent editorial or ranker details that were not verified from a source.
- Do not replace the user's notes wholesale when a careful update or append is enough.
- Do not paste large code blocks or long verbatim excerpts into `references/*.md`.
- Do not use a blog as the only ranker source when an accepted submission code can be verified.
- Do not stop after the first editorial entry when the official task editorial page lists multiple relevant solutions.
- If the problem workspace does not exist yet, hand off to `problem-intake` instead of creating ad hoc files.
