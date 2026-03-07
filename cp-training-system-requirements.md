# cp-training-system-requirements

## 1. 문서 목적
이 문서는 개인용 Competitive Programming(CP) 훈련 시스템을 `repo-first` 방식으로 구축하기 위한 제품 요구사항 문서(PRD)다.
목표는 Codex가 이 문서를 입력으로 받아 아래 순서를 바로 실행할 수 있게 만드는 것이다.

1. 디렉토리 구조 생성
2. YAML 스키마 확정
3. skill 4개 초안 작성
4. scripts 최소 버전 작성
5. daily workflow 문서화

이 문서는 아이디어 정리 문서가 아니라 구현 계약 문서다. 따라서 파일 경로, 데이터 계약, 책임 범위, 완료 기준을 명시적으로 고정한다.

## 2. 제품 정의

### 2.1 목표
이 시스템은 다음을 만족해야 한다.

- 개인용 CP 훈련 시스템이어야 한다.
- 문제 풀이 자체가 repo 안에서 이루어져야 한다.
- 복기는 `editorial / ranker / 내 풀이` 비교를 기반으로 해야 한다.
- AI의 역할은 힌트 생성기가 아니라 근거 기반 정리 엔진이어야 한다.
- 최소 4개의 skill로 운영 가능해야 한다.
- 디렉토리 구조, 파일 역할, YAML 스키마가 먼저 고정되어야 한다.

### 2.2 성공 조건
다음 조건이 만족되면 1차 목표를 달성한 것으로 본다.

- 새 문제를 시작하면 표준 디렉토리와 메타데이터가 자동 생성된다.
- 풀이 코드, 시도 기록, 실행 기록, 복기 문서가 한 문제 디렉토리 안에서 추적된다.
- 복기 문서는 반드시 `내 풀이`, `editorial`, `ranker` 비교 근거를 포함한다.
- 모든 핵심 상태가 YAML 파일로 저장되어 script와 skill이 동일한 계약을 공유한다.
- Codex skill 4개가 각자 책임 범위가 분리된 채로 동작한다.

### 2.3 비목표
이번 버전에서 다음은 우선순위 밖이다.

- 온라인 저지 제출 자동화
- 범용 팀 협업 기능
- 완전한 웹 UI
- AI가 문제를 대신 풀어주는 자동 풀이 에이전트
- 대규모 통계 대시보드

## 3. 핵심 원칙

### 3.1 Repo-first
문제 시작, 풀이, 시도 기록, 복기, 일일 운영까지 모두 repo 안에서 관리한다.
외부 서비스는 링크와 참조 대상으로만 사용하고, 작업의 기준 상태는 로컬 repo가 가진다.

### 3.2 Evidence-first
AI 출력은 반드시 저장된 근거를 기반으로 해야 한다.
근거 없는 추정, 일반론 요약, 힌트성 서술은 기본 동작으로 허용하지 않는다.

### 3.3 Attempt-before-review
문제 풀이 시점에는 정답 유도보다 시도 기록이 우선이다.
`editorial`과 `ranker` 비교 기반 복기는 내 시도가 저장된 뒤에 수행한다.

### 3.4 Schema-first
skill과 script는 자유 텍스트 문서가 아니라 YAML 스키마를 공통 계약으로 사용한다.
새 자동화는 스키마 변경 없이 붙일 수 있어야 한다.

### 3.5 Minimal-but-extensible
초기 구현은 4개 skill + 최소 scripts로 시작한다.
다만 플랫폼 추가, 언어 추가, 복기 포맷 확장이 가능한 구조여야 한다.

## 4. 사용자와 운영 단위

### 4.1 사용자
- 단일 사용자: 본인

### 4.2 핵심 운영 단위
- Problem: 하나의 문제
- Attempt: 특정 시점의 풀이 시도
- Reference: editorial 또는 ranker 풀이 참조
- Review: 근거 기반 복기 결과
- Session: 하루 또는 한 번의 훈련 세션

## 5. 필수 기능 범위

### 5.1 문제 시작
- 플랫폼과 문제 ID 또는 slug를 기준으로 문제 워크스페이스를 생성한다.
- 기본 메타데이터 YAML과 코드 템플릿을 만든다.
- 아직 editorial/ranker를 읽지 않았다는 상태를 명시한다.
- AtCoder 문제의 난이도는 repo에 저장된 로컬 difficulty dataset을 우선 조회한다.

### 5.2 풀이 수행
- 사용자는 repo 안의 표준 경로에서 직접 코드를 작성한다.
- 각 시도는 별도 디렉토리 또는 명시적 attempt 메타데이터로 저장한다.
- 실행/테스트 결과를 파일로 남길 수 있어야 한다.

### 5.3 근거 수집
- editorial 링크, ranker 링크, 내 풀이 경로를 명시적으로 저장한다.
- 필요 시 핵심 발상, 전환점, 코드 차이, 복잡도 차이 메모를 기록한다.
- 참조 원문 전체를 무조건 복사하지 않고, 링크/요약/발췌 메모 중심으로 저장한다.

### 5.4 비교 기반 복기
- 복기는 최소한 다음 축을 포함해야 한다.
- 내 풀이 접근
- editorial 핵심 아이디어
- ranker 구현 또는 관점 차이
- 실수 유형
- 다음 재발 방지 규칙

### 5.5 일일 운영
- 오늘 풀 문제 큐, 진행 중 문제, 복습 필요 문제를 구분한다.
- 세션 종료 시 무엇을 풀었고 무엇을 복기해야 하는지 남긴다.

## 6. 저장소 구조 계약
초기 구조는 아래를 기준으로 한다.

```text
.
├── cp-training-system-requirements.md
├── README.md
├── data/
│   └── atcoder/
│       └── problem-models.json
├── docs/
│   ├── daily-workflow.md
│   ├── schemas.md
│   └── conventions.md
├── problems/
│   └── {platform}/
│       └── {problem_slug}/
│           ├── problem.yaml
│           ├── README.md
│           ├── statement.md
│           ├── workspace/
│           │   ├── main.cpp
│           │   ├── notes.md
│           │   └── scratch/
│           ├── attempts/
│           │   └── {attempt_id}/
│           │       ├── attempt.yaml
│           │       ├── solution.cpp
│           │       ├── notes.md
│           │       └── run.log
│           ├── references/
│           │   ├── references.yaml
│           │   ├── editorial.md
│           │   └── ranker.md
│           └── review/
│               ├── review.yaml
│               └── review.md
├── sessions/
│   └── {yyyy-mm-dd}.yaml
├── skills/
│   ├── problem-intake/
│   │   └── SKILL.md
│   ├── attempt-tracker/
│   │   └── SKILL.md
│   ├── evidence-review/
│   │   └── SKILL.md
│   └── daily-manager/
│       └── SKILL.md
├── scripts/
│   ├── init_problem.py
│   ├── lookup_atcoder_difficulty.py
│   ├── start_attempt.py
│   ├── build_review.py
│   └── update_session.py
└── templates/
    ├── problem.README.md
    ├── problem.yaml
    ├── attempt.yaml
    ├── review.yaml
    └── session.yaml
```

## 7. 문제 디렉토리 구조와 파일 역할
문제 단위의 표준 구조와 각 파일 역할은 다음과 같다.

### 7.1 `problem.yaml`
문제의 단일 진실 원천(single source of truth)이다.
문제 메타데이터, 현재 상태, 대표 시도, 참조 상태를 담는다.

### 7.2 `README.md`
문제 페이지의 운영 인덱스다.
현재 상태, 마지막 시도, 다음 액션, 관련 파일 링크를 사람이 빠르게 볼 수 있게 정리한다.

### 7.3 `statement.md`
문제 원문을 전부 복제하는 용도보다는 문제 요약, 입출력 핵심, 제약, 주의점을 적는 로컬 정리본으로 쓴다.
저작권 이슈가 있거나 원문 복제가 불필요한 플랫폼에서는 링크 + 요약만 저장한다.

### 7.4 `workspace/main.cpp`
문제를 풀 때 현재 작업 중인 메인 코드 파일이다.
풀이 도중에는 이 파일을 적극 수정한다.
정리된 시점의 스냅샷은 `attempts/{attempt_id}/solution.cpp`로 보존한다.

### 7.5 `workspace/notes.md`
아이디어 메모, 반례, 막힌 지점, 시간 복잡도 추정을 자유롭게 남긴다.
단, 복기 문서의 최종 근거는 이 메모를 재가공해서 `review/`에 넣는다.

### 7.6 `attempts/{attempt_id}/attempt.yaml`
각 시도의 상태를 남긴다.
예: 시도 시작/종료 시각, 결과, 사용 언어, 제출 여부, 핵심 접근.

### 7.7 `attempts/{attempt_id}/solution.cpp`
해당 시점의 풀이 스냅샷이다.
실패한 시도라도 보존해 나중에 사고 과정을 비교할 수 있게 한다.

### 7.8 `attempts/{attempt_id}/notes.md`
그 시도에서만 유효한 판단과 반례를 남긴다.
workspace 메모와 분리해 시점별 컨텍스트를 보존한다.

### 7.9 `attempts/{attempt_id}/run.log`
로컬 실행 결과를 저장한다.
최소 버전에서는 수동 리다이렉션도 허용하되, 이후 script가 자동 생성할 수 있어야 한다.

### 7.10 `references/references.yaml`
editorial과 ranker 참조의 메타데이터를 담는다.
링크, 읽은 시점, 핵심 키워드, 신뢰도 메모를 저장한다.

### 7.11 `references/editorial.md`, `references/ranker.md`
원문 전체 복제보다 핵심 구조를 정리한 로컬 노트다.
복기에서 인용할 수 있는 비교 포인트를 뽑아 둔다.

### 7.12 `review/review.yaml`
복기의 구조화 데이터다.
실수 유형, 핵심 차이, 후속 액션, 재풀이 예정일 등을 기계적으로 읽을 수 있어야 한다.

### 7.13 `review/review.md`
최종 복기 문서다.
반드시 `내 풀이 vs editorial vs ranker` 비교 섹션이 있어야 한다.

## 8. YAML 스키마 계약
초기 버전에서 반드시 고정할 스키마는 4개다.

1. `problem.yaml`
2. `attempt.yaml`
3. `review.yaml`
4. `sessions/{date}.yaml`

### 8.0 공통 값 규약
스키마를 쓰는 모든 skill과 script는 아래 규약을 따른다.

- `problem_slug`: `{platform}-{problem_id}`를 기본값으로 사용한다. 예: `boj-1234`, `cf-2050b`
- `attempt_id`: `YYYYMMDD-HHMM` 로컬 시간 형식을 사용한다. 예: `20260307-0900`
- `status.state` 허용값: `not_started`, `in_progress`, `solved`, `review_pending`, `reviewed`, `archived`
- `attempt.status` 허용값: `in_progress`, `accepted`, `wrong_answer`, `time_limit`, `memory_limit`, `runtime_error`, `compile_error`, `abandoned`
- `references.*.status` 허용값: `pending`, `collected`, `reviewed`
- `review.outcome` 허용값: `pending`, `solved_after_review`, `needs_retry`, `concept_gap`, `implementation_gap`
- 모든 시간 필드는 ISO 8601 with timezone 형식을 사용한다. 예: `2026-03-07T09:00:00+09:00`

### 8.1 `problem.yaml` 예시
```yaml
schema_version: 1
problem:
  platform: boj
  contest_id: null
  problem_id: "1234"
  slug: boj-1234
  title: Example Problem
  url: https://example.com/problems/1234
  tags: [graph, shortest-path]
  difficulty:
    source: solvedac
    value: gold4
status:
  state: in_progress
  first_started_at: 2026-03-07T09:00:00+09:00
  last_touched_at: 2026-03-07T10:20:00+09:00
  solved_at: null
  current_attempt_id: 20260307-0900
  canonical_solution_path: attempts/20260307-0900/solution.cpp
workflow:
  language: cpp17
  workspace_entry: workspace/main.cpp
  review_required: true
references:
  editorial:
    status: pending
    path: references/editorial.md
  ranker:
    status: pending
    path: references/ranker.md
review:
  status: pending
  path: review/review.md
```

### 8.2 `attempt.yaml` 예시
```yaml
schema_version: 1
attempt:
  attempt_id: 20260307-0900
  started_at: 2026-03-07T09:00:00+09:00
  ended_at: 2026-03-07T10:20:00+09:00
  actor: user
  language: cpp17
  status: wrong_answer
  submitted: false
  source_path: workspace/main.cpp
artifacts:
  snapshot_path: attempts/20260307-0900/solution.cpp
  notes_path: attempts/20260307-0900/notes.md
  run_log_path: attempts/20260307-0900/run.log
analysis:
  intended_strategy: dijkstra with state compression
  blockers:
    - edge case for duplicated states
    - memory growth not controlled
  self_assessment:
    confidence: medium
    bug_type: implementation
```

### 8.3 `review.yaml` 예시
```yaml
schema_version: 1
review:
  generated_at: 2026-03-07T11:00:00+09:00
  based_on_attempt_id: 20260307-0900
  outcome: solved_after_review
  confidence: high
comparison:
  my_solution:
    summary: Used Dijkstra with an extra dimension but mishandled state pruning.
    strengths:
      - Correct high-level direction
    weaknesses:
      - Missing dominance check
  editorial:
    summary: Formalized state pruning invariant before coding.
    key_points:
      - Dominance relation is the core invariant
      - Complexity bound depends on bounded relaxations
  ranker:
    summary: Same algorithmic class, cleaner state encoding and less branching.
    key_points:
      - Flattened state representation
      - Earlier pruning in transition loop
insights:
  mistakes:
    - I moved to implementation before invariant was written down.
    - I did not test a duplicated-state counterexample early.
  reusable_rules:
    - For stateful shortest path, write the dominance rule before coding.
    - Prepare one adversarial test for each extra state dimension.
follow_up:
  needs_re_solve: true
  revisit_on: 2026-03-10
  tags: [state-graph, review-needed]
```

### 8.4 `sessions/{date}.yaml` 예시
```yaml
schema_version: 1
session:
  date: 2026-03-07
  focus: graph + implementation discipline
  queue:
    planned:
      - boj-1234
      - cf-2050b
    active:
      - boj-1234
    review:
      - atc-abc100-d
log:
  completed:
    - problem: boj-1234
      attempt_id: 20260307-0900
      result: wrong_answer
  review_completed:
    - boj-0987
next_actions:
  - Finish grounded review for boj-1234
  - Re-solve atc-abc100-d without editorial
```

## 9. Skill 최소 세트
초기 버전은 반드시 4개 skill로 시작한다.
각 skill은 책임 범위를 넘지 않아야 한다.

### 9.1 `problem-intake`
역할: 새 문제 워크스페이스 생성

입력:
- 플랫폼
- 문제 ID 또는 slug
- 제목 또는 URL

출력:
- `problems/{platform}/{problem_slug}/` 생성
- `problem.yaml`, `README.md`, `workspace/main.cpp`, `workspace/notes.md` 초기화
- 오늘 세션 파일에 해당 문제 등록 가능

금지:
- 문제 풀이 전략 제안
- editorial/ranker 비교 수행

### 9.2 `attempt-tracker`
역할: 시도 시작/종료 및 스냅샷 기록

입력:
- 대상 문제 경로
- 언어
- 시도 종료 상태

출력:
- 새 `attempt_id` 생성
- `attempt.yaml`, `solution.cpp`, `notes.md`, `run.log` 스냅샷 저장
- `problem.yaml`의 현재 상태 업데이트

금지:
- 근거 없는 회고 생성
- editorial 요약 생성

### 9.3 `evidence-review`
역할: `내 풀이 / editorial / ranker` 비교 기반 복기 생성

입력:
- 문제 경로
- 대상 attempt
- references 메모

출력:
- `review/review.yaml`
- `review/review.md`
- 비교 포인트, 실수 유형, 재발 방지 규칙

강제 규칙:
- 복기는 반드시 저장된 파일을 근거로 한다.
- 근거가 없으면 `unknown` 또는 `missing evidence`로 남긴다.
- 힌트 생성기가 아니라 사후 정리 엔진으로 동작한다.

### 9.4 `daily-manager`
역할: 일일 큐 관리와 세션 업데이트

입력:
- 날짜
- 문제 상태들
- 복습 필요 여부

출력:
- `sessions/{date}.yaml` 생성 또는 갱신
- 오늘의 planned/active/review 목록 정리
- 세션 종료 시 next actions 갱신

금지:
- 임의의 우선순위 조작
- 문제 풀이 자체 대행

## 10. Script 최소 버전 요구사항
초기 scripts는 최소 기능만 제공해도 된다. 다만 YAML 계약을 깨면 안 된다.

### 10.1 `scripts/init_problem.py`
기능:
- 인자로 플랫폼, 문제 ID/slug, 제목을 받아 문제 디렉토리 생성
- 템플릿 파일 복사
- `problem.yaml` 기본값 채우기
- AtCoder 문제면 로컬 difficulty dataset을 조회해 difficulty를 채운다.

예상 호출:
```bash
python scripts/init_problem.py --platform boj --id 1234 --title "Example Problem"
```

### 10.2 `scripts/start_attempt.py`
기능:
- 현재 `workspace/main.cpp`를 새 attempt 스냅샷으로 복사
- `attempt.yaml` 생성
- 필요 시 종료 상태를 반영해 `problem.yaml` 갱신

예상 호출:
```bash
python scripts/start_attempt.py --problem problems/boj/boj-1234 --status wrong_answer
```

### 10.3 `scripts/build_review.py`
기능:
- 문제 디렉토리의 attempt, references, notes를 읽어 review 초안 생성
- 최소 버전에서는 템플릿 채우기 수준이어도 괜찮다.
- 근거가 비어 있으면 비어 있는 채로 표시해야 한다.

예상 호출:
```bash
python scripts/build_review.py --problem problems/boj/boj-1234 --attempt 20260307-0900
```

### 10.4 `scripts/update_session.py`
기능:
- 날짜별 세션 파일 생성/갱신
- 문제 상태를 planned/active/review/completed에 반영

예상 호출:
```bash
python scripts/update_session.py --date 2026-03-07 --add-active boj-1234
```

## 11. 복기 문서 형식 요구사항
`review/review.md`는 최소한 다음 섹션을 포함해야 한다.

1. Problem Summary
2. Attempt Snapshot
3. My Solution
4. Editorial
5. Ranker
6. Comparison
7. Mistakes
8. Reusable Rules
9. Next Action

각 섹션은 빈 문단으로 남겨도 되지만, 섹션 자체는 유지한다.
이는 후속 script와 skill이 같은 뼈대를 공유하기 위함이다.

## 12. Daily Workflow 요구사항
별도 문서 `docs/daily-workflow.md`에서 상세화하되, 최소 흐름은 아래와 같다.

1. 오늘 세션 파일 생성 또는 열기
2. 새 문제 intake 또는 기존 문제 재개
3. repo 안에서 직접 풀이
4. attempt 스냅샷 저장
5. 필요 시 references 정리
6. evidence review 생성
7. 세션 종료 시 다음 액션 정리

## 13. 구현 순서와 완료 기준

### 13.1 1단계: 디렉토리 구조 생성
완료 기준:
- 루트 구조와 템플릿 디렉토리가 생성된다.
- 예시 문제 하나를 넣을 수 있는 수준의 빈 구조가 있다.

### 13.2 2단계: YAML 스키마 확정
완료 기준:
- `problem.yaml`, `attempt.yaml`, `review.yaml`, `session.yaml` 템플릿이 생성된다.
- 필수 필드와 nullable 필드가 구분된다.

### 13.3 3단계: skill 4개 초안 작성
완료 기준:
- `skills/problem-intake/SKILL.md`
- `skills/attempt-tracker/SKILL.md`
- `skills/evidence-review/SKILL.md`
- `skills/daily-manager/SKILL.md`
- 각 skill은 입력, 출력, 금지사항, 작업 절차를 가진다.

### 13.4 4단계: scripts 최소 버전 작성
완료 기준:
- 스크립트 4개가 템플릿 생성/갱신 수준으로 동작한다.
- 스키마와 파일 경로 계약을 어기지 않는다.

### 13.5 5단계: daily workflow 문서화
완료 기준:
- 하루 시작부터 종료까지 실제 사용 예시가 문서에 들어간다.
- 어떤 skill/script를 언제 호출하는지 명시된다.

## 14. Codex 실행 지침
이 문서를 기준으로 다음 작업을 수행할 때 Codex는 다음 우선순위를 따른다.

1. 먼저 디렉토리와 템플릿을 만든다.
2. YAML 계약을 코드보다 먼저 고정한다.
3. skill은 스키마를 읽고 쓰는 문서로 작성한다.
4. script는 최소 기능만 구현하되, 향후 확장 가능한 CLI 형태로 작성한다.
5. AI 출력은 항상 repo 안의 저장 근거를 우선 참조한다.

## 15. 의사결정 메모
초기 버전에서 고정한 결정은 다음과 같다.

- 문제 풀이 코드는 `workspace/`에서 작성하고, 시도 스냅샷은 `attempts/`로 보존한다.
- 복기의 기준 비교축은 `내 풀이 / editorial / ranker` 세 개다.
- 최소 skill 세트는 `problem-intake`, `attempt-tracker`, `evidence-review`, `daily-manager`다.
- 세션 관리 단위는 날짜별 YAML 파일이다.
- AI는 기본적으로 힌트 제공자가 아니라 사후 분석 및 구조화 엔진이다.

이 결정들은 특별한 이유가 없으면 다음 단계 구현에서 변경하지 않는다.
