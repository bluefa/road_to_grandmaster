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

## 기존 문제 처리 (멱등성)

`problems/{platform}/{slug}/`가 이미 존재할 때의 동작.

### 원칙

**유저가 손댄 파일은 절대 건드리지 않는다.** 인테이크 재실행은 "빈 구석 채우기"만 허용.

### 파일별 정책

| 파일/디렉터리 | 기본 동작 | 플래그로 강제 덮어쓰기 |
|---------------|-----------|------------------------|
| `workspace/main.cpp` | **절대 덮어쓰기 금지**. 존재하면 skip | 없음 (수동 삭제 요구) |
| `workspace/notes.md` | 존재하면 skip | 없음 |
| `attempts/**` | 존재하면 skip | 없음 |
| `review/**` | 존재하면 skip | 없음 |
| `references/editorial.md`, `ranker.md` | 파일이 **비어있지 않으면** skip | `--force-references` |
| `references/references.yaml` | 위와 동일 | `--force-references` |
| `statement.md` | 파일이 **비어있지 않으면** skip | `--force-statement` |
| `README.md` | 매번 재생성 OK (상태 표시 파일이라 휘발성) | — |
| `workspace/testcases/sample_*.txt` | 존재하면 skip, 없는 번호만 추가 | `--refresh-testcases` (전체 덮어쓰기) |
| `problem.yaml` | **머지**: 기존 값 유지, 누락 필드만 보충 | `--refresh-metadata` (난이도·제한만 최신화) |

### "비어있다"의 정의

- 파일이 없거나 크기 0
- 공백/줄바꿈만 있음
- 템플릿 그대로(치환되지 않은 플레이스홀더 포함) — 이 판정은 템플릿과 hash 비교로 확인

### `problem.yaml` 머지 규칙

기존 값이 `null`, 빈 문자열, 빈 리스트인 필드만 새 값으로 채움. 유저가 수동 편집한 값은 유지.
`--refresh-metadata` 지정 시엔 예외적으로 `difficulty`, `time_limit_ms`, `memory_limit_mb`만 최신 값으로 덮어씀 (나머지는 머지 규칙 그대로).

### 동작 요약

```bash
# 이미 존재하는 문제 URL로 다시 실행
./scripts/init_problem.py https://codeforces.com/contest/1168/problem/C

# 출력 예시
[init] existing problem detected: problems/cf/cf-1168_c/
[init] main.cpp         skip (user file)
[init] notes.md         skip (user file)
[init] testcases/       2 existing, 0 added
[init] problem.yaml     merged (difficulty was null → 2100)
[init] statement.md     skip (non-empty)
[init] references/      skip (non-empty)
done. no destructive changes.
```

### 플래그

- `--refresh-testcases` : 샘플 테스트케이스 전체 재다운로드 (공식 샘플이 수정된 경우 등)
- `--refresh-metadata`  : `problem.yaml`의 난이도·제한만 최신화
- `--force-references`  : `references/*`만 템플릿으로 리셋
- `--force-statement`   : `statement.md`만 템플릿으로 리셋
- 그 외 파일은 **플래그 없음** — 정말 리셋하려면 유저가 손으로 지우고 재실행

---

## 검증 계획

구현 후 "진짜 제대로 동작하나"를 확인하는 체크리스트. 자동화된 테스트 스크립트 없이도 수동으로 따라할 수 있게 구성.

### A. 단위 수준 확인 (스크립트별)

**A1. `refresh_codeforces_problems.py`**
- [ ] 실행 후 `data/codeforces/problemset.json` 생성됨
- [ ] JSON 파싱 성공, `problems` 배열 길이 > 9000
- [ ] 샘플 문제 하나 골라서 `rating`/`tags` 존재 확인
- [ ] 두 번째 실행 시 파일 mtime 갱신 확인

**A2. `lookup_codeforces_difficulty.py`**
- [ ] 캐시 없는 상태에서 호출 → 자동 refresh 후 결과 반환
- [ ] 캐시 fresh 상태(< 24h)에서 호출 → 네트워크 호출 없이 즉시 반환 (strace 또는 시간 비교)
- [ ] 캐시 stale (`touch -d '2 days ago'`)에서 호출 → refresh 트리거
- [ ] 알려진 문제: `1168 C` → rating 있음, tags 비어있지 않음
- [ ] 존재하지 않는 문제: `99999 Z` → `{"rating": null, ...}` 반환, exit 0
- [ ] 최신 rating 없는 문제 (방금 끝난 콘테스트): `rating: null` 정상 반환

**A3. `lookup_atcoder_difficulty.py` (기존 동작 회귀)**
- [ ] 기존 AtCoder 문제에서 여전히 정상 동작

### B. `init_problem.py` — Happy Path

각각 **빈 임시 디렉터리**(또는 `--dry-run` 후 실제)에서 실행.

**B1. AtCoder 신규 문제**
- [ ] `./scripts/init_problem.py https://atcoder.jp/contests/abc300/tasks/abc300_a`
- [ ] `problems/atc/atc-abc300_a/` 생성됨
- [ ] `problem.yaml`의 `difficulty`, `time_limit_ms`, `memory_limit_mb` 채워짐
- [ ] `workspace/testcases/sample_input_1.txt` 등 최소 1쌍 존재
- [ ] `workspace/main.cpp` 빈 템플릿 존재
- [ ] `./scripts/run_tests.sh problems/atc/atc-abc300_a` 호출 시 빌드 실패는 나도 **샘플은 인식됨**

**B2. Codeforces 신규 문제**
- [ ] `./scripts/init_problem.py https://codeforces.com/contest/1168/problem/C`
- [ ] `problems/cf/cf-1168_c/` 생성됨
- [ ] `problem.yaml`의 `difficulty.value = 2100`, `tags` 존재
- [ ] 샘플 케이스 존재
- [ ] 전체 소요 시간 < 10초

**B3. 기존 수동 문제와 구조 비교**
- [ ] 새로 생성한 `atc-abc300_a`와 기존 `atc-abc436_g`의 디렉터리 트리 diff → 파일 목록 동일
- [ ] `problem.yaml` 필드 키 집합 동일

### C. `init_problem.py` — 멱등성

**C1. 두 번째 실행 (no-op)**
- [ ] B2 직후 같은 URL로 다시 실행
- [ ] `main.cpp` mtime 변화 없음
- [ ] 출력에 `skip (user file)` 표시됨
- [ ] exit 0

**C2. 유저 편집 보호**
- [ ] `main.cpp`에 코드 작성 → 재실행 → 코드 그대로 남아있음
- [ ] `notes.md`에 메모 추가 → 재실행 → 메모 보존
- [ ] `references/editorial.md`에 내용 추가 → 재실행 (플래그 없음) → 내용 보존

**C3. 메타데이터 머지**
- [ ] `problem.yaml`에 `difficulty: null`인 기존 문제 → `--refresh-metadata` 실행 → 난이도만 채워지고 유저가 편집한 다른 필드는 그대로
- [ ] 플래그 없이 실행 → null 필드 보충되지만, 이미 값 있던 필드는 유지

**C4. 테스트케이스 부분 추가**
- [ ] `sample_input_1.txt`, `sample_output_1.txt`만 남기고 2번 삭제 → 재실행 → 2번만 추가됨, 1번 파일 mtime 유지
- [ ] `--refresh-testcases` → 전부 덮어쓰기됨

### D. 에러 / 엣지 케이스

- [ ] 네트워크 차단 상태에서 새 문제 → 샘플 다운로드 실패 메시지, 디렉터리는 생성되지 않거나 명확히 "partial" 표시
- [ ] 존재하지 않는 CF 문제 URL (`contest/99999/problem/Z`) → 명확한 에러, 디렉터리 생성 안 됨
- [ ] AtCoder 진행 중 콘테스트 URL (로그인 필요) → 에러 메시지에서 원인(로그인) 안내
- [ ] 잘못된 URL 포맷 → URL 파싱 단계에서 exit, 네트워크 호출 없음
- [ ] rating이 아직 부여되지 않은 최신 CF 문제 → `difficulty: null`로 디렉터리 생성됨, 에러 아님
- [ ] oj-api 미설치 → 명확한 설치 안내 메시지

### E. 통합 (E2E)

- [ ] `problem-intake` SKILL을 호출해서 새 문제 생성 → 위 B1/B2와 동일한 결과
- [ ] 생성된 문제에서 `test-runner` SKILL 호출 → 샘플이 바로 돌아감
- [ ] 세션 플래그 사용 → `sessions/{today}.yaml`에 slug 정확히 등록

### F. 회귀 (기존 자산 보호)

- [ ] 기존 문제 `problems/atc/atc-abc436_g/`, `problems/cf/cf-1168_c/` 파일들 모두 그대로
- [ ] `data/atcoder/problem-models.json` 수정되지 않음
- [ ] `templates/**` 내용 변화 없음

검증 통과 조건: A·B·C 전부 통과 + D/E/F에서 알려진 실패 없음.

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
