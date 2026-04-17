# Plan: 문제 인테이크 자동화 (AtCoder / Codeforces)

## 목표

URL 한 줄만 넘기면 문제 디렉터리·메타데이터·샘플 테스트케이스가 전부 자동 생성되게 한다.
대상 플랫폼은 **AtCoder, Codeforces** 두 개로 한정.

```bash
./scripts/init_problem.py https://atcoder.jp/contests/abc436/tasks/abc436_g
./scripts/init_problem.py https://codeforces.com/contest/1168/problem/C
```

실행 후 즉시 `workspace/main.cpp`에서 코딩 시작할 수 있는 상태가 되어야 한다.

---

## 전체 아키텍처

```
사용자 URL 입력
      │
      ▼
┌─────────────────────────────────────────┐
│  init_problem.py                        │
│   ├─ URL → (platform, contest, index)   │
│   ├─ oj-api get-problem <url>           │  ← 샘플 + 시간/메모리 제한
│   ├─ 난이도 조회 (플랫폼별)              │
│   └─ 디렉터리 + 파일 materialize         │
└─────────────────────────────────────────┘
      │
      ▼
problems/{platform}/{slug}/
   problem.yaml, statement.md, README.md,
   workspace/main.cpp, workspace/testcases/*,
   references/, review/, attempts/
```

핵심 원칙:

- **파싱이 아니라 매핑**: oj-api가 뱉는 JSON(Competitive Companion과 동일 스키마)을 그대로 우리 템플릿에 꽂는다.
- **스크립트는 결정성 있게**: SKILL은 "호출 + 사용자 확인"만. 분기 로직은 전부 스크립트에.
- **난이도 캐시는 로컬 데이터셋**: 네트워크 실패에도 의존하지 않음. 주기적 갱신.

---

## 구성 요소

### 1. 난이도 데이터 캐시

AtCoder는 이미 있음. Codeforces만 새로 추가.

| 파일 | 역할 | 갱신 주기 |
|------|------|-----------|
| `data/atcoder/problem-models.json` | (기존) AtCoder Problems API 미러 | 수동 또는 드물게 |
| `data/codeforces/problemset.json` | **신규** CF `problemset.problems` API 미러 | **lazy**: 난이도 조회 시 파일 mtime이 24h 초과면 자동 갱신 |

### 2. 스크립트

| 스크립트 | 입력 | 출력 | 비고 |
|----------|------|------|------|
| `scripts/refresh_codeforces_problems.py` | — | `data/codeforces/problemset.json` | **신규**. CF API 한 번 호출해서 저장. 단독 실행도 가능 |
| `scripts/lookup_codeforces_difficulty.py` | `contestId`, `index` | `rating`, `tags` JSON | **신규**. 캐시 조회. 파일 mtime > 24h면 `refresh_codeforces_problems.py` 자동 호출 후 조회 |
| `scripts/lookup_atcoder_difficulty.py` | `problem_id` | `difficulty` | (기존) 유지 |
| `scripts/init_problem.py` | URL | 문제 디렉터리 전체 | **신규**. 메인 엔트리포인트 |

### 3. `init_problem.py` 내부 흐름

```
1. URL 파싱 → (platform, contest_id, problem_index, slug)
   - atcoder.jp/contests/<c>/tasks/<task_id>   → platform=atc, slug=atc-<task_id>
   - codeforces.com/contest/<n>/problem/<i>    → platform=cf,  slug=cf-<n>_<i_lower>

2. oj-api get-problem <url>  (subprocess)
   → JSON: name, timeLimit, memoryLimit, tests[], url

3. 난이도/태그 조회
   - AtCoder: lookup_atcoder_difficulty.py
   - CF:      lookup_codeforces_difficulty.py

4. 캐노니컬 루트(/Users/study/road_to_grandmaster) 기준으로 디렉터리 생성
   problems/{platform}/{slug}/
     ├─ problem.yaml         ← 템플릿에서 렌더
     ├─ statement.md         ← 빈 요약 스켈레톤
     ├─ README.md            ← 상태/엔트리포인트
     ├─ workspace/
     │   ├─ main.cpp         ← 빈 템플릿
     │   ├─ notes.md
     │   └─ testcases/
     │       ├─ sample_input_1.txt / sample_output_1.txt
     │       └─ ...
     ├─ references/
     │   ├─ editorial.md     ← 빈
     │   ├─ ranker.md        ← 빈
     │   └─ references.yaml  ← 빈
     ├─ attempts/            ← 빈 디렉터리
     └─ review/              ← 빈 디렉터리

5. 세션 등록 (옵션, --session 플래그 시에만)
   sessions/{yyyy-mm-dd}.yaml에 slug 추가

6. 사람이 읽기 좋은 요약 stdout 출력
   - 생성된 경로, rating/difficulty, 샘플 개수, time/memory limit
```

### 4. `problem-intake` SKILL.md 재작성

현재 SKILL은 LLM이 단계별로 디렉터리를 만들게 되어 있음. 이걸 **스크립트 래퍼로 슬림화**.

SKILL 역할 재정의:

- URL 받기 (사용자에게 부족한 정보 있으면 질문)
- `init_problem.py <url>` 호출
- 실패 시 에러 메시지 읽고 사용자에게 설명
- 성공 시 생성된 경로 안내
- 세션 등록 요청 여부 확인

SKILL에서 제거:

- 디렉터리 수동 생성 단계
- YAML 필드 수동 채우기
- 난이도 수동 조회

---

## 디렉터리 변경 요약

**신규**
```
data/codeforces/problemset.json
scripts/init_problem.py
scripts/refresh_codeforces_problems.py
scripts/lookup_codeforces_difficulty.py
```

**수정**
```
skills/problem-intake/SKILL.md      ← 스크립트 호출 래퍼로 축소
.gitignore                          ← data/codeforces/*.json 캐시 정책 결정
```

**영향 없음**
```
problems/**                         ← 기존 문제는 건드리지 않음
templates/**                        ← 그대로 재사용
data/atcoder/problem-models.json    ← 그대로
```

---

## 구현 단계

작은 단위로 쪼개서 점진적으로.

| 단계 | 작업 | 검증 |
|------|------|------|
| 1 | `refresh_codeforces_problems.py` 작성 → 캐시 JSON 생성 | 파일 크기/문제 개수 확인 |
| 2 | `lookup_codeforces_difficulty.py` 작성 | 알려진 문제(예: 1168C)로 rating/tags 확인 |
| 3 | `init_problem.py` 스켈레톤 (URL 파싱 + slug 계산까지) | `--dry-run`으로 slug만 출력 |
| 4 | oj-api 통합 → 샘플 테스트케이스 저장 | AtCoder/CF 각 1문제로 실행 |
| 5 | 난이도/메타데이터 → `problem.yaml` 렌더링 | 기존 문제와 필드 동등성 확인 |
| 6 | 나머지 파일(`main.cpp`, `statement.md`, …) materialize | run_tests.sh가 바로 돌아가는지 확인 |
| 7 | `SKILL.md` 재작성 (스크립트 래퍼화) | 새 문제 인테이크 E2E 테스트 |
| 8 | (옵션) 세션 등록 플래그 | `--session` 동작 확인 |

각 단계는 독립적으로 커밋 가능.

---

## 스코프 밖 (이번엔 안 함)

- BOJ, 기타 OJ 지원 — AtCoder/CF 두 개만
- 브라우저 확장(Competitive Companion) 리스너 — 서버 사이드 파서로 충분
- 문제 statement 전문(本文) 다운로드 — `statement.md`는 로컬 요약용
- 콘테스트 단위 일괄 인테이크 — 단일 문제 URL만
- 에디토리얼/랭커 자동 수집 — `reference-collector` 별도 스킬
- CF Gym, AtCoder Heuristic 등 특수 콘테스트

---

## 의존성

- Python 3.10+
- `oj-api` (`pip install online-judge-tools` 또는 `pip install online-judge-api-client`)
- 표준 라이브러리만 (urllib, json, pathlib, subprocess)
- PyYAML (이미 쓰고 있다면 유지, 아니면 단순 문자열 포맷으로 대체 가능)

---

## 성공 기준

1. `init_problem.py <url>` 한 줄로 디렉터리 완성까지 **10초 이내**
2. 생성 직후 `./scripts/run_tests.sh problems/.../slug` 호출 시 샘플이 바로 실행됨
3. AtCoder/CF 각각 최소 3문제로 회귀 테스트 통과
4. 기존 수동 생성 문제와 파일 구조 완전 동일
