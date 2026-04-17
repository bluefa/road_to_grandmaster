## Skills
A skill is a set of local instructions to follow that is stored in a `SKILL.md` file. Below is the list of skills that can be used. Each entry includes a name, description, and file path so you can open the source for full instructions when using a specific skill.

### Available skills
- problem-intake: Create a new competitive programming problem workspace in this repository when the user starts a new BOJ, Codeforces, AtCoder, or similar problem and needs the standard directory, YAML metadata, workspace files, and optional session entry. (file: /Users/study/road_to_grandmaster/skills/problem-intake/SKILL.md)
- test-runner: Build and test a competitive programming solution when the user wants to compile `workspace/main.cpp`, run it against `workspace/testcases/sample_input_*.txt`, compare against `sample_output_*.txt`, and produce `workspace/summary.md` with PASS/FAIL results. (file: /Users/study/road_to_grandmaster/skills/test-runner/SKILL.md)
- attempt-tracker: Record a competitive programming attempt in this repository when the user wants to start or end an attempt, snapshot `workspace/main.cpp`, save attempt YAML, preserve notes, or update problem status after a try. (file: /Users/study/road_to_grandmaster/skills/attempt-tracker/SKILL.md)
- reference-collector: Collect competitive programming reference notes for a saved problem when the user asks for hints, editorial notes, or ranker solution notes, preferring accepted submission code for ranker analysis and persisting the results into `references/editorial.md`, `references/ranker.md`, and `references/references.yaml`. (file: /Users/study/road_to_grandmaster/skills/reference-collector/SKILL.md)
- evidence-review: Generate a grounded retrospective for a competitive programming problem when the user asks to compare their saved attempt with editorial and ranker notes and produce `review.yaml` and `review.md` from repository evidence. (file: /Users/study/road_to_grandmaster/skills/evidence-review/SKILL.md)
- daily-manager: Manage the daily training queue in this repository when the user wants to open a session, add or move problem slugs across planned, active, review, or completed lists, or close the day with next actions. (file: /Users/study/road_to_grandmaster/skills/daily-manager/SKILL.md)

### How to use skills
- Discovery: The list above is the skills available in this repository session (name + description + file path). Skill bodies live on disk at the listed paths.
- Trigger rules: If the user names a skill (with `$SkillName` or plain text) OR the task clearly matches a skill's description shown above, you must use that skill for that turn. Multiple mentions mean use them all. Do not carry skills across turns unless re-mentioned.
- Missing/blocked: If a named skill isn't in the list or the path can't be read, say so briefly and continue with the best fallback.
- How to use a skill (progressive disclosure):
  1. After deciding to use a skill, open its `SKILL.md`. Read only enough to follow the workflow.
  2. When `SKILL.md` references relative paths, resolve them relative to the skill directory listed above first, and only consider other paths if needed.
  3. If `SKILL.md` points to extra folders such as `references/`, load only the specific files needed for the request; don't bulk-load everything.
  4. If `scripts/` exist, prefer running or patching them instead of retyping large code blocks.
  5. If `assets/` or templates exist, reuse them instead of recreating from scratch.
- Coordination and sequencing:
  - If multiple skills apply, choose the minimal set that covers the request and state the order you'll use them.
  - Announce which skill or skills you're using and why in one short line.
- Context hygiene:
  - Keep context small: summarize long sections instead of pasting them; only load extra files when needed.
  - Avoid deep reference-chasing: prefer opening only files directly linked from `SKILL.md` unless blocked.
- Safety and fallback: If a skill can't be applied cleanly, state the issue, pick the next-best approach, and continue.
